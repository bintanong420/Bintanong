import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

test('navigation collapses on desktop and opens as a keyboard-safe mobile drawer', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  assert.ok(url && ['localhost', '127.0.0.1'].includes(new URL(url).hostname));
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE, viewport: { width: 1440, height: 900 } });
    const page = await context.newPage(), submissions = [];
    page.on('request', request => { if (request.method() === 'POST' && new URL(request.url()).pathname === '/api/chat') submissions.push(request); });
    await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
    const heading = await page.getByRole('heading', { level: 1 }).boundingBox();
    const composer = await page.locator('.composer').boundingBox();
    assert.ok(composer.y - heading.y - heading.height < 180, 'starter and composer form one focused area');
    const input = page.getByRole('textbox', { name: 'Your question' });
    await input.fill('A draft to keep');
    await page.getByRole('button', { name: 'Program and curriculum', exact: true }).click();
    await page.keyboard.press('Escape');
    await page.getByRole('button', { name: 'Files in this chat', exact: true }).click();
    await page.keyboard.press('Escape');
    assert.equal(await input.inputValue(), 'A draft to keep');
    assert.equal(submissions.length, 0, 'context controls must never submit the composer form');
    await page.getByRole('button', { name: 'Close navigation', exact: true }).click({ timeout: 2500 });
    assert.equal(await page.getByRole('navigation', { name: 'Example questions' }).count(), 0);
    await page.getByRole('button', { name: 'Open navigation', exact: true }).click();
    await page.getByRole('navigation', { name: 'Example questions' }).waitFor();
    await page.setViewportSize({ width: 390, height: 844 });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.getByRole('button', { name: 'Open navigation', exact: true }).click();
    await page.getByRole('dialog', { name: 'Navigation', exact: true }).waitFor();
    assert.equal(await page.getByRole('dialog').evaluate(node => node.getAnimations().length), 0);
    await page.keyboard.press('Escape');
    assert.equal(await page.getByRole('dialog').count(), 0);
    assert.equal(await page.evaluate(() => document.activeElement.getAttribute('aria-label')), 'Open navigation');
    await page.getByRole('button', { name: 'Open navigation', exact: true }).click();
    await page.getByRole('dialog').getByRole('button', { name: 'What if I fail CC5/L?', exact: true }).click();
    assert.equal(await page.getByRole('dialog').count(), 0);
    assert.equal(await page.getByRole('textbox', { name: 'Your question' }).inputValue(), 'What if I fail CC5/L?');
    assert.equal(await page.getByRole('article', { name: 'Your message', exact: true }).count(), 0);
    assert.equal(submissions.length, 0);
  } finally { await browser.close(); }
});
