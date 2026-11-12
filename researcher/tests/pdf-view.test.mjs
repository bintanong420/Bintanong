import assert from 'node:assert/strict';
import test from 'node:test';
import { knowledgePdfPath, pdfAtPage, sourcePdfPath } from '../lib/pdf-view.ts';
import { chunkMeta } from '../lib/knowledge.ts';
import { proxyResponseHeaders } from '../lib/review-proxy.ts';
import config from '../next.config.mjs';

test('the full PDF opens at the record page through the existing identifiers only', () => {
  assert.equal(sourcePdfPath('handbook/../x'), '/api/source/handbook%2F..%2Fx');
  assert.equal(knowledgePdfPath('a'.repeat(64)), '/api/knowledge/pdf?sha256=' + 'a'.repeat(64));
  assert.equal(pdfAtPage('/review/api/source/h', 7), '/review/api/source/h#page=7');
  for (const bad of [0, -2, 1.5, NaN]) assert.equal(pdfAtPage('/review/api/source/h', bad), '/review/api/source/h#page=1');
});

test('the review proxy passes an inline disposition and nothing that names a download', () => {
  const pass = value => proxyResponseHeaders(new Headers({ 'content-type': 'application/pdf', 'content-disposition': value }));
  assert.deepEqual(pass('inline'), { 'content-type': 'application/pdf', 'cache-control': 'no-store', 'content-disposition': 'inline' });
  for (const value of ['attachment', 'inline; filename="../secret.pdf"', 'INLINE ', 'attachment; filename=x.pdf']) {
    assert.equal(pass(value)['content-disposition'], undefined, value);
  }
});

test('only the PDF routes may be framed, and only by this origin', async () => {
  const rules = await config.headers();
  const csp = source => rules.filter(rule => rule.source === '/:path*' || rule.source === source).at(-1)
    .headers.find(header => header.key === 'Content-Security-Policy').value;
  assert.match(csp('/review/api/source/:identity'), /frame-ancestors 'self'/);
  assert.match(csp('/review/api/knowledge/pdf'), /frame-ancestors 'self'/);
  const page = rules.find(rule => rule.source === '/:path*').headers.find(header => header.key === 'Content-Security-Policy').value;
  assert.match(page, /frame-ancestors 'none'/);
  for (const rule of rules) assert.doesNotMatch(JSON.stringify(rule), /frame-ancestors \*|X-Frame-Options.*ALLOW/i);
});

test('chunk metadata leaves out empty values instead of showing a bare label', () => {
  assert.deepEqual(chunkMeta({ document_title: 'Charter.pdf', section: null, pages: [66, 67] }),
    [['Document', 'Charter.pdf'], ['Pages', '66, 67']]);
  assert.deepEqual(chunkMeta({ document_title: '  ', section: '   ', pages: [] }), []);
  assert.deepEqual(chunkMeta({ section: 'Part I' }), [['Section', 'Part I']]);
});
