import test from 'node:test';
import assert from 'node:assert/strict';
import { answerNotice, createWorkspace, workspaceReducer as reduce, shouldSend, selectedPDF } from '../lib/student-workspace.ts';

test('answer notices distinguish missing evidence, source conflict and unsupported scope', () => {
  assert.deepEqual(answerNotice({ status: 'insufficient_evidence', language: 'en' }), { label: 'Information is incomplete', tone: 'warning' });
  assert.deepEqual(answerNotice({ status: 'source_conflict', language: 'en' }), { label: 'Sources need checking', tone: 'warning' });
  assert.deepEqual(answerNotice({ status: 'out_of_scope', language: 'en' }), { label: 'Outside this study', tone: 'info' });
  assert.deepEqual(answerNotice({ status: 'temporarily_unavailable', language: 'en' }), { label: 'Temporarily unavailable', tone: 'warning' });
});
test('answer notices match the backend reply language and request clarification without a decision', () => {
  assert.equal(answerNotice({ status: 'clarification_needed', language: 'fil' }).label, 'May kulang pang detalye');
  assert.equal(answerNotice({ status: 'source_conflict', language: 'taglish' }).label, 'May conflicting sources');
  assert.equal(answerNotice({ status: 'abstained', language: 'unknown' }).label, 'Unable to confirm an answer');
});
test('answered and greeting responses do not add an unsupported success claim', () => {
  assert.equal(answerNotice({ status: 'answered', language: 'en' }), null);
  assert.equal(answerNotice({ status: 'greeting', language: 'en' }), null);
});

test('empty and pending submissions do not create duplicate messages', () => {
  const empty = createWorkspace();
  assert.equal(reduce(empty, { type: 'submit', id: 'a' }), empty);
  const started = reduce({ ...empty, draft: 'Question' }, { type: 'submit', id: 'a' });
  assert.equal(started.messages.length, 2);
  assert.equal(reduce(started, { type: 'submit', id: 'b' }), started);
});
test('clear discards stale deltas and completions', () => {
  const started = reduce({ ...createWorkspace(), draft: 'Question' }, { type: 'submit', id: 'a' });
  const cleared = reduce(started, { type: 'clear' });
  assert.equal(reduce(cleared, { type: 'delta', id: 'a', text: 'Late' }), cleared);
  assert.equal(reduce(cleared, { type: 'complete', id: 'a', answer: {} }), cleared);
});
test('interruption preserves the user message and an unrelated draft', () => {
  let state = reduce({ ...createWorkspace(), draft: 'Question' }, { type: 'submit', id: 'a' });
  state = reduce(state, { type: 'draft', text: 'Another question' });
  state = reduce(state, { type: 'interrupt', id: 'a', warning: 'Stopped' });
  assert.equal(state.messages[0].text, 'Question');
  assert.equal(state.draft, 'Another question');
  assert.equal(state.messages[1].delivery, 'interrupted');
});
test('explicit clarification submission preserves the unrelated composer draft', () => {
  const initial = { ...createWorkspace(), draft: 'Keep my next question' };
  const state = reduce(initial, { type: 'submit', id: 'clarify', text: 'Original question. I do not know whether I passed B2.' });
  assert.equal(state.messages[0].text, 'Original question. I do not know whether I passed B2.');
  assert.equal(state.draft, 'Keep my next question');
  assert.equal(reduce(state, { type: 'submit', id: 'duplicate', text: 'Duplicate' }), state);
});
test('IME and Shift Enter do not submit', () => {
  assert.equal(shouldSend({ key: 'Enter', shiftKey: false, isComposing: true, keyCode: 13 }), false);
  assert.equal(shouldSend({ key: 'Enter', shiftKey: false, isComposing: false, keyCode: 229 }), false);
  assert.equal(shouldSend({ key: 'Enter', shiftKey: true, isComposing: false, keyCode: 13 }), false);
  assert.equal(shouldSend({ key: 'Enter', shiftKey: false, isComposing: false, keyCode: 13 }), true);
});
test('unsupported or multiple selection does not replace an existing review', () => {
  const invalid = new File(['image'], 'synthetic.png', { type: 'image/png' });
  assert.equal(selectedPDF([invalid]).file, null);
  const pdf = new File(['%PDF'], 'synthetic.pdf', { type: 'application/pdf' });
  assert.equal(selectedPDF([pdf, pdf]).file, null);
  assert.equal(selectedPDF([pdf]).file, pdf);
  assert.equal(selectedPDF([pdf]).file, pdf);
});
