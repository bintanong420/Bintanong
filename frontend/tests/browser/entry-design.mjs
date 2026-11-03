import { dismissInitialScope } from './scope-helper.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { mkdir } from 'node:fs/promises';
import { join } from 'node:path';

test('chat header has a continuous backdrop and one usable row at narrow widths', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  assert.ok(url && ['localhost', '127.0.0.1'].includes(new URL(url).hostname));
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    for (const theme of ['light', 'dark']) for (const width of [320, 390, 1440]) {
      const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE, viewport: { width, height: 900 }, colorScheme: theme });
      await context.addInitScript(value => localStorage.setItem('bintanong-appearance', value), theme);
      const page = await context.newPage();
      await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
      await dismissInitialScope(page);
      const main = await page.locator('.workspace-main').boundingBox();
      assert.match(await page.locator('.workspace-main').evaluate(node => getComputedStyle(node).backgroundImage), /radial-gradient/, 'ambient backdrop continues behind the header instead of starting at a hard edge');
      const header = await page.locator('.workspace-toolbar').boundingBox();
      assert.ok(header.height <= 76, `${width}/${theme}: compact header stays on one row`);
      // The program control moved beside the chat bar (3 Nov 2026); the header keeps account actions.
      for (const name of ['Chat options', 'Sign out']) {
        const button = page.getByRole('button', { name, exact: true });
        assert.equal(await button.isVisible(), true);
        const box = await button.boundingBox();
        assert.ok(box.height >= 44 && box.width >= 44 && box.x >= main.x && box.x + box.width <= main.x + main.width + 1, name);
      }
      await page.getByRole('button', { name: 'Chat options', exact: true }).click();
      await page.getByRole('combobox', { name: 'Appearance', exact: true }).selectOption(theme === 'light' ? 'dark' : 'light');
      assert.equal(await page.evaluate(() => document.documentElement.dataset.appearance), theme === 'light' ? 'dark' : 'light');
      await page.getByRole('combobox', { name: 'Appearance', exact: true }).selectOption(theme);
      await page.keyboard.press('Escape');
      await page.locator('.workspace-toolbar').evaluate(node => Promise.all(node.getAnimations({ subtree: true }).map(animation => animation.finished.catch(() => {}))));
      assert.equal(await page.getByRole('button', { name: 'Chat options', exact: true }).evaluate(node => document.activeElement === node), true);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      if (process.env.BINTANONG_BROWSER_EVIDENCE) {
        await mkdir(process.env.BINTANONG_BROWSER_EVIDENCE, { recursive: true });
        await page.screenshot({ path: join(process.env.BINTANONG_BROWSER_EVIDENCE, `header-${width}-${theme}.png`) });
      }
      await context.close();
    }
  } finally { await browser.close(); }
});

test('landing page leads with the entry action and keeps scope, privacy and sign-in reachable', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  assert.ok(url && ['localhost', '127.0.0.1'].includes(new URL(url).hostname));
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    for (const width of [320, 390, 768, 1440]) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
      const page = await context.newPage(), errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(url, { waitUntil: 'networkidle' });
      await page.keyboard.press('Tab');
      assert.equal(await page.getByRole('link', { name: 'Skip to content', exact: true }).evaluate(node => document.activeElement === node), true);
      await page.getByRole('heading', { level: 1 }).waitFor();
      const action = page.locator('#main').getByRole('link', { name: 'Ask a question' });
      const box = await action.boundingBox();
      assert.ok(box.y + box.height < 900, `${width}: entry action is immediately visible`);
      assert.equal(await action.getAttribute('href'), '/chat');
      if (width < 768) await page.getByRole('button', { name: 'Toggle navigation' }).click();
      assert.equal(await page.getByRole('link', { name: 'Sign in', exact: true }).getAttribute('href'), '/login');
      assert.equal(await page.locator('#privacy').count(), 1, 'login page links to /#privacy');
      const faq = page.getByRole('button', { name: 'How are prerequisite checks done?' });
      await faq.click();
      assert.equal(await faq.getAttribute('aria-expanded'), 'true');
      assert.match(await page.locator('#faq').innerText(), /says it is unknown/);
      assert.match(await page.locator('#use-case').innerText(), /Illustration, not a real answer/);
      if (process.env.BINTANONG_BROWSER_EVIDENCE) {
        await mkdir(process.env.BINTANONG_BROWSER_EVIDENCE, { recursive: true });
        await page.screenshot({ path: join(process.env.BINTANONG_BROWSER_EVIDENCE, `landing-${width}.png`), fullPage: true });
      }
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, 'no horizontal overflow');
      assert.deepEqual(errors, []);
      if (width === 390) {
        await action.click();
        await page.waitForURL('**/chat');
        await dismissInitialScope(page);
        await page.getByText('Guest', { exact: true }).waitFor();
      }
      await context.close();
    }
  } finally { await browser.close(); }
});
