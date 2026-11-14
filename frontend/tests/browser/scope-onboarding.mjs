import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

// Owner decision, 3 Nov 2026: chat stays locked until a program is chosen; the program can change mid-chat.
const curricula = [
  { programId: 'palsu-bscs', curriculumId: 'bscs-2018-2019', programName: 'Bachelor of Science in Computer Science', curriculumName: '2018-2019' },
  { programId: 'palsu-bscs', curriculumId: 'bscs-proposed-2025-2026', programName: 'Bachelor of Science in Computer Science', curriculumName: '2025-2026' },
  { programId: 'palsu-bsn', curriculumId: 'bsn-2018-2019', programName: 'Bachelor of Science in Nursing', curriculumName: '2018-2019' },
];
function answer(route, submissions) {
  submissions.push(route.request().postDataJSON());
  const parts = [{ type: 'start', messageId: 'synthetic-scope' }, { type: 'text-start', id: 'answer' },
    { type: 'text-delta', id: 'answer', delta: 'Synthetic response.' }, { type: 'text-end', id: 'answer' },
    { type: 'data-answer', data: { status: 'answered', conditional: false, language: 'en', missingFields: [] } },
    { type: 'finish', finishReason: 'stop' }];
  return route.fulfill({ headers: { 'Content-Type': 'text/event-stream', 'x-vercel-ai-ui-message-stream': 'v1' },
    body: parts.map(part => 'data: ' + JSON.stringify(part) + '\n\n').join('') + 'data: [DONE]\n\n' });
}

for (const width of [390, 1440]) test(`chat is locked until a program is chosen; programs search by college and switch mid-chat at ${width}px`, async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  assert.ok(url && ['localhost', '127.0.0.1'].includes(new URL(url).hostname));
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE, viewport: { width, height: 900 } });
    const page = await context.newPage(), submissions = [];
    page.setDefaultTimeout(5000);
    await page.route('**/api/curricula', route => route.fulfill({ json: { curricula } }));
    await page.route('**/api/session', route => route.fulfill({ status: 204 }));
    await page.route('**/api/chat', route => answer(route, submissions));
    await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
    const picker = page.getByRole('dialog', { name: 'Choose your program', exact: true });
    await picker.waitFor();
    assert.equal(await picker.getByRole('region', { name: 'College of Sciences' }).isVisible(), true);
    assert.equal(await picker.getByRole('region', { name: 'College of Nursing and Health Sciences' }).isVisible(), true);
    assert.equal(await picker.locator('.program-option').count(), 0, 'colleges start collapsed');
    await picker.getByRole('button', { name: /College of Sciences/ }).click();
    assert.equal(await picker.locator('.program-option').count(), 1);
    await picker.getByRole('button', { name: /College of Sciences/ }).click();
    assert.equal(await picker.locator('.program-option').count(), 0);
    await picker.getByRole('searchbox', { name: 'Search programs' }).fill('nursing');
    assert.equal(await picker.locator('.program-option').count(), 1);

    // Removing the dialog (as with inspect element) leaves the chat locked.
    await page.evaluate(() => document.querySelector('dialog[open]')?.remove());
    const question = page.getByRole('textbox', { name: 'Your question', exact: true });
    assert.equal(await question.isDisabled(), true);
    await page.evaluate(() => { const input = document.querySelector('textarea'); input.disabled = false; input.form.requestSubmit(); });
    await page.keyboard.press('Enter');
    assert.equal(submissions.length, 0, 'a locked chat never submits');
    assert.equal(await page.getByText('Enter to send', { exact: false }).count(), 0);

    await page.getByRole('button', { name: 'Choose your program', exact: true }).click();
    await picker.getByRole('button', { name: /College of Sciences/ }).click();
    await picker.getByRole('button', { name: /Computer Science/ }).click();
    const year = page.getByRole('dialog', { name: 'When did you start?', exact: true });
    await year.getByRole('radio', { name: 'Before 2023', exact: true }).check();
    await year.getByRole('button', { name: 'Use this program', exact: true }).click();
    const samples = page.getByRole('region', { name: 'Try asking' });
    await samples.getByText('What are the prerequisites of CS 13/L?', { exact: true }).waitFor();
    assert.equal(await page.getByRole('link', { name: /About Bintanong/ }).count(), 0, 'no About icon before chatting');
    await question.fill('A synthetic course question');
    await page.getByRole('button', { name: 'Send question', exact: true }).click();
    await page.getByText('Synthetic response.', { exact: true }).waitFor();
    assert.equal(submissions[0].curriculumId, 'bscs-2018-2019');
    const about = page.getByRole('link', { name: 'About Bintanong (opens in a new tab)', exact: true });
    assert.equal(await about.getAttribute('href'), '/about');
    assert.equal(await about.getAttribute('target'), '_blank');

    // Switch mid-chat to the new BSCS curriculum.
    await page.getByRole('button', { name: /^Program: Bachelor of Science in Computer Science/ }).click();
    await picker.getByRole('searchbox', { name: 'Search programs' }).fill('bscs');
    await picker.getByRole('button', { name: /Computer Science/ }).click();
    await year.getByRole('radio', { name: 'S.Y. 2025–2026', exact: true }).check();
    await year.getByRole('button', { name: 'Use this program', exact: true }).click();
    await question.fill('A second synthetic question');
    await page.getByRole('button', { name: 'Send question', exact: true }).click();
    await page.waitForFunction(() => document.querySelectorAll('.message-assistant').length === 2);
    assert.equal(submissions[1].programId, 'palsu-bscs');
    assert.equal(submissions[1].curriculumId, 'bscs-proposed-2025-2026');
    for (const height of [844, 915]) {
      await page.setViewportSize({ width, height });
      const gap = await page.evaluate(() => innerHeight - document.querySelector('.workspace-main').getBoundingClientRect().bottom);
      assert.ok(Math.abs(gap) <= 1, `chat fills the screen height at ${width}x${height}; ${gap}px left empty below it`);
    }
    await page.setViewportSize({ width, height: 900 });
    if (width < 768) {
      await page.getByRole('button', { name: 'Open navigation', exact: true }).click();
      const navigation = page.getByRole('dialog', { name: 'Navigation', exact: true });
      await navigation.waitFor();
      assert.equal(await navigation.getByText('Navigation', { exact: true }).count(), 0, 'no visible "Navigation" title');
      const brand = navigation.locator('a.brand');
      assert.equal(await brand.count(), 1, 'Bintanong appears once, as the panel title');
      assert.equal(await brand.getAttribute('href'), '/');
      const [brandBox, closeBox] = [await brand.boundingBox(), await navigation.getByRole('button', { name: 'Close Navigation' }).boundingBox()];
      assert.ok(Math.abs((brandBox.y + brandBox.height / 2) - (closeBox.y + closeBox.height / 2)) <= 4, 'brand sits in the top row beside the close button');
    }
    await page.getByRole('button', { name: 'New chat', exact: true }).click();
    await page.getByRole('button', { name: 'Clear chat', exact: true }).click();
    await samples.getByText('Ano ang prerequisites ng Thesis 3?', { exact: true }).waitFor();
    assert.equal(await question.isEnabled(), true, 'New chat keeps the chosen program');
    if (width < 768) for (const height of [780, 915]) {
      await page.setViewportSize({ width, height });
      const below = await page.evaluate(() => innerHeight - document.querySelector('.composer-area').getBoundingClientRect().bottom);
      assert.ok(Math.abs(below) <= 1, `welcome chat bar sits at the bottom at ${width}x${height}; ${below}px below it`);
    }
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await context.close();
  } finally { await browser.close(); }
});

test('an unavailable program list keeps the chat locked and offers a retry', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE });
    const page = await context.newPage();
    page.setDefaultTimeout(5000);
    await page.route('**/api/curricula', route => route.fulfill({ status: 503, json: { error: 'curricula_unavailable' } }));
    await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
    const picker = page.getByRole('dialog', { name: 'Choose your program', exact: true });
    await picker.getByRole('alert').waitFor();
    await picker.getByRole('button', { name: 'Close program choice', exact: true }).click();
    assert.equal(await page.getByRole('textbox', { name: 'Your question', exact: true }).isDisabled(), true);
    await page.getByRole('button', { name: 'Try again', exact: true }).waitFor();
  } finally { await browser.close(); }
});
