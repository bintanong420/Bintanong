import assert from 'node:assert/strict';
import test from 'node:test';
import { chunkCountText, chunksQuery, documentChipLabel, documentLink, documentsPath, knowledgeUrl, libraryGroups,
  pageRangeText, parseKnowledgeUrl, pdfText } from '../lib/knowledge.ts';

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
  assert.deepEqual(groups.map(g => g.heading), ['Online (read-only)', 'Local Supabase', 'Built packages', 'Other sources']);
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
  assert.equal(documentChipLabel('b'.repeat(64), []), 'Document bbbbbbbb');
});
