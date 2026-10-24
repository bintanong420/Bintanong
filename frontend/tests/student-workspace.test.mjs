import test from 'node:test';
import assert from 'node:assert/strict';
import { createWorkspace, workspaceReducer as reduce, shouldSend, selectedPDF } from '../lib/student-workspace.ts';

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
