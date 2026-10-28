import { dismissInitialScope } from './scope-helper.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import sharp from 'sharp';

function luminance(rgb) {
  return Array.from(rgb).slice(0, 3).map(value => value / 255).map(value => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4).reduce((sum, value, index) => sum + value * [.2126, .7152, .0722][index], 0);
}

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
      const backdrop = await page.locator('.campus-banner').boundingBox();
      assert.equal(backdrop.y, main.y, 'campus fade continues behind the header instead of starting at a hard edge');
      const header = await page.locator('.workspace-toolbar').boundingBox();
      assert.ok(header.height <= 76, `${width}/${theme}: compact header stays on one row`);
      for (const name of ['Program and curriculum', 'Chat options', 'Sign out']) {
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

test('public entry gives the greeting and real entry action priority over the photograph', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  assert.ok(url && ['localhost', '127.0.0.1'].includes(new URL(url).hostname));
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    for (const theme of ['light', 'dark']) for (const width of [320, 390, 768, 1440]) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: theme, reducedMotion: 'reduce' });
      await context.addInitScript(value => localStorage.setItem('bintanong-appearance', value), theme);
      const page = await context.newPage(), errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(url, { waitUntil: 'networkidle' });
      await page.keyboard.press('Tab');
      assert.equal(await page.getByRole('link', { name: 'Skip to content', exact: true }).evaluate(node => document.activeElement === node), true);
      const title = await page.getByRole('heading', { level: 1 }).boundingBox();
      const photo = await page.locator('.landing-photo').boundingBox();
      const action = page.getByRole('link', { name: 'Ask a question', exact: true });
      const box = await action.boundingBox();
      assert.ok(box.y + box.height < 900, `${width}/${theme}: entry action is immediately visible`);
      if (width >= 1100) assert.ok(photo.x > title.x + title.width, 'campus sits beside the invitation');
      else assert.ok(photo.y > box.y + box.height, 'mobile invitation comes before the photo');
      assert.equal(await action.getAttribute('href'), '/chat');
      assert.equal(await page.locator('.landing-photo img').evaluate(img => img.complete && img.naturalWidth > 0), true);
      await page.getByRole('link', { name: 'What can I ask?', exact: true }).click();
      await page.getByRole('heading', { name: 'Start with your question.', exact: true }).waitFor();
      assert.equal(await page.locator('#privacy').count(), 1);
      assert.match(await page.locator('#scope').innerText(), /Missing information stays unknown/);
      const ratios = await page.evaluate(() => {
        const canvas = document.createElement('canvas'), ctx = canvas.getContext('2d');
        const luminance = color => {
          ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = color; ctx.fillRect(0, 0, 1, 1);
          return [...ctx.getImageData(0, 0, 1, 1).data].slice(0, 3).map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4).reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
        };
        const background = getComputedStyle(document.querySelector('.landing-page')).backgroundColor;
        return ['.landing-description', '.public-caption', '.landing-introduction [data-slot="button"]'].map(selector => {
          const style = getComputedStyle(document.querySelector(selector));
          const a = luminance(style.color), b = luminance(style.backgroundColor === 'rgba(0, 0, 0, 0)' ? background : style.backgroundColor);
          return (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
        });
      });
      assert.ok(ratios.every(ratio => ratio >= 4.5), `text contrast: ${ratios.join(', ')}`);
      if (width === 320 || width === 1440) {
        const figure = page.locator('.landing-photo'), caption = figure.locator('figcaption');
        await figure.scrollIntoViewIfNeeded();
        const area = await figure.boundingBox(), text = await caption.boundingBox();
        const foreground = await caption.evaluate(node => {
          const ctx = document.createElement('canvas').getContext('2d');
          ctx.fillStyle = getComputedStyle(node).color; ctx.fillRect(0, 0, 1, 1);
          return Array.from(ctx.getImageData(0, 0, 1, 1).data);
        });
        await caption.evaluate(node => { node.style.visibility = 'hidden'; });
        const pixels = await sharp(await figure.screenshot()).extract({ left: Math.floor(text.x - area.x), top: Math.floor(text.y - area.y), width: Math.floor(text.width), height: Math.floor(text.height) }).removeAlpha().raw().toBuffer();
        await caption.evaluate(node => { node.style.visibility = ''; });
        let brightest = 0;
        for (let i = 0; i < pixels.length; i += 3) {
          brightest = Math.max(brightest, luminance(pixels.subarray(i, i + 3)));
        }
        assert.ok((luminance(foreground) + .05) / (brightest + .05) >= 4.5, `${width}/${theme}: caption contrasts with every underlying image pixel`);
      }
      if (process.env.BINTANONG_BROWSER_EVIDENCE) {
        await mkdir(process.env.BINTANONG_BROWSER_EVIDENCE, { recursive: true });
        await page.screenshot({ path: join(process.env.BINTANONG_BROWSER_EVIDENCE, `landing-${width}-${theme}.png`), fullPage: true });
      }
      await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, 'enlarged text reflows');
      assert.deepEqual(errors, []);
      if (width === 390 && theme === 'light') {
        await action.click();
        await page.waitForURL('**/login');
      }
      await context.close();
    }
  } finally { await browser.close(); }
});
