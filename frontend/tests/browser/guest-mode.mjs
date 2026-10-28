import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { dismissInitialScope } from './scope-helper.mjs';

test('unreadable auth credentials are refused instead of becoming a guest', async () => {
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext();
    await context.addCookies([{ name: process.env.BINTANONG_AUTH_COOKIE ?? 'sb-127-auth-token', value: 'base64-invalid',
      domain: new URL(process.env.BINTANONG_BROWSER_URL).hostname, path: '/' }]);
    const response = await context.request.get(new URL('/api/curricula', process.env.BINTANONG_BROWSER_URL).href);
    assert.equal(response.status(), 503);
    assert.equal((await response.json()).error, 'auth_unavailable');
  } finally { await browser.close(); }
});

test('visitors enter chat without auth and see optional sign-in on both entry pages', async () => {
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
    const page = await context.newPage();
    page.setDefaultTimeout(5000);
    page.setDefaultNavigationTimeout(45000);
    await page.goto(process.env.BINTANONG_BROWSER_URL, { waitUntil: 'networkidle' });
    await page.getByText('Continue as a guest or sign in with your PSU Google account.', { exact: false }).waitFor();
    await page.getByRole('link', { name: 'Sign in', exact: true }).click();
    await page.getByRole('link', { name: 'Continue as guest', exact: true }).click();
    await dismissInitialScope(page);
    assert.equal(new URL(page.url()).pathname, '/chat');
    await page.getByText('Guest', { exact: true }).waitFor();
    assert.equal(await page.getByRole('link', { name: 'Sign in', exact: true }).isVisible(), true);
    assert.equal(await page.getByRole('button', { name: 'Sign out', exact: true }).count(), 0);
    assert.equal(await page.getByRole('textbox', { name: 'Your question', exact: true }).isEnabled(), true);
    assert.equal((await context.cookies()).some(cookie => cookie.name.includes('-auth-token')), false);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  } finally { await browser.close(); }
});

test('another tab switching access clears private drafts and aborts a pending guest answer', async () => {
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext();
    const page = await context.newPage();
    page.setDefaultTimeout(5000);
    page.setDefaultNavigationTimeout(45000);
    await page.goto(new URL('/chat', process.env.BINTANONG_BROWSER_URL).href, { waitUntil: 'networkidle' });
    await dismissInitialScope(page);
    const input = page.getByRole('textbox', { name: 'Your question', exact: true });
    await input.fill('Synthetic slow request');
    await page.getByRole('button', { name: 'Send question', exact: true }).click();
    await page.getByRole('button', { name: 'Stop response', exact: true }).waitFor();
    const other = await context.newPage();
    await other.goto(new URL('/', process.env.BINTANONG_BROWSER_URL).href);
    const navigation = page.waitForEvent('framenavigated', { predicate: frame => frame === page.mainFrame() });
    await other.evaluate(() => {
      const channel = new BroadcastChannel('bintanong-access');
      channel.postMessage({ identity: 'synthetic-account' });
      channel.close();
    });
    await navigation;
    await page.waitForLoadState('networkidle');
    await dismissInitialScope(page);
    assert.equal(await input.inputValue(), '');
    assert.equal(await page.getByRole('article', { name: 'Your message', exact: true }).count(), 0);
    assert.equal(await page.getByRole('button', { name: 'Stop response', exact: true }).count(), 0);
    assert.equal(await page.getByRole('button', { name: 'Program and curriculum', exact: true }).getAttribute('title'), 'Choose your program and curriculum');
  } finally { await browser.close(); }
});

test('the existing signed-in workspace keeps sign-out controls beside guest access', async () => {
  assert.ok(process.env.BINTANONG_BROWSER_STATE, 'synthetic signed-in state is required');
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE });
    const page = await context.newPage();
    await page.goto(new URL('/chat', process.env.BINTANONG_BROWSER_URL).href, { waitUntil: 'networkidle' });
    await dismissInitialScope(page);
    assert.equal(await page.getByRole('button', { name: 'Sign out', exact: true }).isVisible(), true);
    assert.equal(await page.getByRole('link', { name: 'Sign in', exact: true }).count(), 0);
    assert.equal(await page.getByText('Guest', { exact: true }).count(), 0);
  } finally { await browser.close(); }
});

test('a guest can review a temporary PDF, confirm courses, ask, delete and clear', async () => {
  assert.ok(process.env.BINTANONG_GUEST_PDF, 'synthetic PDF path is required');
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext();
    const page = await context.newPage();
    page.setDefaultTimeout(7000);
    await page.goto(new URL('/chat', process.env.BINTANONG_BROWSER_URL).href, { waitUntil: 'networkidle' });
    const scope = page.getByRole('dialog', { name: 'Program and curriculum', exact: true });
    await scope.getByRole('combobox').selectOption('bscs-2018');
    await scope.getByRole('button', { name: 'Use this curriculum', exact: true }).click();
    await page.locator('input[type=file]').setInputFiles(process.env.BINTANONG_GUEST_PDF);
    const files = page.getByRole('dialog', { name: 'Files in this chat', exact: true });
    await files.getByRole('combobox', { name: 'Status for CC 5/L', exact: true }).selectOption('passed');
    await files.getByRole('button', { name: 'Save selected course details', exact: true }).click();
    await files.getByText('Selected course details saved for this chat.', { exact: true }).waitFor();
    await page.keyboard.press('Escape');
    await page.getByRole('textbox', { name: 'Your question', exact: true }).fill('A synthetic question about my course');
    await page.getByRole('button', { name: 'Send question', exact: true }).click();
    await page.getByRole('article', { name: 'Bintanong response', exact: true }).waitFor();
    await page.getByRole('button', { name: 'Files in this chat', exact: true }).click();
    await files.getByRole('button', { name: 'Remove synthetic-grades.pdf', exact: true }).click();
    await files.getByText('No PDFs added', { exact: true }).waitFor();
    await page.keyboard.press('Escape');
    await page.getByRole('button', { name: 'New chat', exact: true }).click();
    await page.getByRole('button', { name: 'Clear chat', exact: true }).click();
    await scope.waitFor();
    assert.equal(await scope.getByRole('combobox').inputValue(), '');
    assert.equal((await context.cookies()).some(cookie => cookie.name.includes('-auth-token')), false);
  } finally { await browser.close(); }
});
