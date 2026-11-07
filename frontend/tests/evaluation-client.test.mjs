import test from 'node:test';
import assert from 'node:assert/strict';
import { caseStatuses, countedRunId, listRuns, loadCases, matchCase, progress, runEvaluation, saveJudgment }
  from '../lib/evaluation-client.ts';
import { forwardStudentRequest } from '../lib/student-proxy.ts';

const cases = [{ case_id: 'B11-EN', question: 'How to drop subjects?' }, { case_id: 'B11-TL', question: 'Paano mag-drop ng subject?' }];
const run = (run_id, case_id, outcome = 'completed', judgment = null) => ({ run_id, case_id, outcome, judgment });

test('matchCase ignores spacing and case but not a different word', () => {
  assert.equal(matchCase('  how to  DROP subjects? ', cases).case_id, 'B11-EN');
  assert.equal(matchCase('How to drop subject?', cases), null);
  assert.equal(matchCase('', cases), null);
});

test('the first completed run counts, matching the scorer', () => {
  const runs = [run('r1', 'B11-EN', 'infrastructure_error'), run('r2', 'B11-EN'), run('r3', 'B11-EN')];
  assert.equal(countedRunId('B11-EN', runs), 'r2');
  assert.equal(countedRunId('B11-TL', runs), null);
});

test('each case shows whether it still needs running or marking', () => {
  const runs = [run('r1', 'B11-EN', 'infrastructure_error'), run('r2', 'B11-TL'), run('r3', null)];
  assert.deepEqual(caseStatuses(cases, runs), { 'B11-EN': 'failed', 'B11-TL': 'needs_marks' });
  const marked = [run('r4', 'B11-EN', 'completed', { answer_mark: 'correct', chunk_marks: {} })];
  assert.deepEqual(caseStatuses(cases, marked), { 'B11-EN': 'marked', 'B11-TL': 'not_run' });
});

test('a later failure does not hide an earlier counted run', () => {
  const runs = [run('r1', 'B11-EN', 'completed', { answer_mark: 'wrong', chunk_marks: {} }), run('r2', 'B11-EN', 'infrastructure_error')];
  assert.equal(caseStatuses(cases, runs)['B11-EN'], 'marked');
});

test('progress counts cases, not extra runs', () => {
  const runs = [run('r1', 'B11-EN', 'completed', { answer_mark: 'correct', chunk_marks: {} }), run('r2', 'B11-EN')];
  assert.deepEqual(progress(cases, runs), { ran: 1, marked: 1, total: 2 });
});

test('a judgment without an answer mark is not counted as marked', () => {
  const runs = [run('r1', 'B11-EN', 'completed', { answer_mark: null, chunk_marks: { a: true } })];
  assert.equal(caseStatuses(cases, runs)['B11-EN'], 'needs_marks');
});

function recording(response = { ok: true }, status = 200) {
  const calls = [];
  return { calls, fetch: async (url, init) => { calls.push({ url, init }); return Response.json(response, { status }); } };
}

test('every call goes through the proxy with the passcode header', async () => {
  const { calls, fetch } = recording();
  await loadCases('pass', fetch);
  await listRuns('pass', fetch);
  await runEvaluation('How to drop subjects?', 'pass', fetch);
  await saveJudgment('run-1', { chunk_marks: { a: true }, answer_mark: 'correct', note: '' }, 'pass', fetch);
  assert.deepEqual(calls.map(c => c.url), ['/api/evaluation/cases', '/api/evaluation/runs', '/api/evaluation/run', '/api/evaluation/runs/run-1/judgment']);
  for (const call of calls) assert.equal(call.init.headers['x-bintanong-evaluator'], 'pass');
  assert.deepEqual(JSON.parse(calls[2].init.body), { question: 'How to drop subjects?' });
});

test('a refused call reports its code instead of looking empty', async () => {
  const { fetch } = recording({ error: 'route_unavailable' }, 404);
  await assert.rejects(loadCases('wrong', fetch), { message: 'route_unavailable' });
});

const base = 'https://bintanong.example';
const options = (seen) => ({ baseUrl: 'http://127.0.0.1:8021', accessToken: null, siteOrigin: base, fetch: async (url, init) => {
  seen.push({ url: String(url), headers: init.headers });
  return Response.json({ ok: true });
} });
const proxied = (path, method, headers = {}) => new Request(base + '/api' + path, { method,
  headers: { Origin: base, ...headers }, ...(method === 'POST' ? { body: '{}' } : {}) });

for (const [path, method] of [['/evaluation/cases', 'GET'], ['/evaluation/runs', 'GET'], ['/evaluation/run', 'POST'],
  ['/evaluation/ablation', 'GET'], ['/evaluation/ablation', 'POST'],
  ['/evaluation/runs/run-0123456789abcdef/judgment', 'POST']]) {
  test(`proxy forwards the passcode on ${method} ${path}`, async () => {
    const seen = [];
    const response = await forwardStudentRequest(proxied(path, method, { 'x-bintanong-evaluator': 'pass' }), path, options(seen));
    assert.equal(response.status, 200);
    assert.equal(seen[0].headers.get('x-bintanong-evaluator'), 'pass');
  });
}

test('proxy never forwards the passcode to the student chat', async () => {
  const seen = [];
  await forwardStudentRequest(proxied('/chat', 'POST', { 'x-bintanong-evaluator': 'pass' }), '/chat', options(seen));
  assert.equal(seen[0].headers.has('x-bintanong-evaluator'), false);
});

test('proxy refuses other evaluation paths and wrong methods', async () => {
  const seen = [];
  assert.equal((await forwardStudentRequest(proxied('/evaluation/secret', 'GET'), '/evaluation/secret', options(seen))).status, 404);
  assert.equal((await forwardStudentRequest(proxied('/evaluation/runs/../x/judgment', 'POST'), '/evaluation/runs/../x/judgment', options(seen))).status, 404);
  assert.equal((await forwardStudentRequest(proxied('/evaluation/cases', 'POST'), '/evaluation/cases', options(seen))).status, 405);
  assert.equal(seen.length, 0);
});
