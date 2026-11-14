import { dismissInitialScope } from './scope-helper.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { mkdir } from 'node:fs/promises';
import { join } from 'node:path';

test('welcome keeps the mascot identity, ambient backdrop and pill composer', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  assert.ok(url && ['localhost', '127.0.0.1'].includes(new URL(url).hostname));
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    for (const [width, height, theme] of [[1440, 900, 'light'], [1440, 900, 'dark'], [390, 844, 'light'], [390, 844, 'dark'], [320, 568, 'light'], [320, 568, 'dark']]) {
      const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE, viewport: { width, height }, reducedMotion: 'reduce', colorScheme: theme });
      await context.addInitScript(value => localStorage.setItem('bintanong-appearance', value), theme);
      const page = await context.newPage(), errors = [], submissions = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.route('**/api/chat', route => {
        submissions.push(route.request().postDataJSON());
        const parts = [{ type: 'start', messageId: 'synthetic-welcome' }, { type: 'text-start', id: 'answer' }, { type: 'text-delta', id: 'answer', delta: 'Synthetic layout response.' }, { type: 'text-end', id: 'answer' }, { type: 'data-answer', data: { status: 'answered', conditional: false, language: 'en', missingFields: [] } }, { type: 'finish', finishReason: 'stop' }];
        return route.fulfill({ status: 200, headers: { 'Content-Type': 'text/event-stream', 'x-vercel-ai-ui-message-stream': 'v1' }, body: parts.map(part => 'data: ' + JSON.stringify(part) + '\n\n').join('') + 'data: [DONE]\n\n' });
      });
      await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
      await dismissInitialScope(page);
      const welcome = page.getByRole('region', { name: "Hi, I'm Bintanong", exact: true });
      await welcome.waitFor();
      assert.equal(await welcome.evaluate(node => getComputedStyle(node).textAlign), 'center', `${width}/${theme}: welcome copy is centered`);
      const main = await page.locator('.workspace-main').boundingBox();
      for (const selector of ['.welcome-logo', '#welcome-title', '.welcome-description']) {
        const box = await welcome.locator(selector).boundingBox();
        assert.ok(Math.abs(box.x + box.width / 2 - main.x - main.width / 2) < 2, `${width}/${theme}: ${selector} shares the workspace center`);
      }
      assert.match(await page.locator('.workspace-main').evaluate(node => getComputedStyle(node).backgroundImage), /radial-gradient/, 'welcome carries the ambient backdrop');
      const logo = page.locator('.welcome-logo img');
      assert.equal(await logo.evaluate(img => img.complete && img.naturalWidth > 0), true);
      assert.equal(await logo.getAttribute('alt'), '', 'decorative mascot is not repeated to screen readers');
      const mark = await page.locator('.welcome-logo').boundingBox(), art = await logo.boundingBox();
      assert.equal(mark.width, 80, 'the mascot keeps its requested size');
      assert.ok(art.width >= 64 && art.height >= 64, 'the mascot art fills its mark');
      assert.equal(await page.getByRole('link', { name: 'Learn more about me', exact: true }).getAttribute('href'), '/about');
      const composer = await page.locator('.composer').boundingBox(), starters = await page.getByRole('group', { name: 'Suggested questions', exact: true }).boundingBox();
      assert.ok(starters.y + starters.height <= composer.y, 'starters sit above the composer');
      assert.ok(composer.height <= 72, `${width}/${theme}: an empty composer stays one pill row`);
      for (const name of ['Add a PDF to this chat', 'Send question', 'Files in this chat']) {
        const box = await page.getByRole('button', { name, exact: true }).boundingBox();
        assert.ok(box.height >= 44 && box.width >= 44, name + ' keeps a usable touch target');
      }
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      if (process.env.BINTANONG_BROWSER_EVIDENCE) {
        await mkdir(process.env.BINTANONG_BROWSER_EVIDENCE, { recursive: true });
        await page.screenshot({ path: join(process.env.BINTANONG_BROWSER_EVIDENCE, `centered-welcome-${width}-${theme}.png`) });
      }
      const input = page.getByRole('textbox', { name: 'Your question', exact: true });
      await page.getByRole('button', { name: 'Find course prerequisites', exact: true }).click();
      assert.match(await input.inputValue(), /prerequisites/);
      assert.equal(submissions.length, 0, 'starter remains an editable draft');
      await page.getByRole('button', { name: 'Send question', exact: true }).click();
      await page.getByText('Synthetic layout response.', { exact: true }).waitFor();
      assert.equal(await page.locator('.welcome-surface').count(), 0, 'active conversation keeps a clear reading area');
      assert.equal(await page.locator('.message-assistant .brand-mark img').evaluate(img => img.complete && img.naturalWidth > 0), true, 'answers carry the mascot');
      assert.equal((await page.locator('.message-assistant .brand-mark').boundingBox()).width, 28, 'the answer avatar stays compact');
      assert.equal(await page.getByRole('button', { name: 'Edit as new question', exact: true }).count(), 1);
      assert.deepEqual(errors, []);
      await context.close();
    }
  } finally { await browser.close(); }
});
