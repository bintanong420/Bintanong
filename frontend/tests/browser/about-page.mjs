import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

test('about page is public, leads back to chat and only claims supported capabilities', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  assert.ok(url && ['localhost', '127.0.0.1'].includes(new URL(url).hostname));
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    for (const theme of ['light', 'dark']) for (const width of [320, 390, 1440]) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: theme, reducedMotion: 'reduce' });
      await context.addInitScript(value => localStorage.setItem('bintanong-appearance', value), theme);
      const page = await context.newPage(), errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const response = await page.goto(new URL('/about', url).href, { waitUntil: 'networkidle' });
      assert.equal(response.status(), 200);
      assert.equal(new URL(page.url()).pathname, '/about', 'guests are not redirected');
      await page.getByRole('heading', { level: 1, name: "Hi, I'm Bintanong", exact: true }).waitFor();
      assert.equal(await page.locator('.about-hero img').evaluate(img => img.complete && img.naturalWidth > 0), true);
      assert.equal(await page.getByRole('link', { name: 'Back to chat', exact: true }).getAttribute('href'), '/chat');
      assert.equal(await page.getByRole('link', { name: 'Start chatting with Bintanong', exact: true }).getAttribute('href'), '/chat');
      const text = await page.locator('main').innerText();
      assert.doesNotMatch(text, /graduation|flowchart|audit units/i, 'no capability the system does not provide');
      assert.match(text, /Research preview/);
      assert.match(text, /cannot enroll you, change grades or issue a COR/);
      assert.match(text, /university office or academic adviser/);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, 'enlarged text reflows');
      assert.deepEqual(errors, []);
      await context.close();
    }
  } finally { await browser.close(); }
});