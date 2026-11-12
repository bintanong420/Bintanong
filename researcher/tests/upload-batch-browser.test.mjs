import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import test from 'node:test';

// Opt-in with an existing Playwright installation and a preview server. All API calls are intercepted; no real uploads.
const origin = process.env.BINTANONG_INTAKE_TEST_ORIGIN;
const runtime = process.env.BINTANONG_TEST_PLAYWRIGHT;
const enabled = Boolean(origin && runtime);
const file = name => ({ name, mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4 synthetic ' + name) });

test('Intake sends files sequentially, preserves Stop, and confirms uncertain retries', { skip: !enabled, timeout: 120000 }, async t => {
  assert.match(origin, /^http:\/\/127\.0\.0\.1:\d+$/);
  const { chromium } = await import(pathToFileURL(runtime).href);
  const browser = await chromium.launch({ executablePath: process.env.BINTANONG_REVIEW_TEST_CHROME
    ?? 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
  t.after(() => browser.close());
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [], sentTypes = [];
  page.on('pageerror', error => errors.push(error.message));
  let mode = 'stop', count = 0, release, started, uploads = [];
  let firstRequest = new Promise(resolve => { started = resolve; });
  await page.route('**/review/api/**', async route => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith('/intake/upload')) {
      sentTypes.push(route.request().headers()['content-type']);
      count++;
      if (mode === 'stop') {
        if (count === 1) return route.fulfill({ status: 400, json: { error: 'Synthetic refusal' } });
        await new Promise(resolve => { release = resolve; started(); });
      } else if (mode === 'uncertain') return route.abort('connectionreset');
      const upload_id = 'synthetic-' + count;
      uploads.push({ upload_id, title: url.searchParams.get('title'), edition: '2026', kind: 'handbook', bytes: 50, sha256: 'a'.repeat(64) });
      return route.fulfill({ json: { upload_id } });
    }
    if (url.pathname.endsWith('/uploads')) return route.fulfill({ json: { uploads } });
    if (url.pathname.endsWith('/current')) return route.fulfill({ json: { upload_id: null } });
    if (route.request().method() === 'GET' && /\/intake\/(prepare|build)\//.test(url.pathname))
      return route.fulfill({ json: { state: 'not_started' } });
    throw Error('Unexpected API call: ' + route.request().method() + ' ' + url.pathname);
  });
  await page.goto(origin + '/review/intake');
  await page.getByText('No uploads yet', { exact: true }).waitFor();
  await page.locator('input[type=file]').setInputFiles([file('one_2026.pdf'),
    { ...file('two_2026.png'), mimeType: 'image/png' }, { ...file('three_2026.webp'), mimeType: 'image/webp' }]);
  await page.getByRole('button', { name: 'Upload 3 documents', exact: true }).click();
  await firstRequest;
  assert.equal(count, 2, 'third request must wait for the second response');
  assert(await page.getByRole('button', { name: 'Retry one_2026.pdf', exact: true }).isDisabled(), 'retry must stay disabled during the batch');
  await page.getByRole('button', { name: 'Stop after this file', exact: true }).click();
  release();
  await page.getByText('1 uploaded, 1 failed, 1 not sent.', { exact: true }).waitFor();
  assert(await page.getByRole('button', { name: 'Retry three_2026.webp', exact: true }).isVisible(), 'the first uploaded file must not collapse the batch');
  assert.equal(count, 2);
  mode = 'success';
  await page.getByRole('button', { name: 'Retry three_2026.webp', exact: true }).click();
  await page.getByText('2 uploaded, 1 failed.', { exact: true }).waitFor();
  assert.equal(count, 3, 'a row retry sends only that row');
  assert.deepEqual(sentTypes, ['application/pdf', 'image/png', 'image/webp']);

  mode = 'uncertain'; count = 0; uploads = [];
  await page.reload();
  await page.getByText('No uploads yet', { exact: true }).waitFor();
  await page.locator('input[type=file]').setInputFiles(file('lost_2026.pdf'));
  await page.getByRole('button', { name: 'Upload document', exact: true }).click();
  await page.getByText('1 failed.', { exact: true }).waitFor();
  assert.match(await page.locator('.batch-row').innerText(), /may already be saved/);
  let dialogs = 0;
  page.on('dialog', async dialog => { dialogs++; assert.match(dialog.message(), /duplicate/); await dialog.dismiss(); });
  await page.getByRole('button', { name: 'Retry lost_2026.pdf', exact: true }).click();
  await page.getByRole('button', { name: 'Upload 1 unfinished', exact: true }).click();
  assert.equal(dialogs, 2);
  assert.equal(count, 1, 'dismissed confirmations must not resend a potentially saved file');

  // The real form, long names, both themes and mobile reflow; no screenshot is required to run the regression.
  await page.reload();
  await page.getByText('No uploads yet', { exact: true }).waitFor();
  await page.locator('input[type=file]').setInputFiles([file('x'.repeat(120) + '_2026.pdf'), file('scan_2026.pdf')]);
  const screenshots = process.env.BINTANONG_INTAKE_TEST_EVIDENCE;
  if (screenshots) await mkdir(screenshots, { recursive: true });
  for (const theme of ['light', 'dark']) {
    await page.getByLabel('Appearance').selectOption(theme);
    for (const width of [1280, 390]) {
      await page.setViewportSize({ width, height: 900 });
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${theme} overflow at ${width}`);
      assert(await page.getByLabel('Title for file 1', { exact: true }).isVisible());
      if (screenshots) await page.screenshot({ path: path.join(screenshots, `${theme}-${width}.png`), fullPage: true });
    }
  }
  assert.deepEqual(errors, []);
});
