import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { dismissInitialScope } from './scope-helper.mjs';

// A refused question (all answer slots busy) shows no "interrupted" bubble, retries itself every 15 s,
// can be retried at once or cancelled, and the cancelled question returns to the chat box.
const curricula = [{ programId: 'palsu-bsn', curriculumId: 'bsn-2018-2019', programName: 'Bachelor of Science in Nursing', curriculumName: '2018-2019' }];
function answer(route) {
  const parts = [{ type: 'start', messageId: 'synthetic-busy' }, { type: 'text-start', id: 'answer' },
    { type: 'text-delta', id: 'answer', delta: 'Synthetic answer after waiting.' }, { type: 'text-end', id: 'answer' },
    { type: 'data-answer', data: { status: 'answered', conditional: false, language: 'en', missingFields: [] } },
    { type: 'finish', finishReason: 'stop' }];
  return route.fulfill({ headers: { 'Content-Type': 'text/event-stream', 'x-vercel-ai-ui-message-stream': 'v1' },
    body: parts.map(part => 'data: ' + JSON.stringify(part) + '\n\n').join('') + 'data: [DONE]\n\n' });
}

async function open(busyCalls) {
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  page.setDefaultTimeout(5000);
  const calls = [];
  await page.clock.install();
  await page.route('**/api/curricula', route => route.fulfill({ json: { curricula } }));
  await page.route('**/api/chat', route => {
    calls.push(route.request().postDataJSON());
    return calls.length <= busyCalls ? route.fulfill({ status: 503, json: { error: 'answers_busy' } }) : answer(route);
  });
  await page.goto(new URL('/chat', process.env.BINTANONG_BROWSER_URL).href, { waitUntil: 'networkidle' });
  await dismissInitialScope(page);
  await page.getByRole('textbox', { name: 'Your question', exact: true }).fill('How do I drop a subject?');
  await page.getByRole('button', { name: 'Send question', exact: true }).click();
  return { browser, page, calls };
}

test('a busy question retries on its own and on request, without an interrupted bubble', async () => {
  const { browser, page, calls } = await open(2);
  try {
    const notice = page.locator('.busy-retry');
    await page.waitForFunction(() => /All answer slots are busy/.test(document.querySelector('.busy-retry')?.textContent ?? ''));
    assert.equal(await page.getByText('Response interrupted', { exact: false }).count(), 0);
    assert.equal(await page.getByText('How do I drop a subject?', { exact: false }).count() >= 1, true, 'the waiting question is shown');
    assert.match(await notice.innerText(), /Retrying in 15 s/);
    await notice.getByRole('button', { name: 'Try again now', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('.busy-retry')?.textContent?.includes('attempt 2'));
    assert.equal(calls.length, 2);
    await page.clock.runFor(16000);
    await page.getByText('Synthetic answer after waiting.', { exact: true }).waitFor();
    assert.equal(calls.length, 3);
    assert.equal(calls[2].text ?? calls[2].messages?.at(-1)?.parts?.[0]?.text ?? 'How do I drop a subject?', 'How do I drop a subject?');
    assert.equal(await notice.count(), 0);
    assert.equal(await page.locator('.message-user').count(), 1, 'the question appears once');
  } finally { await browser.close(); }
});

test('cancelling a busy retry puts the question back in the chat box', async () => {
  const { browser, page, calls } = await open(99);
  try {
    const notice = page.locator('.busy-retry');
    await notice.getByRole('button', { name: 'Cancel', exact: true }).click();
    assert.equal(await notice.count(), 0);
    assert.equal(await page.getByRole('textbox', { name: 'Your question', exact: true }).inputValue(), 'How do I drop a subject?');
    await page.clock.runFor(60000);
    assert.equal(calls.length, 1, 'no retry after cancelling');
  } finally { await browser.close(); }
});

test('after four automatic retries it stops and offers a manual try', async () => {
  const { browser, page, calls } = await open(99);
  try {
    for (let i = 0; i < 4; i++) {
      await page.waitForFunction(n => document.querySelector('.busy-retry')?.textContent?.includes(`attempt ${n}`), i + 1);
      await page.clock.runFor(16000);
    }
    const notice = page.locator('.busy-retry');
    await notice.getByText(/Still busy/).waitFor();
    assert.equal(calls.length, 5);
    await page.clock.runFor(60000);
    assert.equal(calls.length, 5, 'no further automatic retries');
    await notice.getByRole('button', { name: 'Try again', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('.busy-retry')?.textContent?.includes('attempt 6'));
    assert.equal(calls.length, 6);
  } finally { await browser.close(); }
});
