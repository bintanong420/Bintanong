import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

for (const width of [390, 1440]) test(`fresh chat asks for scope without guessing, allows policy questions and resets after clear at ${width}px`, async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  assert.ok(url && ['localhost', '127.0.0.1'].includes(new URL(url).hostname));
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE, viewport: { width, height: 900 } });
    const page = await context.newPage(), submissions = [];
    page.setDefaultTimeout(5000);
    await page.route('**/api/curricula', route => route.fulfill({ json: { curricula: [
      { programId: 'program-a', curriculumId: 'curriculum-a', programName: 'Program A', curriculumName: 'Curriculum A' },
    ] } }));
    await page.route('**/api/session', route => route.fulfill({ status: 204 }));
    await page.route('**/api/chat', route => {
      submissions.push(route.request().postDataJSON());
      const parts = [{ type: 'start', messageId: 'synthetic-scope' }, { type: 'text-start', id: 'answer' },
        { type: 'text-delta', id: 'answer', delta: 'Synthetic policy response.' }, { type: 'text-end', id: 'answer' },
        { type: 'data-answer', data: { status: 'answered', conditional: false, language: 'en', missingFields: [] } },
        { type: 'finish', finishReason: 'stop' }];
      return route.fulfill({ headers: { 'Content-Type': 'text/event-stream', 'x-vercel-ai-ui-message-stream': 'v1' },
        body: parts.map(part => 'data: ' + JSON.stringify(part) + '\n\n').join('') + 'data: [DONE]\n\n' });
    });
    await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
    await page.locator('textarea').first().waitFor();
    const scope = page.getByRole('dialog', { name: 'Program and curriculum', exact: true });
    await scope.waitFor();
    assert.equal(await scope.getByRole('combobox').inputValue(), '');
    assert.equal(submissions.length, 0, 'opening scope never submits a question');
    await scope.getByRole('button', { name: 'Skip for now', exact: true }).click();
    await page.getByRole('textbox', { name: 'Your question', exact: true }).fill('A synthetic policy question');
    await page.getByRole('button', { name: 'Send question', exact: true }).click();
    await page.getByText('Synthetic policy response.', { exact: true }).waitFor();
    assert.equal('programId' in submissions[0], false);
    assert.equal('curriculumId' in submissions[0], false);
    await page.getByRole('button', { name: 'Program and curriculum', exact: true }).click();
    await scope.getByRole('combobox').selectOption('curriculum-a');
    await scope.getByRole('button', { name: 'Use this curriculum', exact: true }).click();
    assert.equal(submissions.length, 1, 'choosing a curriculum never sends a question');
    await page.getByRole('textbox', { name: 'Your question', exact: true }).fill('A synthetic course question');
    await page.getByRole('button', { name: 'Send question', exact: true }).click();
    await page.waitForFunction(() => !document.querySelector('.working-card'));
    assert.equal(submissions[1].programId, 'program-a');
    assert.equal(submissions[1].curriculumId, 'curriculum-a');
    if (width < 768) await page.getByRole('button', { name: 'Open navigation', exact: true }).click();
    await page.getByRole('button', { name: 'New chat', exact: true }).click();
    await page.getByRole('button', { name: 'Clear chat', exact: true }).click();
    await scope.waitFor();
    assert.equal(await scope.getByRole('combobox').inputValue(), '');
    assert.equal(submissions.length, 2);
    await context.close();
  } finally { await browser.close(); }
});

test('unavailable curriculum list never forces a guessed selection or blocks a policy question', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE });
    const page = await context.newPage();
    await page.route('**/api/curricula', route => route.fulfill({ status: 503, json: { error: 'curricula_unavailable' } }));
    await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
    const scope = page.getByRole('dialog', { name: 'Program and curriculum', exact: true });
    await scope.getByRole('alert').waitFor();
    assert.equal(await scope.getByRole('combobox').isDisabled(), true);
    await scope.getByRole('button', { name: 'Skip for now', exact: true }).click();
    assert.equal(await page.getByRole('textbox', { name: 'Your question', exact: true }).isEnabled(), true);
  } finally { await browser.close(); }
});
