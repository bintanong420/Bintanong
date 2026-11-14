"""Routing context keeps distinct reviewed purposes inside its existing four-item budget."""
import json

from backend.bintanong_runtime.research import topic_menu


def inputs():
    chunks, assignments, refs = [], [], []
    for index, value in enumerate([*(f'Fictional deadline statement {n}.' for n in range(4)),
                                   'Complete the fictional deficiency by submitting Form Z.']):
        reading, chunk = f'reading-{index}', f'chunk-{index}'
        assignments.append(dict(reading_id=reading, subject_id='fictional_completion'))
        refs.append(dict(reading_id=reading, field_name='body'))
        chunks.append(dict(chunk_id=chunk, type_fields=dict(reading_id=reading), text=json.dumps(dict(
            fields=[dict(name='body', value=value, source_blank=False)], source_limits=[dict(
                issue='conflicting_deadlines', resolution='unresolved', affected_claims=['deadline precedence'])]))))
    reviews = [dict(subject_id='fictional_completion', claim=claim, finding='visible_fields',
                    reviewed_chunk_ids=[c['chunk_id'] for c in chunks], field_refs=fields)
               for claim, fields in [('printed timing fields', refs[:4]), ('printed method fields', refs[4:])]]
    return dict(reviews=reviews), dict(assignments=assignments), chunks


def test_repeated_timing_context_does_not_hide_the_reviewed_method_or_erase_every_context():
    register, catalogue, chunks = inputs()
    topic, = topic_menu(register, catalogue=catalogue, chunks=chunks, routing_context=True)
    assert len(topic.source_context) == 4
    method = next(value for value in topic.source_context if 'submitting Form Z' in value)
    assert method.startswith('Complete the fictional deficiency by submitting Form Z.')
    assert 'Unresolved source limitations:' in method and 'deadline precedence' in method
    assert not topic.claim_context  # a conflict-bearing body never becomes a clean printed-value hint
    assert all(len(value) <= 1024 for value in topic.source_context)


def test_unreviewed_or_cutoff_method_is_not_promoted_by_context_packing():
    for damage in ('unreviewed', 'cutoff', 'oversized'):
        register, catalogue, chunks = inputs()
        if damage == 'unreviewed':
            register['reviews'][1]['field_refs'] = []
        else:
            record = json.loads(chunks[-1]['text'])
            if damage == 'cutoff':
                record['source_limits'][0]['issue'] = 'source_cutoff'
            else:
                record['fields'][0]['value'] += 'x' * 1025
            chunks[-1]['text'] = json.dumps(record)
        topic, = topic_menu(register, catalogue=catalogue, chunks=chunks, routing_context=True)
        assert not any('submitting Form Z' in value for value in topic.source_context)
