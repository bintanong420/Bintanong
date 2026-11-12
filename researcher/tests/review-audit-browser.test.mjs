import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import test from 'node:test';

const origin = process.env.BINTANONG_AUDIT_TEST_ORIGIN;
const runtime = process.env.BINTANONG_TEST_PLAYWRIGHT;
test('Gemma audit keeps edits untouched until the reviewer uses the source-bound suggestion',
  { skip: !origin || !runtime, timeout: 90000 }, async t => {
    assert.match(origin, /^http:\/\/127\.0\.0\.1:\d+$/);
    const { chromium } = await import(pathToFileURL(runtime).href);
    const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
    t.after(() => browser.close());
    const page = await browser.newPage();
    const field = { name: 'body', original_value: 'Submit form.', reviewed_value: 'Submit form.', decision: 'pending',
      source_blank: false, locator: { physical_pages: [1], field: 'body' }, spans: [] };
    const item = { id: 'item-1', document_id: 'document-1', title: 'Synthetic policy', audience: 'unresolved',
      findings: [], companions: [], fields: [field], reason: '', gaps: [] };
    const state = { packet_id: 'packet-1', revision: 0, items: [item],
      documents: [{ id: 'document-1', sha256: 'a'.repeat(64), title: 'Synthetic', kind: 'handbook', edition: '2026' }], researcher: 'Synthetic' };
    let release, started, decisions = 0, unavailable = false;
    const firstRequest = new Promise(resolve => { started = resolve; });
    await page.route('**/review/api/**', async route => {
      const pathname = new URL(route.request().url()).pathname;
      if (pathname.endsWith('/intake/current')) return route.fulfill({ json: { upload_id: 'synthetic' } });
      if (pathname.endsWith('/state')) return route.fulfill({ json: state });
      if (pathname.includes('/page/')) return route.fulfill({ status: 422, json: { error: 'Synthetic page display omitted' } });
      if (pathname.endsWith('/decision')) { decisions++; return route.fulfill({ status: 500 }); }
      if (pathname.endsWith('/audit')) {
        assert.deepEqual(route.request().postDataJSON(), { packet_id: 'packet-1', revision: 0, item_id: 'item-1', field: 'body' });
        if (unavailable) return route.fulfill({ status: 503, json: { error: 'Gemma unavailable; review manually.' } });
        await new Promise(resolve => { release = resolve; started(); });
        return route.fulfill({ json: { packet_id: 'packet-1', revision: 0, item_id: 'item-1', field: {
          ...field, proposed_value: 'Keep the printed form.', assistance: { outcome: 'proposal', rationale: 'Compare the original.',
            provider: 'synthetic', model: 'Gemma test', binding: { source_sha256: 'a'.repeat(64), item_id: 'item-1',
              field: 'body', pages: [1], original_value: 'Submit form.' } } } } });
      }
      throw Error('Unexpected review request: ' + pathname);
    });
    await page.goto(origin + '/review');
    const audit = page.getByRole('button', { name: 'Audit with Gemma', exact: true });
    await audit.click();
    await firstRequest;
    assert(await page.getByRole('button', { name: 'Auditing with Gemma…', exact: true }).isDisabled());
    await page.getByLabel('Review reason').fill('My own note.');
    release();
    await page.getByText('Gemma audit ready. It has not changed your review.', { exact: true }).waitFor();
    assert.equal(await page.getByLabel('Review reason').inputValue(), 'My own note.');
    assert.equal(await page.locator('.rw-choice input:checked').count(), 0);
    await page.getByRole('button', { name: 'Use as my correction', exact: true }).click();
    assert.equal(await page.getByLabel('body reviewed value').inputValue(), 'Keep the printed form.');
    assert.equal(decisions, 0);
    unavailable = true;
    await audit.click();
    await page.getByText('Gemma unavailable; review manually.', { exact: true }).waitFor();
    assert.equal(await page.getByLabel('body reviewed value').inputValue(), 'Keep the printed form.');
    assert.equal(decisions, 0);
  });
