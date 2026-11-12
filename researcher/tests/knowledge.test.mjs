import assert from 'node:assert/strict';
import test from 'node:test';
import { chunkCountText, chunksQuery, documentChipLabel, documentLink, documentsPath, knowledgeUrl, libraryGroups,
  pageRangeText, parseKnowledgeUrl, pdfText, snippet } from '../lib/knowledge.ts';

test('the document filter lives in the address and the chunk query', () => {
  const state = parseKnowledgeUrl('?source=hosted:r1&document=Handbook%20%282026%29&offset=20');
  assert.deepEqual(state, { source: 'hosted:r1', q: '', chunk: '', document: 'Handbook (2026)', offset: 20 });
  assert.equal(parseKnowledgeUrl('').document, '');
  assert.deepEqual(parseKnowledgeUrl(knowledgeUrl(state).split('?')[1]), state);
  assert.equal(knowledgeUrl({ source: 's', q: '', chunk: '', document: '', offset: 0 }), '/review/knowledge?source=s');
  const query = new URLSearchParams(chunksQuery({ source: 'local:r', q: '', document: 'a'.repeat(64), offset: 0, limit: 20 }));
  assert.equal(query.get('document'), 'a'.repeat(64));
  assert.equal(new URLSearchParams(chunksQuery({ source: 'local:r', q: '', document: '', offset: 0, limit: 20 })).has('document'), false);
});

test('library groups put the online release first and hide empty groups', () => {
  const groups = libraryGroups([{ id: 'package:1', kind: 'package', label: 'P' }, { id: 'local:a', kind: 'local', label: 'L' },
    { id: 'hosted:h', kind: 'hosted', label: 'H', active: true }, { id: 'x:1', kind: 'x', label: 'X' }]);
  assert.deepEqual(groups.map(g => g.heading), ['Online knowledge (read-only)', 'Local copy on this computer', 'Built packages', 'Other sources']);
  assert.deepEqual(libraryGroups([{ id: 'local:a', kind: 'local', label: 'L' }]).map(g => g.kind), ['local']);
  assert.deepEqual(libraryGroups([]), []);
});

test('document rows read in plain words', () => {
  assert.equal(chunkCountText(1), '1 chunk');
  assert.equal(chunkCountText(0), '0 chunks');
  assert.equal(chunkCountText(1204), '1,204 chunks');
  assert.equal(pageRangeText([]), 'No page reference');
  assert.equal(pageRangeText([4, 4]), 'Page 4');
  assert.equal(pageRangeText([2, 18]), 'Pages 2 to 18');
  assert.equal(pdfText({ pdf_available: true, source_sha256: 'a'.repeat(64) }), 'PDF on this machine');
  assert.equal(pdfText({ pdf_available: false, source_sha256: 'a'.repeat(64) }), 'PDF not on this machine');
  assert.equal(pdfText({ pdf_available: false }), 'No source PDF recorded');
});

test('links and paths keep the source and document intact', () => {
  assert.equal(documentsPath('hosted:rel 1'), '/api/knowledge/documents?source=hosted%3Arel+1');
  const link = documentLink('local:r1', { document_key: 'Title & more', title: 'Title & more', chunk_count: 1, pages: [], pdf_available: false });
  assert.equal(link, '/review/knowledge?source=local%3Ar1&document=Title+%26+more');
  assert.equal(documentChipLabel('Plain title', []), 'Plain title');
  assert.equal(documentChipLabel('b'.repeat(64), [{ document_title: 'Handbook' }]), 'Handbook');
  assert.equal(documentChipLabel('b'.repeat(64), []), 'Untitled document (bbbbbbbb)');
});

test('previews prefer readable prose and stay short', () => {
  assert.equal(snippet({ text: '{\"fields\":[]}', display_text: 'Title: Shifting' }), 'Title: Shifting');
  assert.equal(snippet({ text: 'a\n  b' }), 'a b');
  assert.equal(snippet({ text: 'x'.repeat(200) }).length, 140);
});


import { chunkText, documentTitle, groupLabel } from '../lib/knowledge.ts';
import { pageNav } from '../lib/compare.ts';
import { proxyResponseHeaders } from '../lib/review-proxy.ts';

test('a document with no title still gets a readable name', () => {
  assert.equal(documentTitle({ title: '  ', document_key: 'a'.repeat(64) }), 'Untitled document (aaaaaaaa)');
  assert.equal(documentTitle({ title: '', document_key: 'Some key' }), 'Untitled document (Some key)');
  assert.equal(documentTitle({ title: 'Handbook', document_key: 'a'.repeat(64) }), 'Handbook');
  assert.equal(documentChipLabel('b'.repeat(64), []), 'Untitled document (bbbbbbbb)');
});

test('readable text always beats the raw payload', () => {
  assert.equal(chunkText({ text: '{"fields":[]}', display_text: 'Title: A' }), 'Title: A');
  assert.equal(chunkText({ text: 'plain', display_text: null }), 'plain');
  assert.equal(chunkText({ text: 'plain' }), 'plain');
});

test('source groups use everyday names and keep the technical name small', () => {
  assert.deepEqual(groupLabel('hosted'), { heading: 'Online knowledge (read-only)', note: 'Hosted database' });
  assert.deepEqual(groupLabel('local'), { heading: 'Local copy on this computer', note: 'Local Supabase' });
  assert.deepEqual(groupLabel('package'), { heading: 'Built packages', note: '' });
});

test('page buttons stop at both ends of the PDF', () => {
  assert.deepEqual(pageNav(1, 1), { prevDisabled: true, nextDisabled: true });
  assert.deepEqual(pageNav(1, 3), { prevDisabled: true, nextDisabled: false });
  assert.deepEqual(pageNav(3, 3), { prevDisabled: false, nextDisabled: true });
  assert.deepEqual(pageNav(2, 0), { prevDisabled: false, nextDisabled: false });  // count unknown until the first page loads
});

test('the review proxy passes only the headers a page image needs', () => {
  const upstream = new Headers({ 'content-type': 'image/png', 'cache-control': 'private, max-age=300', 'x-page-count': '12', 'set-cookie': 'a=b', 'x-review-token': 't' });
  assert.deepEqual(proxyResponseHeaders(upstream), { 'content-type': 'image/png', 'cache-control': 'private, max-age=300', 'x-page-count': '12' });
  assert.equal(proxyResponseHeaders(new Headers({ 'cache-control': 'public, max-age=999999' }))['cache-control'], 'no-store');
  assert.equal(proxyResponseHeaders(new Headers({ 'cache-control': 'private, max-age=300, no-store' }))['cache-control'], 'no-store');
  assert.equal(proxyResponseHeaders(new Headers({ 'x-page-count': 'abc' }))['x-page-count'], undefined);
  assert.equal(proxyResponseHeaders(new Headers())['content-type'], 'application/octet-stream');
});

test('the review proxy keeps the page geometry the source viewer needs for highlight boxes', () => {
  const upstream = new Headers({ 'content-type': 'image/png', 'x-page-count': '3', 'x-page-width': '612.0',
    'x-page-height': '792', 'x-page-rotation': '90' });
  const passed = proxyResponseHeaders(upstream);
  assert.equal(passed['x-page-width'], '612.0');
  assert.equal(passed['x-page-height'], '792');
  assert.equal(passed['x-page-rotation'], '90');
  assert.equal(proxyResponseHeaders(new Headers({ 'x-page-width': '1e9; evil' }))['x-page-width'], undefined);
  // the API sends Python floats verbatim, e.g. an A4 page width
  assert.equal(proxyResponseHeaders(new Headers({ 'x-page-width': '595.2755905511812' }))['x-page-width'], '595.2755905511812');
});
