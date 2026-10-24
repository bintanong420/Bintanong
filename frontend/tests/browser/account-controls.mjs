import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { mkdir } from 'node:fs/promises';
import { join } from 'node:path';

test('sign-out clears browser credentials even when temporary chat cleanup fails', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  assert.ok(url && ['localhost', '127.0.0.1'].includes(new URL(url).hostname));
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE });
    const page = await context.newPage();
    const fixture = process.env.BINTANONG_TEST_API_URL;
    assert.ok(fixture && ['localhost', '127.0.0.1'].includes(new URL(fixture).hostname));
    const before = await (await context.request.get(new URL('/test-only/auth-status', fixture).href)).json();
    await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
    await page.getByRole('textbox', { name: 'Your question' }).fill('Synthetic refuse clearing');
    await page.getByRole('button', { name: 'Send question', exact: true }).click();
    await page.locator('.source-link').first().waitFor();
    const response = await context.request.post(new URL('/auth/signout', url).href, { headers: { Origin: new URL(url).origin } });
    assert.equal(response.status(), 204, 'backend cleanup failure must not block signing out');
    assert.equal(response.headers()['x-bintanong-signout-notice'], 'cleanup_pending');
    const after = await (await context.request.get(new URL('/test-only/auth-status', fixture).href)).json();
    assert.equal(after.logoutCalls, before.logoutCalls + 1, 'backend cleanup failure must not skip auth revocation');
    const cookies = await context.cookies();
    assert.equal(cookies.some(cookie => cookie.name.includes('-auth-token') || cookie.name === '__Host-bintanong_session'), false);
    await page.goto(new URL('/chat', url).href);
    assert.equal(new URL(page.url()).pathname, '/login', 'protected chat cannot reopen after sign-out');
  } finally { await browser.close(); }
});

test('slow cleanup and failed remote revocation still end the browser session honestly', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    for (const question of ['Synthetic delay cleanup', 'Synthetic refuse revocation']) {
      const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE });
      const page = await context.newPage();
      await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
      await page.getByRole('textbox', { name: 'Your question' }).fill(question);
      await page.getByRole('button', { name: 'Send question', exact: true }).click();
      await page.locator('.source-link').first().waitFor();
      const started = Date.now();
      await page.getByRole('button', { name: 'Sign out', exact: true }).click();
      await page.waitForURL('**/login?notice=cleanup_pending');
      assert.ok(Date.now() - started < 10000);
      await page.getByRole('status').filter({ hasText: "We couldn't confirm that all temporary data was cleared." }).waitFor();
      assert.equal((await context.cookies()).some(cookie => cookie.name.includes('-auth-token') || cookie.name === '__Host-bintanong_session'), false);
      await context.close();
    }
  } finally { await browser.close(); }
});

test('visible sign-out gives feedback, blocks overlapping clearing and protects chat afterward', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE, viewport: { width: 390, height: 844 } });
    const page = await context.newPage();
    await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
    let release;
    await page.route('**/auth/signout', async route => { await new Promise(resolve => { release = resolve; }); await route.continue(); });
    await page.getByRole('button', { name: 'Sign out', exact: true }).click();
    await page.getByRole('button', { name: 'Signing out…', exact: true }).waitFor();
    await page.getByRole('button', { name: 'Open navigation', exact: true }).click();
    assert.equal(await page.getByRole('dialog').getByRole('button', { name: 'New chat', exact: true }).isDisabled(), true);
    await page.keyboard.press('Escape');
    release();
    await page.waitForURL('**/login?notice=signed_out');
    await page.getByRole('status').filter({ hasText: "You're signed out of Bintanong on this browser." }).waitFor();
    assert.equal((await context.cookies()).some(cookie => cookie.name.includes('-auth-token')), false);
    await page.goto(new URL('/chat', url).href);
    assert.equal(new URL(page.url()).pathname, '/login');
  } finally { await browser.close(); }
});

test('signing out can stop an answer that is still running', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE });
    const page = await context.newPage();
    await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
    const response = page.waitForResponse(value => new URL(value.url()).pathname === '/api/chat');
    await page.getByRole('textbox', { name: 'Your question' }).fill('Synthetic slow question before sign-out');
    await page.getByRole('button', { name: 'Send question', exact: true }).click();
    await response;
    await page.getByRole('button', { name: 'Stop response', exact: true }).waitFor();
    await page.getByRole('button', { name: 'Sign out', exact: true }).click();
    await page.waitForURL(value => value.pathname === '/login');
    assert.equal((await context.cookies()).some(cookie => cookie.name.includes('-auth-token') || cookie.name === '__Host-bintanong_session'), false);
  } finally { await browser.close(); }
});

test('missing credentials can sign out again while cross-site sign-out is rejected', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE });
    const denied = await context.request.post(new URL('/auth/signout', url).href, { headers: { Origin: 'https://attacker.example' } });
    assert.equal(denied.status(), 403);
    assert.equal((await context.cookies()).some(cookie => cookie.name.includes('-auth-token')), true);
    await context.clearCookies();
    const response = await context.request.post(new URL('/auth/signout', url).href, { headers: { Origin: new URL(url).origin } });
    assert.equal(response.status(), 204, 'already signed-out browser is not trapped by a 401');
    assert.equal(response.headers()['cache-control'], 'no-store');
    const crossSite = await context.request.post(new URL('/auth/signout', url).href, { headers: { Origin: new URL(url).origin, 'Sec-Fetch-Site': 'cross-site' } });
    assert.equal(crossSite.status(), 403);
  } finally { await browser.close(); }
});

test('an expired session can sign out during a refresh outage without clearing another app cookie', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE });
    const original = (await context.cookies()).find(cookie => cookie.name === 'sb-localhost-auth-token');
    const session = JSON.parse(Buffer.from(original.value.slice(7), 'base64url').toString());
    session.expires_at = Math.floor(Date.now() / 1000) - 120;
    const parts = session.access_token.split('.');
    const claims = JSON.parse(Buffer.from(parts[1], 'base64url').toString());
    claims.exp = session.expires_at;
    parts[1] = Buffer.from(JSON.stringify(claims)).toString('base64url');
    session.access_token = parts.join('.');
    const encoded = 'base64-' + Buffer.from(JSON.stringify(session)).toString('base64url');
    await context.clearCookies();
    await context.addCookies([
      { ...original, name: 'sb-localhost-auth-token.0', value: encoded.slice(0, 800) },
      { ...original, name: 'sb-localhost-auth-token.1', value: encoded.slice(800) },
      { ...original, name: 'sb-unrelated-auth-token', value: 'keep-another-app-session' },
    ]);
    const started = Date.now();
    const response = await context.request.post(new URL('/auth/signout', url).href, { headers: { Origin: new URL(url).origin }, timeout: 45000 });
    assert.equal(response.status(), 204, 'refresh failure must not prevent local sign-out');
    assert.ok(Date.now() - started < 12000, 'auth outage cannot strand sign-out behind repeated refreshes');
    assert.equal(response.headers()['x-bintanong-signout-notice'], 'cleanup_pending');
    const cookies = await context.cookies();
    assert.equal(cookies.some(cookie => cookie.name.startsWith('sb-localhost-auth-token')), false);
    assert.equal(cookies.some(cookie => cookie.name === 'sb-unrelated-auth-token'), true);
  } finally { await browser.close(); }
});

test('curriculum wording explains the student task and errors keep drafts with a direct retry', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE, viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    await page.route('**/api/curricula', route => route.fulfill({ status: 503, contentType: 'application/json', body: '{"error":"service_unavailable"}' }));
    await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
    const input = page.getByRole('textbox', { name: 'Your question' });
    await input.fill('Which subjects can I take next semester?');
    await page.getByRole('button', { name: 'Program and curriculum', exact: true }).click();
    const dialog = page.getByRole('dialog', { name: 'Program and curriculum', exact: true });
    await dialog.getByText(/subjects and prerequisites/).waitFor();
    await dialog.getByText(/Check your prospectus or ask your academic adviser/).waitFor();
    assert.equal((await dialog.innerText()).includes('reviewed research records'), false);
    assert.equal(await dialog.getByRole('combobox').isDisabled(), true);
    assert.equal(await dialog.getByRole('button', { name: 'Continue without selecting', exact: true }).isDisabled(), true);
    await page.unroute('**/api/curricula');
    await dialog.getByRole('button', { name: 'Try again', exact: true }).click();
    await dialog.getByRole('combobox').selectOption('bscs-2018');
    await dialog.getByRole('button', { name: 'Use this curriculum', exact: true }).click();
    assert.equal(await input.inputValue(), 'Which subjects can I take next semester?');
    await page.route('**/auth/signout', route => route.fulfill({ status: 503 }));
    await page.getByRole('button', { name: 'Sign out', exact: true }).click();
    const alert = page.getByRole('alert').filter({ hasText: "We couldn't finish signing you out." });
    await alert.waitFor();
    assert.equal(await input.inputValue(), 'Which subjects can I take next semester?');
    assert.ok((await alert.boundingBox()).width <= (await page.locator('.composer').boundingBox()).width + 1);
    assert.equal((await context.cookies()).some(cookie => cookie.name.includes('-auth-token')), true);
    await page.unroute('**/auth/signout');
    await page.getByRole('button', { name: 'Try signing out again', exact: true }).click();
    await page.waitForURL('**/login?notice=signed_out');
  } finally { await browser.close(); }
});

test('account controls and curriculum dialog fit small screens, both themes and enlarged text', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    for (const theme of ['light', 'dark']) for (const width of [320, 390, 768, 1440]) {
      const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE, viewport: { width, height: 900 }, colorScheme: theme, reducedMotion: 'reduce' });
      const page = await context.newPage();
      await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
      const signOut = page.getByRole('button', { name: 'Sign out', exact: true });
      assert.equal(await signOut.isVisible(), true);
      assert.ok((await signOut.boundingBox()).height >= 44);
      const trigger = page.getByRole('button', { name: 'Program and curriculum', exact: true });
      await trigger.click();
      const dialog = page.getByRole('dialog', { name: 'Program and curriculum', exact: true });
      const box = await dialog.boundingBox();
      assert.ok(box.x >= 0 && box.x + box.width <= width + 1);
      assert.equal(await dialog.locator('p').first().evaluate(node => getComputedStyle(node).fontSize), '16px');
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
      await dialog.getByRole('button', { name: 'Cancel', exact: true }).scrollIntoViewIfNeeded();
      const cancel = await dialog.getByRole('button', { name: 'Cancel', exact: true }).boundingBox();
      assert.ok(cancel.y >= 0 && cancel.y + cancel.height <= 901);
      if (process.env.BINTANONG_BROWSER_EVIDENCE) {
        await mkdir(process.env.BINTANONG_BROWSER_EVIDENCE, { recursive: true });
        await page.screenshot({ path: join(process.env.BINTANONG_BROWSER_EVIDENCE, `curriculum-${theme}-${width}.png`) });
      }
      await page.keyboard.press('Escape');
      assert.equal(await trigger.evaluate(node => document.activeElement === node), true);
      if (width === 768) {
        await page.evaluate(() => { document.documentElement.style.zoom = '2'; });
        await trigger.click();
        await dialog.getByRole('button', { name: 'Cancel', exact: true }).scrollIntoViewIfNeeded();
        assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
        await page.keyboard.press('Escape');
      }
      await context.close();
    }
  } finally { await browser.close(); }
});
