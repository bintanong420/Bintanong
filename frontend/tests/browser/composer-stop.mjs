import { dismissInitialScope } from './scope-helper.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

test('Stop preserves the next draft without submitting another question', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  assert.ok(url && ['localhost', '127.0.0.1'].includes(new URL(url).hostname), 'Use the isolated loopback test preview');
  assert.ok(process.env.BINTANONG_BROWSER_STATE, 'Provide the synthetic fixture browser state');
  assert.ok(process.env.PLAYWRIGHT_MODULE, 'Provide an existing Playwright module path');
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE, viewport: { width: 390, height: 844 } });
    const page = await context.newPage(), submissions = [];
    page.on('request', request => {
      if (request.method() === 'POST' && new URL(request.url()).pathname === '/api/chat') submissions.push(request);
    });
    await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
    await dismissInitialScope(page);
    const input = page.getByRole('textbox', { name: 'Your question' });
    await input.fill('Synthetic slow request');
    await page.getByRole('button', { name: 'Send question', exact: true }).click();
    const stop = page.getByRole('button', { name: 'Stop response', exact: true });
    await stop.waitFor();
    await input.fill('Keep this next question');
    await stop.click();
    await page.getByText('Response stopped. Your question remains in the conversation.', { exact: true }).waitFor();
    assert.equal(await input.inputValue(), 'Keep this next question');
    assert.equal(submissions.length, 1);
    assert.equal(await page.getByRole('article', { name: 'Your message', exact: true }).count(), 1);
  } finally { await browser.close(); }
});
