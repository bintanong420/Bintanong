import copy
import hashlib
import importlib
import json

import pytest

from backend.bintanong_tools.document_ingest.pipeline import run_ingestion
from backend.bintanong_tools.document_ingest.register import pending_version
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
from test_policy_chunks import item, raw_document
from test_prospectus_ingestion import synthetic_converter


def api():
    return importlib.import_module('backend.bintanong_tools.knowledge_update.prepare')


def manifest(tmp_path, edition='2026', kind='handbook'):
    originals = tmp_path / ('originals-' + edition)
    originals.mkdir()
    source = originals / (kind + '.pdf')
    source.write_bytes(b'%PDF-synthetic-' + edition.encode())
    spec = {'schema_version': 'bintanong-knowledge-update-v1', 'documents': [{
        'id': kind, 'kind': kind, 'edition': edition, 'title': 'Synthetic student guide',
        'source': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'locator': 'shelf:synthetic-' + edition}]}
    path = tmp_path / ('manifest-' + edition + '.json')
    path.write_text(json.dumps(spec), encoding='utf-8')
    return path, source, spec


@pytest.mark.parametrize('kind', ['handbook', 'charter'])
def test_prepare_two_editions_keep_originals_and_start_unreviewed(tmp_path, monkeypatch, kind):
    packets = []
    for edition in ['2026', '2027']:
        path, source, spec = manifest(tmp_path, edition, kind)
        before = source.read_bytes()
        snapshot = InputSnapshot(source)
        raw = raw_document([item('Submit the form.'), item('Follow the stated deadline.')], pages=1)
        packet = api().prepare(path, tmp_path / ('packet-' + edition),
            converter=synthetic_converter(monkeypatch, snapshot, raw))
        assert source.read_bytes() == before
        assert packet['candidate_only'] is True
        assert packet['documents'][0]['sha256'] == spec['documents'][0]['sha256']
        assert len(packet['items']) == 2
        assert all(row['audience'] == 'unresolved' for row in packet['items'])
        assert all(field['decision'] == 'pending' for row in packet['items'] for field in row['fields'])
        assert api().load_packet(tmp_path / ('packet-' + edition)) == packet
        packets.append(packet)
    assert packets[0]['packet_id'] != packets[1]['packet_id']


def test_prepare_replays_checked_candidate_without_conversion(tmp_path, monkeypatch):
    path, source, spec = manifest(tmp_path)
    snap = InputSnapshot(source)
    bundle = tmp_path / 'existing-bundle'
    run_ingestion(snap, [pending_version(snap, 'shelf:synthetic-2026')], input_root=source.parent,
        out=bundle, classification='policy_candidate',
        converter=synthetic_converter(monkeypatch, snap, raw_document([item('Printed instruction.')], pages=1)))
    spec['documents'][0]['candidate_bundle'] = str(bundle)
    path.write_text(json.dumps(spec), encoding='utf-8')
    monkeypatch.setattr('backend.bintanong_tools.document_ingest.pipeline.run_ingestion',
        lambda *a, **kw: pytest.fail('verified candidate replay must not convert again'))
    packet = api().prepare(path, tmp_path / 'packet')
    assert packet['items'][0]['fields'][0]['original_value'] == 'Printed instruction.'


@pytest.mark.parametrize('damage', ['hash', 'missing', 'duplicate', 'unknown_kind', 'unknown_key'])
def test_prepare_refuses_invalid_manifest_before_creating_output(tmp_path, damage):
    path, source, spec = manifest(tmp_path)
    if damage == 'hash':
        spec['documents'][0]['sha256'] = '0' * 64
    elif damage == 'missing':
        source.unlink()
    elif damage == 'duplicate':
        spec['documents'].append(copy.deepcopy(spec['documents'][0]))
    elif damage == 'unknown_kind':
        spec['documents'][0]['kind'] = 'graduate'
    else:
        spec['documents'][0]['approved'] = True
    path.write_text(json.dumps(spec), encoding='utf-8')
    with pytest.raises(ValueError):
        api().prepare(path, tmp_path / 'packet')
    assert not (tmp_path / 'packet').exists()


@pytest.mark.parametrize('attack', ['source', 'packet', 'candidate'])
def test_packet_refuses_tampering(tmp_path, monkeypatch, attack):
    path, source, _ = manifest(tmp_path)
    out = tmp_path / 'packet'
    packet = api().prepare(path, out, converter=synthetic_converter(monkeypatch,
        InputSnapshot(source), raw_document([item('Source wording.')], pages=1)))
    if attack == 'source':
        (out / packet['documents'][0]['source']).write_bytes(b'changed')
    elif attack == 'candidate':
        (out / 'candidates' / 'handbook' / 'chunks.json').write_text('{}')
    else:
        value = json.loads((out / 'packet.json').read_bytes())
        value['items'][0]['fields'][0]['original_value'] = 'forged'
        (out / 'packet.json').write_text(json.dumps(value))
    with pytest.raises(ValueError):
        api().load_packet(out)


def test_prepare_resume_does_not_repeat_conversion(tmp_path, monkeypatch):
    path, source, _ = manifest(tmp_path)
    out = tmp_path / 'packet'
    packet = api().prepare(path, out, converter=synthetic_converter(monkeypatch,
        InputSnapshot(source), raw_document([item('Source wording.')], pages=1)))
    monkeypatch.setattr('backend.bintanong_tools.document_ingest.pipeline.run_ingestion',
        lambda *a, **kw: pytest.fail('completed packet should resume without conversion'))
    assert api().prepare(path, out) == packet


def test_prepare_keeps_scanned_page_in_review_queue(tmp_path, monkeypatch):
    path, source, _ = manifest(tmp_path)
    packet = api().prepare(path, tmp_path / 'packet', converter=synthetic_converter(monkeypatch,
        InputSnapshot(source), raw_document([item('Visible on page one.')], pages=2)))
    assert any('scanned_no_text_layer' in row['findings'] for row in packet['items'])


def test_manifest_rejects_unexpected_kind_type_as_validation_error(tmp_path):
    path, _, spec = manifest(tmp_path)
    spec['documents'][0]['kind'] = []
    path.write_text(json.dumps(spec), encoding='utf-8')
    with pytest.raises(ValueError):
        api().prepare(path, tmp_path / 'packet')


def test_prepare_cli_emits_machine_readable_summary(tmp_path, monkeypatch, capsys):
    path, source, spec = manifest(tmp_path)
    snap = InputSnapshot(source)
    bundle = tmp_path / 'bundle'
    run_ingestion(snap, [pending_version(snap, 'shelf:synthetic-2026')], input_root=source.parent,
        out=bundle, classification='policy_candidate', converter=synthetic_converter(monkeypatch,
            snap, raw_document([item('Original instruction.')], pages=1)))
    spec['documents'][0]['candidate_bundle'] = str(bundle)
    path.write_text(json.dumps(spec), encoding='utf-8')
    capsys.readouterr()
    cli = importlib.import_module('backend.bintanong_tools.knowledge_update.__main__')
    assert cli.main(['prepare', str(path), '--out', str(tmp_path / 'packet')]) == 0
    assert json.loads(capsys.readouterr().out)['candidate_only'] is True
