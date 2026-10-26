import assert from 'node:assert/strict';
import test from 'node:test';
import { fieldLabel, filterItems, parseConnection, recordStatus, sourceRectangle } from '../lib/review-state.ts';

test('launch credentials accept only the declared local API shape', () => {
  assert.deepEqual(parseConnection('#api=http%3A%2F%2F127.0.0.1%3A8765&token=abcdefghijklmnop'),
    { api: 'http://127.0.0.1:8765', token: 'abcdefghijklmnop' });
  for (const api of ['https://hosted.example', 'http://127.0.0.1:8765/path',
    'http://user@127.0.0.1:8765', 'http://localhost:8765/?redirect=hosted']) {
    assert.throws(() => parseConnection('#api=' + encodeURIComponent(api) + '&token=abcdefghijklmnop'));
  }
});

test('queue combines document, literal search and unfinished state without losing rows', () => {
  const items = [
    { id: 'h:1', document_id: 'h', title: 'Forms', audience: 'undergraduate', findings: [],
      fields: [{ decision: 'accepted', original_value: 'Keep the receipt.' }] },
    { id: 'c:1', document_id: 'c', title: 'Records', audience: 'unresolved', findings: [],
      fields: [{ decision: 'pending', original_value: 'Submit the form.' }] },
    { id: 'h:2', document_id: 'h', title: 'Scanned page', audience: 'undergraduate',
      findings: ['scanned_no_text_layer'], fields: [{ decision: 'accepted', original_value: '' }] },
  ];
  assert.equal(filterItems(items, '', '', 'all').length, 3);
  assert.deepEqual(filterItems(items, 'c', 'FORM', 'attention').map(r => r.id), ['c:1']);
  assert.deepEqual(filterItems(items, 'h', '', 'attention').map(r => r.id), ['h:2']);
});

test('source highlight converts bottom-left geometry and refuses unverified dimensions', () => {
  assert.deepEqual(sourceRectangle({ bbox: [10, 700, 110, 750], bbox_origin: 'BOTTOMLEFT',
    page_size: [600, 800] }), { x: 10, y: 50, width: 100, height: 50 });
  assert.deepEqual(sourceRectangle({ bbox: [10, 50, 110, 100], bbox_origin: 'TOPLEFT',
    page_size: [600, 800] }), { x: 10, y: 50, width: 100, height: 50 });
  assert.equal(sourceRectangle({ bbox: [10, 50, 110, 100] }), null);
  assert.equal(sourceRectangle({ bbox: [-1, 50, 110, 100], bbox_origin: 'TOPLEFT',
    page_size: [600, 800] }), null);
});

test('previously reviewed records stay distinct from new decisions and source holds are searchable', () => {
  const record = { document_id: 'handbook', title: 'Completion deadline', audience: 'unresolved',
    reference_only: true, findings: [], source_gaps: [{ issue: 'conflicting_deadlines' }],
    fields: [{ name: 'percentage_equivalent', decision: 'pending', original_value: '98-100' }] };
  assert.equal(fieldLabel('percentage_equivalent'), 'Percentage equivalent');
  assert.equal(recordStatus(record), 'Known source problem');
  assert.equal(recordStatus({ ...record, source_gaps: [] }), 'Reviewed reference');
  assert.equal(filterItems([record], '', 'conflicting deadlines', 'all').length, 1);
  assert.equal(filterItems([{ ...record, source_gaps: [] }], '', '', 'attention').length, 0);
  assert.equal(filterItems([record], '', '', 'attention').length, 1);
});

test('candidate queue filters preserve independent audience, content holds and saved reviews', () => {
  const base = { document_id: 'h', title: 'Form', findings: [], audience: 'unresolved',
    fields: [{ decision: 'pending', original_value: 'Submit the form.' }] };
  const items = [{ ...base, id: 'new' },
    { ...base, id: 'held', fields: [{ decision: 'unresolved', original_value: 'Form' }] },
    { ...base, id: 'checked', audience: 'undergraduate', fields: [{ decision: 'accepted', original_value: 'Form' }] },
    { ...base, id: 'audience', fields: [{ decision: 'accepted', original_value: 'Form' }] },
    { ...base, id: 'excluded', audience: 'excluded' }];
  assert.deepEqual(filterItems(items, '', '', 'pending').map(r => r.id), ['new', 'audience']);
  assert.deepEqual(filterItems(items, '', '', 'held').map(r => r.id), ['held']);
  assert.deepEqual(filterItems(items, '', '', 'reviewed').map(r => r.id), ['checked']);
  assert.deepEqual(filterItems(items, '', '', 'excluded').map(r => r.id), ['excluded']);
  assert.equal(recordStatus(items[1]), 'Needs clarification');
  assert.equal(recordStatus(items[3]), 'Audience not checked');
});
