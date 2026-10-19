"""CLI validation must precede opening services or writing evidence."""
import json
import hashlib
from types import SimpleNamespace

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


@pytest.mark.parametrize('mutation',['edit','delete'])
def test_report_binds_the_input_snapshot_used_before_inference(tmp_path,monkeypatch,mutation):
    import backend.bintanong_runtime.cli as cli
    from test_runtime_composition import spec
    spec_path=tmp_path/'spec.json'
    request_path=tmp_path/'request.json'
    original_spec=json.dumps(spec()).encode()
    original_request=json.dumps(dict(question='Original question',
        context=dict(session_id='sess-a',request_id='req-a'))).encode()
    spec_path.write_bytes(original_spec); request_path.write_bytes(original_request)
    class App:
        closed=False
        async def run(self,question,context):
            assert question=='Original question'
            for path in (spec_path,request_path):
                if mutation=='edit': path.write_text('{"changed":true}')
                else: path.unlink()
            return SimpleNamespace(answer=SimpleNamespace(status='answered'),
                model_dump=lambda **kwargs:dict(answer=dict(status='answered')))
        def close(self): self.closed=True
    app=App()
    monkeypatch.setattr(cli,'build_application',lambda *args,**kwargs:app)
    output=tmp_path/'evidence/run.json'
    cli.main([str(spec_path),str(request_path),'--output',str(output),
        '--evidence-root',str(output.parent)])
    report=json.loads(output.read_text())
    assert report['spec_sha256']==hashlib.sha256(original_spec).hexdigest()
    assert report['request_sha256']==hashlib.sha256(original_request).hexdigest()
    assert app.closed
