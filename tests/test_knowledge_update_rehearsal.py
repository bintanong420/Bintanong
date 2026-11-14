"""Synthetic intake-to-draft rehearsal; conversion, embeddings and database are test doubles."""
import copy
import io

import pytest

from backend.bintanong_tools.knowledge_update import build, draft_checks, intake
from backend.bintanong_tools.knowledge_update.manifest import load_manifest
from backend.bintanong_tools.knowledge_update.prepare import prepare
from backend.bintanong_tools.knowledge_update.review import ReviewSession
from backend.bintanong_tools.knowledge_update.verify import verify
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
from test_knowledge_update_draft_checks import QueryEncoder, cases, row
from test_knowledge_update_local_release import FakeClient, stage
from test_knowledge_update_review import answer
from test_policy_chunks import item, raw_document
from test_prospectus_ingestion import synthetic_converter


@pytest.mark.parametrize('media_type', ['application/pdf', 'image/png'])
def test_upload_review_build_checks_and_repeat_stage_keep_active_release(tmp_path, monkeypatch, media_type):
    if media_type == 'application/pdf':
        import fitz
        with fitz.open() as pdf:
            pdf.new_page(width=600, height=800).insert_text((20, 160), 'Submit the form.')
            data = pdf.tobytes()
    else:
        from PIL import Image, ImageDraw
        image = Image.new('RGB', (600, 800), 'white')
        ImageDraw.Draw(image).text((20, 160), 'Submit the form.', fill='black')
        output = io.BytesIO()
        image.save(output, format='PNG')
        data = output.getvalue()

    upload = intake.create_upload(tmp_path / 'uploads', data, kind='handbook',
        title='Synthetic student guide', edition='2026', media_type=media_type)
    folder = tmp_path / 'uploads' / upload['upload_id']
    document = load_manifest(folder / 'manifest.json')['documents'][0]
    source = document['source']
    original = next((folder / 'original').iterdir())
    assert original.read_bytes() == data
    root = folder / 'packet'
    packet = prepare(folder / 'manifest.json', root,
        converter=synthetic_converter(monkeypatch, InputSnapshot(source),
            raw_document([item('Submit the form.'), item('Unreviewed item stays held.')], pages=1),
            image_ocr=media_type == 'image/png'))
    reading_id = upload['upload_id'] + ':text-0'
    with ReviewSession(root, 'Synthetic researcher') as review:
        review.save(answer(packet))
        intake.save_build_metadata(review, {'reading_ids': [reading_id],
            'assignments': [{'reading_id': reading_id, 'subject_id': 'forms'}],
            'claim_reviews': [{'subject_id': 'forms', 'claim': 'instruction', 'finding': 'visible_fields',
                'field_refs': [{'reading_id': reading_id, 'field_name': 'body'}],
                'basis_reading_id': reading_id}]})
    with ReviewSession(root, 'Synthetic researcher') as reopened:
        state = reopened.state()
        assert state['revision'] == 1
        assert state['items'][1]['fields'][0]['decision'] == 'pending'

    package_path = tmp_path / 'package'
    built = build.build(root, package_path, encoder=QueryEncoder(), metadata=root / 'review/build-metadata.json')
    assert built['coverage']['selected_readings'] == [reading_id]
    assert built['coverage']['unselected_readings'] == [upload['upload_id'] + ':text-1']
    verified = verify(package_path, packet_root=root)
    assert verified['verified'] and verified['activation_eligible'] is False
    checks = draft_checks.run_checks(package_path, cases(tmp_path, [row(expected=(reading_id,))]),
                                     tmp_path / 'checks.json', encoder=QueryEncoder())
    assert checks['passed'] and checks['package_id'] == verified['package_id']

    client = FakeClient()
    staged = stage(package_path, client, packet_root=root)
    assert staged['status'] == 'draft' and staged['created'] is True
    assert staged['chunks'] == staged['embeddings'] == 1
    assert staged['document_versions'] == 1
    assert staged['active_release_id'] == 'prior-active'
    assert staged['candidate_only'] and staged['activation_eligible'] is False
    snapshot = copy.deepcopy(client.tables)
    assert stage(package_path, client, packet_root=root)['created'] is False
    assert client.tables == snapshot
    assert client.tables['active_release'] == [{'release_id': 'prior-active'}]
    assert not {'activate_knowledge_release', 'rollback_knowledge_release',
                'designate_research_release'} & set(client.rpc_names())
    assert original.read_bytes() == data
