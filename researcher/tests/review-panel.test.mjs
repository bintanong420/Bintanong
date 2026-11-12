import assert from 'node:assert/strict';
import test from 'node:test';
import { DEFAULT_REASON, fieldAfterChoice, reasonFor, revealScrollTop, stepIndex, textOf, windowRange } from '../lib/review-form.ts';
import { filterItems } from '../lib/review-state.ts';

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

test('revealing a row scrolls only when it is outside the viewport', () => {
  assert.equal(revealScrollTop(0, 400, 2, 80), 0);
  assert.equal(revealScrollTop(0, 400, 10, 80), 480);
  assert.equal(revealScrollTop(900, 400, 3, 80), 240);
  assert.equal(revealScrollTop(240, 400, 4, 80), 240);
});

test('choosing Matches restores the extracted text, Fix text keeps the draft, Unclear keeps it too', () => {
  const edited = { decision: 'corrected', text: 'my edit' };
  assert.deepEqual(fieldAfterChoice('Original', edited, 'accepted'), { decision: 'accepted', text: 'Original' });
  assert.deepEqual(fieldAfterChoice('Original', edited, 'corrected'), { decision: 'corrected', text: 'my edit' });
  assert.deepEqual(fieldAfterChoice('Original', edited, 'unresolved'), { decision: 'unresolved', text: 'my edit' });
  assert.deepEqual(fieldAfterChoice(['a', 1], edited, 'accepted'), { decision: 'accepted', text: textOf(['a', 1]) });
});

test('a note is only required when something was decided, and the default never hides a missing decision', () => {
  const none = { audience: 'unresolved', gaps: [], fields: { a: { decision: 'pending' }, b: { decision: 'pending' } } };
  assert.equal(reasonFor('', none), '');
  assert.equal(reasonFor('  ', none), '');
  assert.equal(reasonFor('Checked the table', none), 'Checked the table');
  const decided = { ...none, fields: { a: { decision: 'accepted' }, b: { decision: 'pending' } } };
  assert.equal(reasonFor('', decided), DEFAULT_REASON);
  assert.equal(reasonFor(' Fixed typo ', decided), 'Fixed typo');
  assert.equal(reasonFor('', { ...none, audience: 'undergraduate' }), DEFAULT_REASON);
  assert.equal(reasonFor('', { ...none, gaps: [{ issue: 'x' }] }), DEFAULT_REASON);
  assert.equal(DEFAULT_REASON, 'Checked against the page');
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
