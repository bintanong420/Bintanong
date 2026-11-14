import test from 'node:test';
import assert from 'node:assert/strict';
import { SIGN_IN_ENABLED, pageRedirect } from '../lib/auth-policy.ts';

test('the landing page stays public for visitors and signed-in students', () => {
  assert.equal(pageRedirect('/', false), null);
  assert.equal(pageRedirect('/', true), null);
});

test('chat accepts guests', () => {
  assert.equal(pageRedirect('/chat', false), null);
  assert.equal(pageRedirect('/chat', true), null);
});

// Owner, 4 Nov 2026: sign-in is switched off for now (kept for later); nobody reaches the sign-in page.
test('with sign-in switched off, the sign-in page sends everyone to the landing page', () => {
  assert.equal(SIGN_IN_ENABLED, false);
  assert.equal(pageRedirect('/login', false), '/');
  assert.equal(pageRedirect('/login', true), '/');
});

test('when sign-in is switched back on, successful sign-in still leads to chat', () => {
  assert.equal(pageRedirect('/login', true, true), '/chat');
  assert.equal(pageRedirect('/login', false, true), null);
});
