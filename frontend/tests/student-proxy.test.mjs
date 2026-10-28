import test from 'node:test';
import assert from 'node:assert/strict';
import { forwardStudentRequest } from '../lib/student-proxy.ts';

const base = 'https://bintanong.example';
const options = { baseUrl: 'http://127.0.0.1:8021', accessToken: 'synthetic-access-token' };
const cookie = '__Host-bintanong_session=' + 'a'.repeat(43);
function request(path, method = 'POST', headers = {}, body = '{}') {
  return new Request(base + path, { method, headers: { Origin: base, Cookie: cookie, ...headers }, ...(method === 'GET' ? {} : { body }) });
}

test('proxy forwards only owned session cookie and server-resolved auth', async () => {
  const response = await forwardStudentRequest(request('/api/chat', 'POST', { Cookie: cookie + '; unrelated=secret' }), '/chat', { ...options,
    fetch: async (url, init) => {
      assert.equal(String(url), 'http://127.0.0.1:8021/chat');
      assert.equal(init.headers.get('Cookie'), cookie);
      assert.equal(init.headers.get('Authorization'), 'Bearer synthetic-access-token');
      assert.equal(init.redirect, 'error');
      return new Response('data', { headers: { 'Set-Cookie': cookie + '; Secure; HttpOnly; SameSite=Strict; Path=/' } });
    } });
  assert.match(response.headers.get('set-cookie'), /^__Host-bintanong_session=/);
  assert.equal(response.headers.get('cache-control'), 'no-store');
});

test('foreign origin and unknown routes never reach upstream', async () => {
  let calls = 0;
  const fetcher = async () => { calls++; return new Response(); };
  assert.equal((await forwardStudentRequest(request('/api/chat', 'POST', { Origin: 'https://attacker.example' }), '/chat', { ...options, fetch: fetcher })).status, 403);
  assert.equal((await forwardStudentRequest(request('/api/chat'), '//attacker.example', { ...options, fetch: fetcher })).status, 404);
  assert.equal(calls, 0);
});

test('guests forward without authorization while retaining the owned session cookie', async () => {
  let calls = 0;
  const response = await forwardStudentRequest(request('/api/chat'), '/chat', { ...options, accessToken: null,
    fetch: async (_url, init) => {
      calls++;
      assert.equal(init.headers.has('Authorization'), false);
      assert.equal(init.headers.get('Cookie'), cookie);
      return new Response('guest-stream');
    } });
  assert.equal(response.status, 200);
  assert.equal(await response.text(), 'guest-stream');
  assert.equal(calls, 1);
});

test('browser authorization cannot replace cookie identity or downgrade to a guest', async () => {
  let calls = 0;
  const response = await forwardStudentRequest(request('/api/chat', 'POST', { Authorization: 'Basic invalid' }), '/chat', {
    ...options, fetch: async () => { calls++; return new Response(); } });
  assert.equal(response.status, 401);
  assert.equal((await response.json()).error, 'sign_in_required');
  assert.equal(calls, 0);
});

test('invalid cookie credentials still reach backend verification', async () => {
  let calls = 0;
  const response = await forwardStudentRequest(request('/api/chat'), '/chat', { ...options, accessToken: 'invalid-token',
    fetch: async (_url, init) => {
      calls++;
      assert.equal(init.headers.get('Authorization'), 'Bearer invalid-token');
      return Response.json({ error: 'sign_in_required' }, { status: 401 });
    } });
  assert.equal(response.status, 401);
  assert.equal(calls, 1);
});

test('upload scope query survives fixed-route forwarding', async () => {
  await forwardStudentRequest(request('/api/uploads?programId=program-a&curriculumId=curriculum-a'), '/uploads', { ...options,
    fetch: async (url, init) => {
      assert.equal(new URL(url).searchParams.get('curriculumId'), 'curriculum-a');
      assert.equal(init.headers.get('Content-Type'), 'application/octet-stream');
      return Response.json({});
    } });
});

test('oversize JSON is rejected before upstream and cancellation is forwarded', async () => {
  let called = false;
  const rejected = await forwardStudentRequest(request('/api/chat', 'POST', {}, 'x'.repeat(32769)), '/chat', { ...options, fetch: async () => { called = true; return new Response(); } });
  assert.equal(rejected.status, 413); assert.equal(called, false);
  const controller = new AbortController();
  const input = new Request(base + '/api/curricula', { signal: controller.signal });
  await forwardStudentRequest(input, '/curricula', { ...options, fetch: async (_url, init) => {
    controller.abort(); assert.equal(init.signal.aborted, true); return new Response();
  } });
});
