import assert from 'node:assert/strict';
import test from 'node:test';
import { SUGGESTED_NOTE, buildPayload, draftFor, fieldAfterChoice, isDirty, leaveWarning, nextIndexForKey, revealScrollTop,
  statusBadge, stepIndex, switchGate, textOf, windowRange } from '../lib/review-form.ts';
import { filterItems } from '../lib/review-state.ts';

const item = (extra = {}) => ({ id: 'i1', document_id: 'd', title: 'T', audience: 'unresolved', findings: [], companions: [], reason: '', gaps: [],
  fields: [{ name: 'body', original_value: 'Original', reviewed_value: 'Original', decision: 'pending' },
    { name: 'steps', original_value: ['a', 1], reviewed_value: ['a', 1], decision: 'pending' }], ...extra });

test('the list renders only the rows in view plus a margin', () => {
  assert.deepEqual(windowRange(0, 400, 80, 600, 2), { start: 0, end: 7 });
  assert.deepEqual(windowRange(800, 400, 80, 600, 2), { start: 8, end: 17 });
  assert.deepEqual(windowRange(100000, 400, 80, 600, 2), { start: 598, end: 600 });
  assert.deepEqual(windowRange(0, 400, 80, 0, 2), { start: 0, end: 0 });
  assert.deepEqual(windowRange(-50, 0, 80, 10, 2), { start: 0, end: 2 });
});

test('arrow keys step one row and stop at both ends', () => {
  assert.equal(stepIndex(3, 1, 10), 4);
  assert.equal(stepIndex(0, -1, 10), 0);
  assert.equal(stepIndex(9, 1, 10), 9);
  assert.equal(stepIndex(-1, 1, 10), 0);
  assert.equal(stepIndex(-1, -1, 10), 9);
  assert.equal(stepIndex(2, 1, 0), -1);
});

test('list keys map to a target row, and anything else is ignored', () => {
  assert.equal(nextIndexForKey('ArrowDown', 3, 10), 4);
  assert.equal(nextIndexForKey('ArrowUp', 3, 10), 2);
  assert.equal(nextIndexForKey('ArrowUp', 0, 10), 0);
  assert.equal(nextIndexForKey('Home', 5, 10), 0);
  assert.equal(nextIndexForKey('End', 5, 10), 9);
  assert.equal(nextIndexForKey('PageDown', 5, 100, 8), 13);
  assert.equal(nextIndexForKey('PageDown', 95, 100, 8), 99);
  assert.equal(nextIndexForKey('PageUp', 3, 100, 8), 0);
  assert.equal(nextIndexForKey('ArrowDown', -1, 10), 0);
  assert.equal(nextIndexForKey('a', 3, 10), null);
  assert.equal(nextIndexForKey('ArrowDown', 0, 0), null);
});

test('revealing a row scrolls only when it is outside the viewport', () => {
  assert.equal(revealScrollTop(0, 400, 2, 80), 0);
  assert.equal(revealScrollTop(0, 400, 10, 80), 480);
  assert.equal(revealScrollTop(900, 400, 3, 80), 240);
  assert.equal(revealScrollTop(240, 400, 4, 80), 240);
});

test('Matches restores the extracted text but the reviewer\'s last edit comes back with Fix text', () => {
  const edited = { decision: 'corrected', text: 'my edit' };
  const matched = fieldAfterChoice('Original', edited, 'accepted');
  assert.equal(matched.decision, 'accepted'); assert.equal(matched.text, 'Original');
  const again = fieldAfterChoice('Original', matched, 'corrected');
  assert.deepEqual([again.decision, again.text], ['corrected', 'my edit']);
  assert.equal(fieldAfterChoice('Original', edited, 'unresolved').text, 'my edit');
  assert.equal(fieldAfterChoice(['a', 1], edited, 'accepted').text, textOf(['a', 1]));
  assert.equal(fieldAfterChoice('Original', { decision: 'accepted', text: 'Original' }, 'corrected').text, 'Original');
});

test('a field can go back to Not checked, keeping the edit for later', () => {
  const cleared = fieldAfterChoice('Original', { decision: 'corrected', text: 'my edit' }, 'pending');
  assert.deepEqual([cleared.decision, cleared.text], ['pending', 'Original']);
  assert.equal(fieldAfterChoice('Original', cleared, 'corrected').text, 'my edit');
});

test('the save payload sends exactly what the reviewer chose', () => {
  const row = item();
  const draft = draftFor(row);
  const untouched = buildPayload(row, draft, 7, 'op-1');
  assert.equal(untouched.fields.body.decision, 'pending');
  assert.equal(untouched.fields.body.value, 'Original');
  assert.deepEqual(untouched.fields.steps, { decision: 'pending', value: ['a', 1] });
  assert.deepEqual([untouched.item_id, untouched.revision, untouched.operation_id], ['i1', 7, 'op-1']);
  draft.fields.body = fieldAfterChoice('Original', draft.fields.body, 'accepted');
  draft.fields.steps = { decision: 'unresolved', text: textOf(['a', 1]) };
  draft.reason = ' Compared with page 4 ';
  const sent = buildPayload(row, draft, 7, 'op-2');
  assert.deepEqual(sent.fields.body, { decision: 'accepted', value: 'Original' });
  assert.equal(sent.fields.steps.decision, 'unresolved');
  assert.equal(sent.reason, ' Compared with page 4 ');
  draft.fields.body = { decision: 'corrected', text: 'Fixed' };
  assert.deepEqual(buildPayload(row, draft, 7, 'op-3').fields.body, { decision: 'corrected', value: 'Fixed' });
});

test('the reason is never filled in for the reviewer', () => {
  const row = item();
  assert.equal(buildPayload(row, draftFor(row), 1, 'o').reason, '');
  assert.equal(SUGGESTED_NOTE, 'Checked against the page');
});

test('unsaved edits are detected, and the edit memory does not count as an edit', () => {
  const row = item();
  const draft = draftFor(row);
  assert.equal(isDirty(row, draft), false);
  assert.equal(isDirty(row, { ...draft, reason: 'x' }), true);
  assert.equal(isDirty(row, { ...draft, audience: 'undergraduate' }), true);
  assert.equal(isDirty(row, { ...draft, fields: { ...draft.fields, body: { ...draft.fields.body, edit: 'old' } } }), false);
  assert.equal(isDirty(row, { ...draft, fields: { ...draft.fields, body: { decision: 'accepted', text: 'Original' } } }), true);
});

test('switching records asks first when there are unsaved edits, and waits for a pending save', () => {
  assert.equal(switchGate(false, false), 'go');
  assert.equal(switchGate(true, false), 'confirm');
  assert.equal(switchGate(false, true), 'blocked');
  assert.equal(switchGate(true, true), 'blocked');
  assert.equal(leaveWarning(true, false), true);
  assert.equal(leaveWarning(false, true), true);
  assert.equal(leaveWarning(false, false), false);
});

test('record status becomes a short label with a tone', () => {
  assert.deepEqual(statusBadge('Not checked yet'), { label: 'Not checked', tone: 'todo' });
  assert.deepEqual(statusBadge('Review saved'), { label: 'Saved', tone: 'done' });
  assert.deepEqual(statusBadge('Known source problem'), { label: 'Source problem', tone: 'hold' });
  assert.deepEqual(statusBadge('Needs clarification'), { label: 'Unclear', tone: 'hold' });
  assert.deepEqual(statusBadge('Outside this study'), { label: 'Outside study', tone: 'muted' });
  assert.deepEqual(statusBadge('Something new'), { label: 'Something new', tone: 'todo' });
});

test('filtering stays literal and repeatable after the search text is cached per record', () => {
  const items = [{ id: '1', document_id: 'h', title: 'Grading', audience: 'unresolved', findings: [], fields: [{ decision: 'pending', original_value: 'Passing grade is 75' }] },
    { id: '2', document_id: 'h', title: 'Clearance', audience: 'unresolved', findings: [], fields: [{ decision: 'pending', original_value: ['x'] }] }];
  assert.deepEqual(filterItems(items, '', 'passing', 'all').map(r => r.id), ['1']);
  assert.deepEqual(filterItems(items, '', 'PASSING', 'all').map(r => r.id), ['1']);
  assert.deepEqual(filterItems(items, '', 'clear', 'all').map(r => r.id), ['2']);
  const reloaded = [{ ...items[0], fields: [{ decision: 'pending', original_value: 'changed' }] }];
  assert.deepEqual(filterItems(reloaded, '', 'changed', 'all').map(r => r.id), ['1']);
  assert.deepEqual(filterItems(reloaded, '', 'passing', 'all'), []);
});
