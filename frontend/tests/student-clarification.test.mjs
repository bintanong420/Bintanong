import test from 'node:test';
import assert from 'node:assert/strict';
import { clarificationQuestions, clarificationReply } from '../lib/student-clarification.ts';

const curricula = [{ programId: 'program-a', curriculumId: 'curriculum-a', programName: 'Synthetic program', curriculumName: 'Reviewed edition' }];
const answer = { status: 'clarification_needed', language: 'en', missingFields: ['course_status'],
  clarification: { courses: [{ code: 'B2/L', kind: 'completion' }, { code: 'C3', kind: 'enrollment' }],
    scope: { programId: 'program-a', curriculumId: 'curriculum-a' } } };

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

test('a bare clarification cannot invent another question or resend an unknown detail', () => {
  for (const language of ['en', 'fil', 'taglish', 'unknown']) {
    const bare = { status: 'clarification_needed', language, missingFields: [], clarification: { courses: [], scope: null } };
    assert.deepEqual(clarificationQuestions(bare, curricula), []);
    assert.equal(clarificationReply('Original question', bare, curricula, { details: { value: 'unknown', explanation: '' } }), null);
  }
});
