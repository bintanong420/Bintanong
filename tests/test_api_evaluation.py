"""Gated evaluation runs: synthetic chunks and answers; the student chat path stays as it was."""
import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from backend.bintanong_api.app import ApiServices, ApiSettings, create_app
from backend.bintanong_api.chat import CurriculumOption
from backend.bintanong_api.evaluation import EvaluationService, evaluation_from_env, route_label
from backend.bintanong_private_context.sessions import SessionStore
from backend.bintanong_retrieval.observation import record_emitted, record_search
from evaluation.system_metrics import load_roster, normalize_question
from test_api_presentation import answer_for
from test_routing_validation import validate

ORIGIN = 'https://bintanong.example'
TOKEN = 'synthetic-evaluator-passcode'
GOOD = {'origin': ORIGIN, 'x-bintanong-evaluator': TOKEN}
QUESTION = 'How to drop subjects?'
CURRICULA = tuple(CurriculumOption(program, curriculum, program.upper(), '2018-2019') for program, curriculum in sorted(
    {(row['program_id'], row['curriculum_id']) for row in load_roster() if row['program_id']}))
KEYS = dict(keys=[dict(key_id='row-11', case_ids=['B11-EN'], expected_route='RAG', expected_outcome='answer',
                       key_status='keyed', relevant_chunk_ids=['a'], expected_facts=['Registrar'],
                       source_note='synthetic')])


def item(chunk_id, similarity=.9):
    return dict(chunk=dict(chunk_id=chunk_id, source_text=f'Clause {chunk_id}', text='{}', source_label='Synthetic.pdf',
                           section_path=['Policy']),
                spans=[dict(page=7), dict(page=7), dict(page=8)], similarity=similarity,
                neighbors=[dict(chunk=dict(chunk_id='n'))])


class Pipeline:
    def __init__(self, searches=(), result='synthetic answer', routed=None, error=None):
        self.searches, self.result, self.routed, self.error, self.contexts = searches, result, routed, error, []

    async def run(self, text, context, *, routed_sink, progress):
        self.contexts.append(context)
        for query, subject, candidates, emitted in self.searches:
            record_search(query, subject, ('claim',), candidates)
            record_emitted([dict(chunk_id=identity) for identity in emitted])
        if self.routed is not None:
            routed_sink(self.routed)
        if self.error is not None:
            raise self.error
        return self.result


class Engine:
    def __init__(self, error=None):
        self.requests, self.error = [], error

    def search_all_chunks(self, request, top_k=None):
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return [item('a'), item('x', .8), item('y', .7)]


def releases(engine):
    resources = SimpleNamespace(retrieval=SimpleNamespace(engine=engine), document_scope=('audience:undergraduate',),
                                pin=SimpleNamespace(release_id='release-test',
                                                    documents=(SimpleNamespace(version_id='v1'),
                                                               SimpleNamespace(version_id='v1'))))

    class Provider:
        async def pin(self):
            return resources
    return Provider()


def service_for(tmp_path, pipeline, engine=None, keys=KEYS):
    return EvaluationService(pipeline=pipeline, releases=releases(engine or Engine()), curricula=CURRICULA,
                             course_labels={}, roster=load_roster(), normalize_question=normalize_question,
                             keys_document=keys, log_path=tmp_path / 'runs.jsonl', code_commit='abc1234', token=TOKEN)


def client_for(service, pipeline=None, **settings):
    return TestClient(create_app(ApiServices(sessions=SessionStore(), pipeline=pipeline, evaluation=service),
                                 ApiSettings(allowed_origins=(ORIGIN,), **settings)), base_url='https://testserver')


def post_run(client, question=QUESTION):
    return client.post('/evaluation/run', json=dict(question=question), headers=GOOD)


def test_off_by_default_is_404():
    client = client_for(None)
    assert client.get('/evaluation/cases', headers=GOOD).status_code == 404
    assert post_run(client).status_code == 404


@pytest.mark.parametrize('headers', [{}, {'x-bintanong-evaluator': 'wrong'}])
def test_wrong_or_missing_passcode_looks_like_no_route(tmp_path, headers):
    client = client_for(service_for(tmp_path, Pipeline()))
    assert client.get('/evaluation/cases', headers=headers).status_code == 404
    assert client.post('/evaluation/run', json=dict(question=QUESTION), headers={'origin': ORIGIN, **headers}).status_code == 404
    assert not (tmp_path / 'runs.jsonl').exists()


def test_cases_list_all_72_with_their_keys_and_no_status_yet(tmp_path):
    body = client_for(service_for(tmp_path, Pipeline())).get('/evaluation/cases', headers=GOOD).json()
    assert len(body['cases']) == 72 and body['code_commit'] == 'abc1234'
    by_id = {case['case_id']: case for case in body['cases']}
    assert by_id['B11-EN']['question'] == QUESTION and by_id['B11-EN']['key']['key_status'] == 'keyed'
    assert by_id['B11-TL']['key']['key_status'] == 'human_judged'


def test_run_returns_both_lists_answer_and_key(tmp_path):
    pipeline = Pipeline([('drop subjects', 'dropping', [item('a'), item('b', .6)], ['a'])])
    body = post_run(client_for(service_for(tmp_path, pipeline))).json()
    assert body['outcome'] == 'completed' and body['case_id'] == 'B11-EN' and body['release_id'] == 'release-test'
    assert body['code_commit'] == 'abc1234' and body['answer']['text'] == 'synthetic answer'
    assert body['key']['relevant_chunk_ids'] == ['a']
    search = body['searches'][0]
    assert search['query'] == 'drop subjects' and search['subject_id'] == 'dropping'
    assert [(r['rank'], r['chunk_id'], r['sent_to_writer']) for r in search['topic_bound']] == [(1, 'a', True), (2, 'b', False)]
    assert [(r['chunk_id'], r['sent_to_writer']) for r in search['all_chunks']] == [('a', True), ('x', False), ('y', False)]
    row = search['topic_bound'][0]
    assert row == dict(rank=1, chunk_id='a', similarity=.9, text='Clause a', source_label='Synthetic.pdf', pages=[7, 8],
                       section_path=['Policy'], sent_to_writer=True, attached_count=1)


def test_all_chunk_search_keeps_scope_and_versions_and_drops_only_the_topic(tmp_path):
    engine = Engine()
    post_run(client_for(service_for(tmp_path, Pipeline([('words', 'topic', [item('a')], [])]), engine)))
    request = engine.requests[0]
    assert (request.query, request.release_id) == ('words', 'release-test')
    assert request.scope == ('audience:undergraduate',) and request.document_version_ids == ('v1',)


def test_reply_without_a_topic_search_still_gets_the_all_chunk_list(tmp_path):
    body = post_run(client_for(service_for(tmp_path, Pipeline()))).json()
    assert len(body['searches']) == 1 and body['searches'][0]['topic_bound'] == []
    assert body['searches'][0]['query'] == QUESTION and len(body['searches'][0]['all_chunks']) == 3


def test_all_chunk_list_uses_the_routers_normalized_text_when_there_was_no_search(tmp_path):
    routed = validate()
    body = post_run(client_for(service_for(tmp_path, Pipeline(routed=routed)))).json()
    assert body['searches'][0]['query'] == routed.query.normalized_text and body['route_label'] == route_label(routed)


def test_route_label_names_a_route_or_a_control():
    assert route_label(SimpleNamespace(decision=SimpleNamespace(route='RAG', control=None))) == 'RAG'
    assert route_label(SimpleNamespace(decision=SimpleNamespace(route=None, control='clarify'))) == 'clarify'
    assert route_label(None) is None


def test_two_topics_give_two_searches(tmp_path):
    pipeline = Pipeline([('first', 'one', [item('a')], ['a']), ('second', 'two', [item('b')], ['b'])])
    body = post_run(client_for(service_for(tmp_path, pipeline))).json()
    assert [(s['query'], s['subject_id']) for s in body['searches']] == [('first', 'one'), ('second', 'two')]


def test_each_run_has_a_fresh_session(tmp_path):
    pipeline = Pipeline(routed=validate())
    client = client_for(service_for(tmp_path, pipeline))
    post_run(client)
    post_run(client)
    first, second = pipeline.contexts
    assert first.session_id != second.session_id
    assert second.conversation is None and second.facts == ()


def scope_of(context):
    return context.program_id, context.curriculum_id


def test_a_query_runs_with_its_rosters_curriculum(tmp_path):
    pipeline = Pipeline()
    body = post_run(client_for(service_for(tmp_path, pipeline))).json()
    assert scope_of(pipeline.contexts[0]) == ('palsu-bscs', 'bscs-2018-2019')
    assert (body['program_id'], body['curriculum_id']) == ('palsu-bscs', 'bscs-2018-2019')


def test_a_named_program_runs_with_that_programs_curriculum(tmp_path):
    pipeline = Pipeline()
    post_run(client_for(service_for(tmp_path, pipeline)), "I'm a BSIT student. Can I take CC 5/L if I haven't passed CC 3/L?")
    assert scope_of(pipeline.contexts[0]) == ('palsu-bsit', 'bsit-2018-2019')


def test_row_7_and_typed_text_run_with_no_curriculum(tmp_path):
    pipeline = Pipeline()
    client = client_for(service_for(tmp_path, pipeline))
    post_run(client, 'Can I take CC 5 if I failed CC 4?')
    post_run(client, 'Something outside the roster?')
    assert [scope_of(context) for context in pipeline.contexts] == [(None, None), (None, None)]


def test_a_curriculum_missing_from_the_release_is_refused_not_run_without_it(tmp_path):
    pipeline = Pipeline()
    service = EvaluationService(pipeline=pipeline, releases=releases(Engine()), curricula=(), course_labels={},
                                roster=load_roster(), normalize_question=normalize_question, keys_document=KEYS,
                                log_path=tmp_path / 'runs.jsonl', code_commit='abc1234', token=TOKEN)
    response = post_run(client_for(service))
    assert response.status_code == 409 and response.json()['error'] == 'case_curriculum_unavailable'
    assert pipeline.contexts == [] and not (tmp_path / 'runs.jsonl').exists()


def test_cases_name_the_curriculum_they_run_with(tmp_path):
    cases = client_for(service_for(tmp_path, Pipeline())).get('/evaluation/cases', headers=GOOD).json()['cases']
    by_id = {case['case_id']: case for case in cases}
    assert by_id['A02-EN']['curriculum_label'] == 'PALSU-BSIT 2018-2019' and by_id['A07-EN']['curriculum_label'] is None


def test_pipeline_failure_is_saved_as_infrastructure_error(tmp_path):
    response = post_run(client_for(service_for(tmp_path, Pipeline(error=RuntimeError('model down')))))
    assert response.status_code == 200
    body = response.json()
    assert body['outcome'] == 'infrastructure_error' and body['error'] == 'answer_unavailable' and body['searches'] == []
    assert 'model down' not in json.dumps(body)


def test_temporarily_unavailable_answer_is_not_scored_as_a_wrong_answer(tmp_path):
    unavailable = answer_for('RAG').model_copy(update=dict(status='temporarily_unavailable', reason=None))
    body = post_run(client_for(service_for(tmp_path, Pipeline(result=unavailable)))).json()
    assert body['outcome'] == 'infrastructure_error' and body['error'] == 'temporarily_unavailable'


def test_failed_all_chunk_search_is_not_shown_as_an_empty_result(tmp_path):
    body = post_run(client_for(service_for(tmp_path, Pipeline(), Engine(error=ValueError('storage'))))).json()
    assert body['outcome'] == 'infrastructure_error' and body['error'] == 'all_chunk_search_failed'


def test_real_answer_keeps_status_language_and_sources(tmp_path):
    answer = answer_for('RAG')
    body = post_run(client_for(service_for(tmp_path, Pipeline(result=answer)))).json()
    assert body['answer']['status'] == answer.status and body['answer']['language'] == answer.language
    assert len(body['answer']['sources']) == len(answer.citations)


def test_unmatched_text_is_kept_with_null_case(tmp_path):
    body = post_run(client_for(service_for(tmp_path, Pipeline())), 'How to drop subject?').json()
    assert body['case_id'] is None and body['outcome'] == 'completed' and body['key'] is None


def test_spacing_and_case_still_match_the_roster(tmp_path):
    assert post_run(client_for(service_for(tmp_path, Pipeline())), '  how to  DROP subjects? ').json()['case_id'] == 'B11-EN'


def test_invalid_question_is_refused(tmp_path):
    client = client_for(service_for(tmp_path, Pipeline()))
    assert post_run(client, '   ').status_code == 422
    assert not (tmp_path / 'runs.jsonl').exists()


def test_run_waits_its_turn_with_students(tmp_path):
    client = client_for(service_for(tmp_path, Pipeline()), max_running_answers=1, max_waiting_answers=0)
    held = client.app.state.admission.reserve(account_id='student')
    try:
        assert post_run(client).status_code == 503
    finally:
        held.release()
    assert post_run(client).status_code == 200
    assert client.app.state.admission.admitted == 0


def test_runs_do_not_use_the_student_question_limit(tmp_path):
    client = client_for(service_for(tmp_path, Pipeline()), max_questions_per_window=1)
    assert [post_run(client).status_code for _ in range(3)] == [200, 200, 200]
    assert client.app.state.question_limit.admit('account:someone') is None


def test_judgment_is_appended_and_survives_reload(tmp_path):
    client = client_for(service_for(tmp_path, Pipeline()))
    run_id = post_run(client).json()['run_id']
    saved = client.post(f'/evaluation/runs/{run_id}/judgment', headers=GOOD,
                        json=dict(chunk_marks=dict(a=True), answer_mark='partial', note='missing office'))
    assert saved.status_code == 200
    reopened = client_for(service_for(tmp_path, Pipeline()))
    runs = reopened.get('/evaluation/runs', headers=GOOD).json()['runs']
    assert runs[0]['run_id'] == run_id and runs[0]['key']['key_id'] == 'row-11'
    assert runs[0]['judgment']['answer_mark'] == 'partial' and runs[0]['judgment']['chunk_marks'] == dict(a=True)


def test_latest_judgment_is_the_one_shown(tmp_path):
    client = client_for(service_for(tmp_path, Pipeline()))
    run_id = post_run(client).json()['run_id']
    for mark in ('wrong', 'correct'):
        client.post(f'/evaluation/runs/{run_id}/judgment', headers=GOOD, json=dict(chunk_marks={}, answer_mark=mark, note=''))
    assert client.get('/evaluation/runs', headers=GOOD).json()['runs'][0]['judgment']['answer_mark'] == 'correct'


def test_log_lines_are_what_the_scorer_reads(tmp_path):
    from evaluation.system_metrics import build_report, read_records
    client = client_for(service_for(tmp_path, Pipeline([('q', 't', [item('a')], ['a'])])))
    run_id = post_run(client).json()['run_id']
    client.post(f'/evaluation/runs/{run_id}/judgment', headers=GOOD, json=dict(chunk_marks={}, answer_mark='correct', note=''))
    report = build_report(read_records(tmp_path / 'runs.jsonl'), KEYS)
    assert report['scored_cases'] == 1 and report['retrieval']['topic_bound']['overall']['hit_at_3'] == 1
    assert report['answer']['strict']['accuracy'] == 1


@pytest.mark.parametrize('run_id,body,status', [
    ('run-0000000000000000', dict(chunk_marks={}, answer_mark='correct', note=''), 404),
    (None, dict(chunk_marks={}, answer_mark='maybe', note=''), 422),
])
def test_unknown_run_or_invalid_mark_is_rejected(tmp_path, run_id, body, status):
    client = client_for(service_for(tmp_path, Pipeline()))
    run_id = run_id or post_run(client).json()['run_id']
    assert client.post(f'/evaluation/runs/{run_id}/judgment', headers=GOOD, json=body).status_code == status


def chat_parts(client):
    response = client.post('/chat', headers={'origin': ORIGIN}, json=dict(
        id='chat-1', trigger='submit-message',
        messages=[dict(id='m1', role='user', parts=[dict(type='text', text=QUESTION)])]))
    assert response.status_code == 200
    parts = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith('data: {')]
    return [(part['type'], part.get('delta')) for part in parts]


def test_student_chat_stream_is_unchanged(tmp_path):
    answer = answer_for('RAG')
    pipeline = Pipeline(result=answer)
    without = chat_parts(client_for(None, pipeline))
    assert chat_parts(client_for(service_for(tmp_path, pipeline), pipeline)) == without


def environment(tmp_path, **changes):
    keys = tmp_path / 'keys.json'
    keys.write_text(json.dumps(KEYS), encoding='utf-8')
    values = dict(BINTANONG_EVALUATION_TOKEN=TOKEN, BINTANONG_EVALUATION_LOG=str(tmp_path / 'log.jsonl'),
                  BINTANONG_EVALUATION_KEYS=str(keys), BINTANONG_EVALUATION_COMMIT='abc1234')
    values.update(changes)
    return {name: value for name, value in values.items() if value is not None}


def from_env(values):
    return evaluation_from_env(Pipeline(), releases(Engine()), CURRICULA, {}, environ=values)


def test_no_token_means_no_service():
    assert from_env({}) is None


def test_full_configuration_builds_a_service(tmp_path):
    assert isinstance(from_env(environment(tmp_path)), EvaluationService)


@pytest.mark.parametrize('missing', ['BINTANONG_EVALUATION_LOG', 'BINTANONG_EVALUATION_KEYS', 'BINTANONG_EVALUATION_COMMIT'])
def test_partial_configuration_refuses_startup(tmp_path, missing):
    with pytest.raises(ValueError, match='evaluation_configuration_incomplete'):
        from_env(environment(tmp_path, **{missing: None}))


def test_short_passcode_refuses_startup(tmp_path):
    with pytest.raises(ValueError, match='evaluation_token_too_short'):
        from_env(environment(tmp_path, BINTANONG_EVALUATION_TOKEN='short'))


def test_log_inside_git_checkout_refuses_startup(tmp_path):
    (tmp_path / '.git').write_text('gitdir: elsewhere', encoding='utf-8')
    (tmp_path / 'inner').mkdir()
    with pytest.raises(ValueError, match='evaluation_log_inside_git'):
        from_env(environment(tmp_path, BINTANONG_EVALUATION_LOG=str(tmp_path / 'inner' / 'log.jsonl')))


@pytest.mark.parametrize('case_ids,code', [(['Z99-EN'], 'evaluation_key_unknown_case'), (['B11-EN', 'B11-EN'], 'evaluation_key_duplicate_case')])
def test_bad_keys_refuse_startup(tmp_path, case_ids, code):
    bad = dict(keys=[dict(KEYS['keys'][0], case_ids=case_ids)])
    values = environment(tmp_path)
    (tmp_path / 'keys.json').write_text(json.dumps(bad), encoding='utf-8')
    with pytest.raises(ValueError, match=code):
        from_env(values)
