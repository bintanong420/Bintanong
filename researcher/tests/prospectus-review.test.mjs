import assert from 'node:assert/strict';
import test from 'node:test';
import { answerPayload, filterQuestions, groupBySection, nextAfter, progressLine, prospectusFieldLabel, statusLines, step, warningCount }
  from '../lib/prospectus-review.ts';

const q = (qid, sid = 's1', prompt = `Is ${qid} correct?`) => ({ qid, prompt, section: { sid, title: sid.toUpperCase(), health: 'clean' } });

test('after a save the next question follows the saved one, wrapping, never itself', () => {
  const queue = [q('A'), q('B'), q('C')];
  assert.equal(nextAfter(queue, 'B'), 'C');
  assert.equal(nextAfter(queue, 'C'), 'A');
  assert.equal(nextAfter([q('B')], 'B'), null);
  // the saved question left the attention queue: start from the top, as the original reviewer did
  assert.equal(nextAfter([q('A'), q('C')], 'B'), 'A');
  assert.equal(nextAfter([], 'B'), null);
});

test('previous and next stay inside the queue', () => {
  const queue = [q('A'), q('B'), q('C')];
  assert.equal(step(queue, 'B', 1), 'C');
  assert.equal(step(queue, 'C', 1), 'C');
  assert.equal(step(queue, 'A', -1), 'A');
  assert.equal(step(queue, 'missing', 1), 'A');
  assert.equal(step([], 'A', 1), null);
});

test('the filter matches the question id or prompt, ignoring case', () => {
  const queue = [q('P-CC5', 's1', 'Is CC 5/L correct?'), q('P-GE1', 's1', 'Is Purposive Communication correct?')];
  assert.equal(filterQuestions(queue, '  ').length, 2);
  assert.deepEqual(filterQuestions(queue, 'ge1').map(x => x.qid), ['P-GE1']);
  assert.deepEqual(filterQuestions(queue, 'cc 5/l').map(x => x.qid), ['P-CC5']);
  assert.deepEqual(filterQuestions(queue, 'nursing'), []);
});

test('sections group by id in queue order', () => {
  const groups = groupBySection([q('A', 's1'), q('B', 's2'), q('C', 's1'), q('D', 's3')]);
  assert.deepEqual(groups.map(g => [g.section.sid, g.items.map(x => x.qid)]), [['s1', ['A', 'C']], ['s2', ['B']], ['s3', ['D']]]);
  const same = groupBySection([{ ...q('A', 'x'), section: { sid: 'x', title: 'First year', health: 'ok' } },
    { ...q('B', 'y'), section: { sid: 'y', title: 'First year', health: 'review' } }]);
  assert.equal(same.length, 2);
  assert.deepEqual(groupBySection([]), []);
});

test('prospectus fields use the printed labels, unknown names stay readable', () => {
  assert.equal(prospectusFieldLabel('prerequisites_raw'), 'Prerequisites as printed');
  assert.equal(prospectusFieldLabel('lab_units'), 'Lab units');
  assert.equal(prospectusFieldLabel('some_new_field'), 'some new field');
  // question references use short names for the same printed columns
  assert.equal(prospectusFieldLabel('code'), 'Course code');
  assert.equal(prospectusFieldLabel('title'), 'Course title');
});

test('progress counts decisions across the whole prospectus, not the shrinking attention queue', () => {
  assert.equal(progressLine({ progress: { decided: 2, questions: 3 } }), '2 of 3 questions decided');
  assert.equal(progressLine(undefined), 'Loading questions…');
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

test('warning count covers unchecked PDF text, Docling and ledger problems only', () => {
  assert.equal(warningCount(state), 3);
  assert.equal(warningCount({ ...state, source_verification: { health: 'clean', pdf_checked: true }, docling: { warning: null },
    content_review: { stale_entries: 0, inapplicable_entries: 0, invalid_entries: 0 } }), 0);
  assert.equal(warningCount(undefined), 0);
});
