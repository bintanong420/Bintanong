import assert from 'node:assert/strict';
import test from 'node:test';
import { answerPayload, prospectusFieldLabel, statusLines } from '../lib/prospectus-review.ts';

test('prospectus fields use the printed labels, unknown names stay readable', () => {
  assert.equal(prospectusFieldLabel('prerequisites_raw'), 'Prerequisites as printed');
  assert.equal(prospectusFieldLabel('lab_units'), 'Lab units');
  assert.equal(prospectusFieldLabel('some_new_field'), 'some new field');
});

test('Other on a prerequisite sends an untouched blank as "none"', () => {
  const question = { qid: 'P1', kind: 'prerequisite', editable_fields: ['prerequisites_raw'] };
  assert.deepEqual(answerPayload(question, 'other', {}, 'blank in the original').edits, { prerequisites_raw: '' });
  assert.deepEqual(answerPayload(question, 'other', { prerequisites_raw: 'CC 1' }, '').edits, { prerequisites_raw: 'CC 1' });
});

test('elsewhere an untouched or blank field means unchanged, and Yes/No send no edits', () => {
  const course = { qid: 'C1', kind: 'course', editable_fields: ['course_code', 'course_title'] };
  assert.deepEqual(answerPayload(course, 'other', { course_code: 'CC 5/L', course_title: '  ' }, 'r').edits, { course_code: 'CC 5/L' });
  assert.deepEqual(answerPayload(course, 'yes', { course_code: 'x' }, 'r').edits, {});
});

test('section confirmation sends the text as a note, other kinds as a reason', () => {
  const section = { qid: 'S1', kind: 'section_confirm', editable_fields: [] };
  assert.deepEqual(answerPayload(section, 'yes', {}, 'ok'), { qid: 'S1', choice: 'yes', edits: {}, proposals: [], reason: '', note: 'ok' });
  const course = { qid: 'C1', kind: 'course', editable_fields: [] };
  assert.equal(answerPayload(course, 'no', {}, 'why').reason, 'why');
});

const state = {
  approval_line: 'Nothing here is an approval.',
  review_states: [{ name: 'content', word: 'pending', meaning: 'not reviewed' }],
  source_verification: { health: 'warn', pdf_checked: false },
  prerequisites: { questions: 4, decided: 1, unclassified_courses: 2 },
  content_review: { stale_entries: 1, inapplicable_entries: 0, invalid_entries: 3 },
  docling: { warning: 'raw JSON missing' },
};

test('status lines keep every integrity warning the old reviewer showed', () => {
  const lines = statusLines(state);
  assert.equal(lines[0], 'Nothing here is an approval.');
  for (const expected of ['content: pending (not reviewed)', 'PDF text check: warn, PDF text not checked',
    'prerequisite questions: 1 of 4 decided', '2 courses have no prerequisite state', 'Docling JSON: raw JSON missing',
    'ledger: 1 stale, 0 for another PDF, 3 unreadable']) {
    assert.ok(lines.some(line => line.includes(expected)), expected);
  }
});

test('clean state omits the optional warnings', () => {
  const lines = statusLines({ ...state, prerequisites: { questions: 0, decided: 0, unclassified_courses: 0 },
    content_review: { stale_entries: 0, inapplicable_entries: 0, invalid_entries: 0 }, docling: { warning: null } });
  assert.equal(lines.length, 3);
  assert.deepEqual(statusLines(undefined), []);
});
