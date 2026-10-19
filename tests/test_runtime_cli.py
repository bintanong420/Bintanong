"""CLI validation must precede opening services or writing evidence."""
import json

import pytest

from backend.bintanong_runtime.cli import load_request, output_path


@pytest.mark.parametrize('value', [dict(question='hello',context={},integration={}),
    dict(question=' ',context=dict(session_id='sess-a',request_id='req-a')),
    dict(question='hello',context=dict(session_id='sess-a',request_id='req-a',facts=[
        dict(fact_id='fact-a',session_id='sess-b',program_id='p',curriculum_id='c',
            course_id='a',state='passed')]))])
def test_request_rejects_evidence_injection_invalid_text_and_foreign_facts(tmp_path,value):
    path=tmp_path/'request.json'; path.write_text(json.dumps(value))
    with pytest.raises(ValueError): load_request(path)


def test_request_preserves_natural_text_without_a_route_override(tmp_path):
    path=tmp_path/'request.json'
    path.write_text(json.dumps(dict(question='Where do I submit Form Q?',
        context=dict(session_id='sess-a',request_id='req-a'))))
    request=load_request(path)
    assert request.question=='Where do I submit Form Q?'
    assert request.context.request_id=='req-a'


def test_output_stays_in_explicit_evidence_root(tmp_path):
    root=tmp_path/'raw'
    with pytest.raises(ValueError): output_path(tmp_path/'outside.json',root)
    with pytest.raises(ValueError): output_path(root,root)
    assert output_path(root/'run.json',root)==root/'run.json'
