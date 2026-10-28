import test from 'node:test';
import assert from 'node:assert/strict';
import { pageRedirect } from '../lib/auth-policy.ts';

test('the landing page stays public for visitors and signed-in students', () => {
  assert.equal(pageRedirect('/', false), null);
  assert.equal(pageRedirect('/', true), null);
});

test('chat requires sign-in and successful sign-in leads to chat', () => {
  assert.equal(pageRedirect('/chat', false), '/login');
  assert.equal(pageRedirect('/chat', true), null);
  assert.equal(pageRedirect('/login', true), '/chat');
  assert.equal(pageRedirect('/login', false), null);
});
