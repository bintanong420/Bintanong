import test from 'node:test';
import assert from 'node:assert/strict';
import { clarificationQuestions, clarificationReply, typedReply } from '../lib/student-clarification.ts';

const curricula = [{ programId: 'program-a', curriculumId: 'curriculum-a', programName: 'Synthetic program', curriculumName: 'Reviewed edition' }];
const answer = { status: 'clarification_needed', language: 'en', missingFields: ['course_status'],
  clarification: { courses: [{ code: 'B2/L', kind: 'completion' }, { code: 'C3', kind: 'enrollment' }],
    scope: { programId: 'program-a', curriculumId: 'curriculum-a' } } };

test('server-bound dialog and typed replies send only the new student utterance', () => {
  const bound = { ...answer, clarification: { ...answer.clarification,
    courses: [{ code: 'B2/L', kind: 'completion', slot: 'completion_unknown:course-b' },
      { code: 'C3', kind: 'enrollment', slot: 'enrollment_unknown:course-c' }],
    binding: { replyToTurnId: 'turn-owned', revision: 3,
      requestedSlots: ['completion_unknown:course-b', 'enrollment_unknown:course-c'] } } };
  const reply = clarificationReply('Can I take A1?', bound, curricula, {
    'completion:B2/L': { value: 'unknown', explanation: '' },
    'enrollment:C3': { value: 'not_enrolled', explanation: '' },
  });
  assert.ok(!reply.text.includes('Can I take A1?'));
  assert.deepEqual(reply.clarificationReply, { replyToTurnId: 'turn-owned', revision: 3, slots: [
    { slot: 'completion_unknown:course-b', value: 'unknown' },
    { slot: 'enrollment_unknown:course-c', value: 'not_enrolled' },
  ] });
  const typed = typedReply('Can I take A1?', bound, 'I took it, but do not know my result.', curricula);
  assert.equal(typed.text, 'I took it, but do not know my result.');
  assert.deepEqual(typed.clarificationReply, { replyToTurnId: 'turn-owned', revision: 3, slots: [] });
});

test('no default or incomplete choices can be submitted', () => {
  assert.equal(clarificationReply('Can I take A1?', answer, curricula, {}), null);
  assert.equal(clarificationReply('Can I take A1?', answer, curricula, { 'completion:B2/L': { value: 'passed', explanation: '' } }), null);
});
test('unknown remains unknown and contradictory explanations accompany the choice', () => {
  const reply = clarificationReply('Can I take A1?', answer, curricula, {
    'completion:B2/L': { value: 'unknown', explanation: 'I might have passed it; please check what I mean.' },
    'enrollment:C3': { value: 'enrolled', explanation: 'Actually, I dropped it yesterday.' },
  });
  assert.match(reply.text, /Can I take A1\?/);
  assert.match(reply.text, /I do not know whether I have passed B2\/L/);
  assert.match(reply.text, /Actually, I dropped it yesterday/);
  assert.match(reply.text, /I am currently enrolled in C3/);
  assert.ok(!reply.text.includes('failed'));
  assert.deepEqual(reply.scope, { programId: 'program-a', curriculumId: 'curriculum-a' });
});
test('only supported curriculum choices supply scope and an unknown selection clears it', () => {
  const missing = { ...answer, missingFields: ['program', 'curriculum'], clarification: undefined };
  const questions = clarificationQuestions(missing, curricula);
  assert.equal(questions.length, 1);
  const reply = clarificationReply('Which courses next?', missing, curricula, { scope: { value: 'curriculum-a', explanation: 'I am a transferee.' } });
  assert.deepEqual(reply.scope, { programId: 'program-a', curriculumId: 'curriculum-a' });
  assert.match(reply.text, /Reviewed edition/);
  assert.match(reply.text, /I am a transferee/);
  assert.equal(clarificationReply('Question', missing, curricula, { scope: { value: 'invented', explanation: '' } }), null);
  assert.equal(clarificationReply('Question', missing, curricula, { scope: { value: 'unknown', explanation: '' } }).scope, null);
});
test('missing grounded options allow an explanation without inventing a course', () => {
  const missing = { ...answer, clarification: undefined };
  const questions = clarificationQuestions(missing, []);
  assert.equal(questions.length, 1);
  assert.equal(questions[0].options.length, 2);
  assert.equal(clarificationReply('Question', missing, [], { course_status: { value: 'other', explanation: '' } }), null);
  assert.match(clarificationReply('Question', missing, [], { course_status: { value: 'other', explanation: 'I transferred from another program.' } }).text, /I transferred/);
});
test('each reply language preserves unknown and final replies stay within chat limits', () => {
  for (const language of ['fil', 'taglish']) {
    const translated = { ...answer, language };
    const reply = clarificationReply('Puwede ba ang A1?', translated, curricula, {
      'completion:B2/L': { value: 'unknown', explanation: '' }, 'enrollment:C3': { value: 'unknown', explanation: '' },
    });
    assert.match(reply.text, /Hindi ko alam/);
    assert.ok(!reply.text.includes('I do not know'));
  }
  assert.throws(() => clarificationReply('X'.repeat(8190), answer, curricula, {
    'completion:B2/L': { value: 'passed', explanation: '' }, 'enrollment:C3': { value: 'enrolled', explanation: '' },
  }), /clarification_too_long/);
});

test('prerequisite replies send the original question and selected facts without asking the dialog questions again', () => {
  const original = 'Ano ang prerequisites ng ZZ5?';
  const prerequisite = { ...answer, language: 'fil', clarification: {
    ...answer.clarification, courses: [{ code: 'ZZ 4/L', kind: 'completion' }, { code: 'ZZ 3/L', kind: 'completion' }],
  } };
  const reply = clarificationReply(original, prerequisite, curricula, {
    'completion:ZZ 4/L': { value: 'passed', explanation: '' },
    'completion:ZZ 3/L': { value: 'not_passed', explanation: '' },
  });
  assert.equal(reply.text, original + '\n\nPasado na ako sa ZZ 4/L.\nHindi pa ako pasado sa ZZ 3/L.');
  assert.deepEqual(reply.scope, prerequisite.clarification.scope);
  assert.ok(!reply.text.includes('failed'), 'not passed never asserts a failed grade');
});

test('the leaving-or-incoming question offers both sides and resends the original question with the choice', () => {
  // Owner GUI 3 Nov 2026 (H2): the direction question had no choices ("No specific clarification question was provided.").
  for (const [language, leaving, incoming] of [
    ['en', 'I am leaving PalSU (transfer credentials / honorable dismissal).', 'I am transferring into PalSU from another school.'],
    ['taglish', 'Aalis ako sa PalSU (transfer credentials / honorable dismissal).', 'Lilipat ako sa PalSU galing sa ibang school.']]) {
    const asked = { status: 'clarification_needed', language, missingFields: ['transfer_direction'], clarification: { courses: [], scope: null } };
    const [question] = clarificationQuestions(asked, curricula);
    assert.equal(question.key, 'transfer_direction');
    assert.deepEqual(question.options.slice(0, 2).map(o => o.text), [leaving, incoming]);
    assert.equal(clarificationReply('How to secure Transfer Credentials?', asked, curricula,
      { transfer_direction: { value: 'leaving', explanation: '' } }).text, 'How to secure Transfer Credentials?\n\n' + leaving);
  }
});

test('a bare clarification cannot invent another question or resend an unknown detail', () => {
  for (const language of ['en', 'fil', 'taglish', 'unknown']) {
    const bare = { status: 'clarification_needed', language, missingFields: [], clarification: { courses: [], scope: null } };
    assert.deepEqual(clarificationQuestions(bare, curricula), []);
    assert.equal(clarificationReply('Original question', bare, curricula, { details: { value: 'unknown', explanation: '' } }), null);
  }
});

// Owner 3 Nov 2026 (fix 2): a typed reply to the leaving-or-incoming question carries the original question, like the
// dialog choice; live, "aalis ako sa PalSU" alone was checked as the question and the fee answer was rejected.
test('a typed reply to the direction question carries the original question', () => {
  const asked = { status: 'clarification_needed', language: 'taglish', missingFields: ['transfer_direction'], clarification: { courses: [], scope: null } };
  assert.deepEqual(typedReply('magkano bayad sa transfer credentials?', asked, ' aalis ako sa PalSU ', curricula), { text: 'magkano bayad sa transfer credentials?\n\naalis ako sa PalSU', scope: null });
  assert.deepEqual(typedReply('Can I take A1?', answer, 'passed B2/L', curricula), { text: 'passed B2/L', scope: null });
  assert.deepEqual(typedReply('X'.repeat(8190), asked, 'aalis ako', curricula), { text: 'aalis ako', scope: null });
});

// Owner GUI 3 Nov 2026 (#12): typing one of the offered program names answers 'Which program is this for?' like the
// dialog choice; the name alone reached the router as a question and failed.
test('a typed program name selects that program and resends the original question', () => {
  const program = { status: 'clarification_needed', language: 'en', missingFields: ['program'], clarification: { courses: [], scope: null } };
  assert.deepEqual(typedReply('What are my first-term subjects?', program, ' synthetic PROGRAM ', curricula),
    { text: 'What are my first-term subjects?\n\nSynthetic program · Reviewed edition', scope: { programId: 'program-a', curriculumId: 'curriculum-a' } });
  assert.deepEqual(typedReply('What are my first-term subjects?', program, 'Another program', curricula), { text: 'Another program', scope: null });
});

// Owner GUI 3 Nov 2026 (#12 follow-up): after an answer, typing another program name asks the last question again for
// that program; the server keeps ids only, so the name alone had no question.
test('a typed program name after an answer asks the last question for that program', () => {
  assert.deepEqual(typedReply('What are my first-term subjects?\n\nOther program · 2018', null, 'Synthetic program', curricula),
    { text: 'What are my first-term subjects?\n\nSynthetic program · Reviewed edition', scope: { programId: 'program-a', curriculumId: 'curriculum-a' } });
  assert.deepEqual(typedReply('What are my first-term subjects?', null, 'What about Ethics?', curricula), { text: 'What about Ethics?', scope: null });
});
