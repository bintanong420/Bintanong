import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { sendStudentMessage, uploadStudentFile } from '../lib/student-transport.ts';

const request = { id: 'msg-test', text: 'A synthetic question', programId: 'program-a', curriculumId: 'curriculum-a' };
const sse = parts => parts.map(part => 'data: ' + JSON.stringify(part) + '\n\n').join('') + 'data: [DONE]\n\n';
const normal = [
  { type: 'start', messageId: 'msg-answer' },
  { type: 'text-start', id: 'text-answer' },
  { type: 'text-delta', id: 'text-answer', delta: 'Synthetic response.' },
  { type: 'text-end', id: 'text-answer' },
  { type: 'data-answer', data: { status: 'answered', conditional: false, language: 'en', missingFields: [] } },
  { type: 'finish', finishReason: 'stop' },
];
function response(raw) { return new Response(raw, { headers: { 'Content-Type': 'text/event-stream', 'x-vercel-ai-ui-message-stream': 'v1' } }); }

test('installed SDK parses actual Python answer stream, queue status and sources', async () => {
  const raw = execFileSync('py', ['-3.13', '-B', new URL('../../tests/export_student_stream.py', import.meta.url).pathname.replace(/^\//, '')], { encoding: 'utf8' });
  const progress = [], text = [];
  const answer = await sendStudentMessage(request, { signal: new AbortController().signal, onText: t => text.push(t), onProgress: p => progress.push(p),
    fetch: async (_url, init) => {
      const body = JSON.parse(init.body);
      assert.deepEqual(body.messages, [{ id: request.id, role: 'user', parts: [{ type: 'text', text: request.text }] }]);
      assert.equal(body.curriculumId, request.curriculumId);
      return response(raw);
    } });
  assert.equal(answer.status, 'answered');
  assert.equal(answer.conditional, true);
  assert.ok(answer.sources.length > 0);
  assert.deepEqual(progress, ['waiting']);
  assert.equal(text.join(''), answer.text);
  assert.ok(!answer.text.includes('ev-'));
});

test('missing final summary or finish never becomes a completed answer', async () => {
  for (const parts of [normal.filter(p => p.type !== 'data-answer'), normal.slice(0, -1)]) {
    await assert.rejects(sendStudentMessage(request, { signal: new AbortController().signal, onText() {}, fetch: async () => response(sse(parts)) }), /incomplete_response/);
  }
});

test('typed backend errors are preserved and untrusted errors are hidden', async () => {
  for (const [raw, expected] of [[{ error: 'answers_busy' }, 'answers_busy'], [{ error: 'secret with spaces' }, 'request_failed']]) {
    await assert.rejects(sendStudentMessage(request, { signal: new AbortController().signal, onText() {}, fetch: async () => Response.json(raw, { status: 503 }) }), new RegExp(expected));
  }
});

test('stream failure never resubmits a possibly committed answer', async () => {
  let calls = 0;
  await assert.rejects(sendStudentMessage(request, { signal: new AbortController().signal, onText() {}, fetch: async () => { calls++; return response(sse([{ type: 'error', errorText: 'already_answered' }])); } }), /already_answered/);
  assert.equal(calls, 1);
});

test('PDF upload uses explicit scope and preserves backend review shape', async () => {
  const file = new File(['%PDF-synthetic'], 'synthetic.pdf', { type: 'application/pdf' });
  const review = { uploadId: 'upl-0123456789abcdef', unmatchedLines: 0, rows: [{ rowId: 'row-1-1', printedCode: 'A1', marks: [], courses: [{ courseId: 'course-a', label: 'A1' }] }] };
  let queryKeys;
  const value = await uploadStudentFile(file, request, new AbortController().signal, async (url, init) => {
    assert.ok(url.includes('programId=program-a') && url.includes('curriculumId=curriculum-a'));
    queryKeys = [...new URL(url, 'https://synthetic.example').searchParams.keys()].sort();
    assert.equal(init.body, file);
    return Response.json(review);
  });
  assert.deepEqual(value, review);
  assert.deepEqual(queryKeys, ['curriculumId', 'programId']);
});
