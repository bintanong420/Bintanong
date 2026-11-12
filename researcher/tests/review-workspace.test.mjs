import assert from 'node:assert/strict';
import test from 'node:test';
import { SECTIONS, prospectusDocuments, reviewSection } from '../lib/review-nav.ts';
import { chunksQuery, groupSources, knowledgeUrl, pageImagePath, pageWindow, parseKnowledgeUrl, packageSourceId } from '../lib/knowledge.ts';
import { clampPage, itemsOnPage, pagesOf } from '../lib/compare.ts';
import { buildChecklist, buildControl, buildLabel, buildSummary, opensMetadataForm, INTERRUPTED_NOTE, pipelineSteps, REBUILD_NOTE, shouldPollBuild } from '../lib/intake.ts';

test('the current section follows the address and keeps every old review URL under Documents or Prospectus', () => {
  assert.deepEqual(SECTIONS.map(s => s.href), ['/review/intake', '/review', '/review/prospectus', '/review/knowledge']);
  assert.equal(reviewSection('/review'), 'documents');
  assert.equal(reviewSection('/review/'), 'documents');
  assert.equal(reviewSection('/review/policy/handbook%3Agrading'), 'documents');
  assert.equal(reviewSection('/review/intake'), 'intake');
  assert.equal(reviewSection('/review/prospectus'), 'prospectus');
  assert.equal(reviewSection('/review/prospectus/bscs/S1-01'), 'prospectus');
  assert.equal(reviewSection('/review/knowledge'), 'knowledge');
  assert.equal(reviewSection('/review/intakex'), 'documents');
  assert.equal(reviewSection('/chat'), null);
});

test('prospectus documents come from candidate records only, with a record count', () => {
  const state = { documents: [{ id: 'h', title: 'Handbook', edition: '2024' }, { id: 'b', title: 'BSCS', edition: '2018' }, { id: 'e', title: 'Empty', edition: '1' }],
    items: [{ document_id: 'h' }, { document_id: 'b', prospectus_candidate: {} }, { document_id: 'b', prospectus_candidate: {} }] };
  assert.deepEqual(prospectusDocuments(state), [{ id: 'b', title: 'BSCS', edition: '2018', records: 2 }]);
  assert.deepEqual(prospectusDocuments({ documents: [], items: [] }), []);
});

test('knowledge URL state round-trips and drops empty values', () => {
  assert.deepEqual(parseKnowledgeUrl(''), { source: '', q: '', chunk: '', document: '', offset: 0 });
  assert.deepEqual(parseKnowledgeUrl('?source=package%3Aup-1&q=grade+scale&chunk=c%2F1&offset=40'),
    { source: 'package:up-1', q: 'grade scale', chunk: 'c/1', document: '', offset: 40 });
  assert.deepEqual(parseKnowledgeUrl('?offset=-3').offset, 0);
  assert.deepEqual(parseKnowledgeUrl('?offset=abc').offset, 0);
  assert.equal(knowledgeUrl({ source: '', q: '', chunk: '', document: '', offset: 0 }), '/review/knowledge');
  const state = { source: 'package:up-1', q: 'grade scale', chunk: 'c/1', document: '', offset: 40 };
  assert.deepEqual(parseKnowledgeUrl(knowledgeUrl(state).split('?')[1]), state);
  assert.equal(knowledgeUrl({ source: packageSourceId('up 1'), q: '', chunk: '', document: '', offset: 0 }), '/review/knowledge?source=package%3Aup+1');
});

test('chunk queries carry the source, trimmed search, offset and limit', () => {
  assert.equal(chunksQuery({ source: 'local', q: '  late  ', offset: 20, limit: 20 }), 'source=local&q=late&offset=20&limit=20');
  assert.equal(chunksQuery({ source: 'local', q: '', offset: 0, limit: 20 }), 'source=local&offset=0&limit=20');
});

test('sources are grouped package, local, hosted, with the hosted group marked read-only', () => {
  const groups = groupSources([{ id: 'h1', kind: 'hosted', label: 'Hosted' }, { id: 'package:a', kind: 'package', label: 'A' },
    { id: 'l', kind: 'local', label: 'Local' }, { id: 'package:b', kind: 'package', label: 'B' }]);
  assert.deepEqual(groups.map(g => g.kind), ['package', 'local', 'hosted']);
  assert.deepEqual(groups[0].sources.map(s => s.id), ['package:a', 'package:b']);
  assert.equal(groups[2].heading, 'Online knowledge (read-only)');
  assert.deepEqual(groupSources([]), []);
  // an unknown kind is kept visible, not dropped
  assert.equal(groupSources([{ id: 'x', kind: 'mystery', label: 'X' }]).length, 1);
});

test('paging reports the visible range and the neighbouring offsets', () => {
  assert.deepEqual(pageWindow(95, 0, 20), { from: 1, to: 20, total: 95, page: 1, pages: 5, prev: null, next: 20 });
  assert.deepEqual(pageWindow(95, 80, 20), { from: 81, to: 95, total: 95, page: 5, pages: 5, prev: 60, next: null });
  assert.deepEqual(pageWindow(0, 0, 20), { from: 0, to: 0, total: 0, page: 1, pages: 1, prev: null, next: null });
  assert.equal(pageWindow(95, 30, 20).page, 2);  // an offset that is not a page boundary still lands on a page
});

test('page image URLs are encoded and the scale is optional', () => {
  assert.equal(pageImagePath('ab12', 3), '/api/knowledge/page?sha256=ab12&page=3');
  assert.equal(pageImagePath('ab12', 3, 1.5), '/api/knowledge/page?sha256=ab12&page=3&scale=1.5');
});

test('extracted items group by the pages they cite', () => {
  const items = [
    { id: 'a', title: 'Grading', fields: [{ name: 'rule', original_value: 'x', locator: { physical_pages: [2, 3] } }, { name: 'note', original_value: 7, locator: { physical_pages: [3] } }] },
    { id: 'b', fields: [{ name: 'blank', original_value: null, locator: { physical_pages: [] } }, { name: 'p1', original_value: ['r1', 'r2'], locator: { physical_pages: [1] } }] }];
  assert.deepEqual(pagesOf(items), [1, 2, 3]);
  const three = itemsOnPage(items, 3);
  assert.deepEqual(three.map(r => [r.itemId, r.fieldName, r.text]), [['a', 'rule', 'x'], ['a', 'note', '7']]);
  assert.deepEqual(itemsOnPage(items, 1).map(r => r.text), ['r1\nr2']);
  assert.deepEqual(itemsOnPage(items, 9), []);
  assert.equal(itemsOnPage(items, 2)[0].itemTitle, 'Grading');
  assert.equal(itemsOnPage(items, 1)[0].itemTitle, 'b');  // falls back to the id
  assert.deepEqual(pagesOf([]), []);
});

test('page navigation stays inside the document', () => {
  assert.equal(clampPage(0, 10), 1);
  assert.equal(clampPage(11, 10), 10);
  assert.equal(clampPage(4.7, 10), 4);
  assert.equal(clampPage(Number.NaN, 10), 1);
  assert.equal(clampPage(5, 0), 5);  // count unknown until the first image loads
});

test('the Build step is words as well as status, and reflects the build job', () => {
  const by = (prepare, open, build) => Object.fromEntries(pipelineSteps(prepare, open, build).map(s => [s.key, s]));
  assert.deepEqual(pipelineSteps('running', false).map(s => s.key), ['upload', 'prepare', 'review', 'build']);
  assert.equal(by('running', false).build.status, 'blocked');
  assert.equal(by('done', false).build.status, 'todo');
  assert.equal(by('done', true, { state: 'running' }).build.status, 'active');
  assert.equal(by('done', true, { state: 'failed' }).build.status, 'failed');
  assert.equal(by('done', true, { state: 'interrupted' }).build.status, 'failed');
  const built = by('done', true, { state: 'done', package: { package_id: 'p', chunk_count: 12 } }).build;
  assert.equal(built.status, 'done');
  assert.match(built.text, /12 chunks/);
  assert.equal(by('done', true, { state: 'done' }).build.text, 'Built');
  assert.match(buildSummary({ state: 'done', package: { package_id: 'p', chunk_count: 1 } }), /^Built 1 chunk$/);
  assert.equal(buildSummary({ state: 'running' }), '');
  assert.equal(shouldPollBuild('running'), true);
  assert.equal(shouldPollBuild('done'), false);
  assert.equal(shouldPollBuild(undefined), false);
  assert.match(buildLabel('interrupted'), /restarted/);
  assert.equal(buildLabel('weird'), 'Unknown state');
});

test('the API client keeps the server message and its machine-readable code', async () => {
  const { request, ReviewError } = await import('../lib/api.ts');
  const original = globalThis.fetch;
  try {
    globalThis.fetch = async () => new Response(JSON.stringify({ error: 'A package already exists.', code: 'package_exists' }), { status: 409 });
    await assert.rejects(request({ api: '/review' }, '/api/intake/build'), error => {
      assert.ok(error instanceof ReviewError);
      assert.equal(error.message, 'A package already exists.');
      assert.equal(error.status, 409);
      assert.equal(error.code, 'package_exists');
      return true;
    });
    globalThis.fetch = async () => new Response('not json', { status: 503 });
    await assert.rejects(request({ api: '/review' }, '/x'), error => error.code === undefined && /503/.test(error.message));
  } finally { globalThis.fetch = original; }
});

test('Build offers one start, only a retry after a failure, and nothing after success', () => {
  assert.deepEqual(buildControl(true, undefined), { kind: 'start', label: 'Build chunks' });
  assert.deepEqual(buildControl(false, undefined), { kind: 'start', label: 'Build chunks' });
  assert.equal(buildControl(true, { state: 'running' }).kind, 'running');
  assert.deepEqual(buildControl(true, { state: 'failed' }), { kind: 'retry', label: 'Try the build again' });
  assert.deepEqual(buildControl(true, { state: 'interrupted' }), { kind: 'none', label: '' });  // the old process may still be running
  assert.match(INTERRUPTED_NOTE, /may still be running.*new upload/);
  assert.equal(buildControl(true, { state: 'done' }).kind, 'none');
  assert.match(REBUILD_NOTE, /needs a new upload/);
});

test('the pre-build checklist and the refusal codes', () => {
  assert.deepEqual(buildChecklist(true).map(row => [row.key, row.status]), [['prepared', 'done'], ['form', 'unknown']]);
  assert.equal(buildChecklist(false)[0].status, 'blocked');
  assert.match(buildChecklist(true, false)[1].text, /Save the passages and claims form first/);
  assert.equal(opensMetadataForm('metadata_missing'), true);
  for (const code of ['not_prepared', 'package_exists', 'build_running', 'model_dir_missing', 'interpreter_missing', undefined]) assert.equal(opensMetadataForm(code), false);
});

import { itemSnippet } from '../lib/review-state.ts';
test('queue rows tell same-titled items apart by their first words', () => {
  const a = { fields: [{ name: 'service_name', original_value: 'Shifting of programs   from one college to another, in the same semester' }] };
  assert.match(itemSnippet(a), /^Service name: Shifting of programs from one college/);
  assert.ok(itemSnippet(a).length <= 84);
  assert.equal(itemSnippet({ fields: [{ name: 'x', original_value: '' }, { name: 'fee', original_value: ['Pay 50', 'at cashier'] }] }), 'Fee: Pay 50 at cashier');
  assert.equal(itemSnippet({ fields: [] }), '');
});

