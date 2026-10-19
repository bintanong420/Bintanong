"""Saved runtime artifacts stay bound to authoring truth and the tracked engine."""
import copy
import importlib
import json

import pytest

from test_symbolic_runtime import api, facts, fixture, request, rereview, run


def bundles():
    return importlib.import_module('backend.bintanong_symbolic.bundle')


def prepared(data=None):
    return bundles().prepare_runtime_bundle(run(fixture()) if data is None else data)


def test_bundle_is_deterministic_detached_and_inactive():
    ledger=run(fixture()); before=copy.deepcopy(ledger)
    bundle=prepared(ledger)
    assert bundle==prepared(ledger) and ledger==before
    assert bundle['schema_version']=='curriculum-runtime-bundle-v1'
    assert bundle['activation_allowed'] is bundle['runtime_ready'] is bundle['eligibility_executable'] is False
    assert bundle['approval_id'] is None and bundle['release_holds']
    assert bundle['ledger']['content_sha256']==ledger['content_sha256']
    assert bundle['payload']['curriculum_id']==ledger['scope']['curriculum_id']
    ledger['courses'][0]['facts']['course_code']['value']='mutated'
    assert bundle['ledger']==before
    assert bundles().validate_runtime_bundle(json.loads(json.dumps(bundle)))==bundle


def test_saved_synthetic_bundle_round_trip_executes_same_engine_and_results():
    ledger=run(fixture()); bundle=prepared(ledger)
    loaded=api().CurriculumRuntime.from_bundle(json.loads(json.dumps(bundle)))
    direct=api().CurriculumRuntime(ledger)
    assert loaded.check(request(),facts(passed=('course-1',)))==direct.check(request(),facts(passed=('course-1',)))
    assert loaded.list_affected_courses(request('course-1',predicate='list_affected_courses')).course_ids==('course-2',)


@pytest.mark.parametrize('field',['content_sha256','payload_sha256','engine_sha256','review_bundle_sha256',
                                 'runtime_version','coverage','release_holds','payload','activation_allowed'])
def test_forged_saved_artifact_rejected_before_worker(field,monkeypatch):
    bundle=prepared()
    if field=='coverage': bundle[field]=[]
    elif field=='release_holds': bundle[field]=[]
    elif field=='payload': bundle[field]['courses']=[]
    elif field=='activation_allowed': bundle[field]=True
    else: bundle[field]='forged'
    monkeypatch.setattr(api(),'_invoke_worker',lambda *a:pytest.fail('must not execute'))
    with pytest.raises(ValueError): api().CurriculumRuntime.from_bundle(bundle)


def test_engine_change_invalidates_saved_bundle(monkeypatch,tmp_path):
    bundle=prepared(); changed=tmp_path/'engine.pl'; changed.write_text('% changed engine\n')
    monkeypatch.setattr(bundles(),'_ENGINE',changed)
    with pytest.raises(ValueError): bundles().validate_runtime_bundle(bundle)


def test_engine_change_during_loading_cannot_replace_the_requested_artifact(monkeypatch,tmp_path):
    bundle=prepared(); original=api().validate_runtime_bundle
    changed=tmp_path/'engine.pl'; changed.write_text('% changed during load\n')
    def validate_then_change(value):
        checked=original(value)
        monkeypatch.setattr(bundles(),'_ENGINE',changed)
        return checked
    monkeypatch.setattr(api(),'validate_runtime_bundle',validate_then_change)
    with pytest.raises(ValueError): api().CurriculumRuntime.from_bundle(bundle)


def test_partial_projection_never_exports_unresolved_rule_as_executable():
    data=fixture(); c=data[2][1]
    c['prerequisites']={'kind':'unresolved','reason':'Fictional blank',
                        'source_spans':c['prerequisites']['source_spans']}
    bundle=prepared(rereview(data))
    assert bundle['payload']['courses'][1]['rule']=={'kind':'unresolved'}
    assert bundle['coverage'][1]['direct_rule']=='unresolved'
    result=api().CurriculumRuntime.from_bundle(bundle).check(request())
    assert result.decision.outcome=='unknown'


def test_real_source_artifact_can_be_prepared_but_cannot_execute(monkeypatch):
    data=fixture(); source=data[1][0].model_dump(mode='json'); source['synthetic']=False
    data=(data[0],[source],data[2],data[3]); bundle=prepared(run(data))
    assert bundle['ledger']['synthetic'] is bundle['payload']['synthetic'] is False
    assert bundle['runtime_ready'] is bundle['activation_allowed'] is False
    assert bundles().validate_runtime_bundle(bundle)==bundle
    monkeypatch.setattr(api(),'_invoke_worker',lambda *a:pytest.fail('must not execute'))
    with pytest.raises(ValueError,match='synthetic'): api().CurriculumRuntime.from_bundle(bundle)


def test_extra_keys_and_changed_ledger_do_not_load():
    bundle=prepared(); bundle['caller_approval']=True
    with pytest.raises(ValueError): bundles().validate_runtime_bundle(bundle)
    bundle=prepared(); bundle['ledger']['courses'][0]['facts']['course_code']['value']='SYN999'
    with pytest.raises(ValueError): bundles().validate_runtime_bundle(bundle)


def test_bundle_validation_is_bound_to_algorithm_folder_engine(monkeypatch):
    from pathlib import Path
    bundle=prepared()
    canonical=Path(__file__).resolve().parents[1]/'backend/algorithms/curriculum_runtime.pl'
    original=Path.read_bytes
    def changed_engine(path):
        data=original(path)
        return data+b'\n' if path.resolve()==canonical else data
    monkeypatch.setattr(Path,'read_bytes',changed_engine)
    with pytest.raises(ValueError,match='runtime bundle differs'):
        bundles().validate_runtime_bundle(bundle)


def test_windows_git_checkout_preserves_immutable_engine_bytes(tmp_path):
    import os
    import shutil
    import subprocess
    from pathlib import Path

    git = shutil.which('git')
    if git is None:
        pytest.skip('Git checkout verification requires Git')
    repo = Path(__file__).resolve().parents[1]
    relative = 'backend/algorithms/curriculum_runtime.pl'
    canonical = (repo / relative).read_bytes()
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_bytes(canonical)
    attributes = repo / '.gitattributes'
    if attributes.is_file():
        shutil.copyfile(attributes, tmp_path / '.gitattributes')
    command = [git, '-c', 'core.autocrlf=true', '-c', 'core.safecrlf=false',
               '-c', f'core.attributesFile={os.devnull}', '-C', str(tmp_path)]
    subprocess.run([*command, 'init', '-q'], check=True, capture_output=True, timeout=10)
    subprocess.run([*command, 'add', '--', '.'], check=True, capture_output=True, timeout=10)
    target.unlink()
    subprocess.run([*command, 'checkout-index', '--force', '--', relative],
                   check=True, capture_output=True, timeout=10)
    assert target.read_bytes() == canonical, 'Git checkout changed the immutable Prolog engine bytes'
