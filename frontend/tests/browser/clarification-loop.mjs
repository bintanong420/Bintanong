import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

test('clarification opens on request, preserves selected facts and does not restart on a bare fallback', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  assert.ok(url && ['localhost', '127.0.0.1'].includes(new URL(url).hostname));
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE });
    const page = await context.newPage(), submissions = [];
    const original = 'Ano ang prerequisites ng ZZ5?';
    await page.route('**/api/chat', async route => {
      submissions.push(route.request().postDataJSON());
      const first = submissions.length === 1;
      const text = first ? 'Prerequisites: ZZ 4/L and ZZ 3/L.' : 'Please clarify the missing information before a conclusion can be given.';
      const data = { status: 'clarification_needed', conditional: first, language: first ? 'taglish' : 'en',
        missingFields: first ? ['course_status'] : [], clarification: { scope: null,
          courses: first ? [{ code: 'ZZ 4/L', kind: 'completion' }, { code: 'ZZ 3/L', kind: 'completion' }] : [] } };
      const parts = [{ type: 'start', messageId: 'msg-fixture-' + submissions.length },
        { type: 'text-start', id: 'answer' }, { type: 'text-delta', id: 'answer', delta: text },
        { type: 'text-end', id: 'answer' }, { type: 'data-answer', data }, { type: 'finish', finishReason: 'stop' }];
      await route.fulfill({ status: 200, headers: { 'Content-Type': 'text/event-stream', 'x-vercel-ai-ui-message-stream': 'v1' },
        body: parts.map(part => 'data: ' + JSON.stringify(part) + '\n\n').join('') + 'data: [DONE]\n\n' });
    });
    await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
    await page.getByRole('textbox', { name: 'Your question' }).fill(original);
    await page.getByRole('button', { name: 'Send question', exact: true }).click();
    const dialog = page.getByRole('dialog');
    const continueCheck = page.getByRole('button', { name: 'Continue clarification', exact: true });
    await continueCheck.waitFor();
    await page.getByText('Prerequisites: ZZ 4/L and ZZ 3/L.', { exact: true }).waitFor();
    assert.equal(await dialog.count(), 0, 'listing prerequisites must not automatically open a grade check');
    assert.equal(submissions.length, 1);
    await continueCheck.click();
    await dialog.getByRole('heading', { name: 'Passed ka na ba sa ZZ 4/L?' }).waitFor();
    await dialog.getByRole('radio', { name: 'Passed na', exact: true }).check();
    await dialog.getByRole('button', { name: 'Continue', exact: true }).click();
    await dialog.getByRole('radio', { name: 'Hindi pa passed', exact: true }).check();
    await dialog.getByRole('button', { name: 'Continue', exact: true }).click();
    assert.equal(submissions.length, 1, 'choices and review do not send anything');
    await dialog.getByRole('button', { name: 'Confirm at send', exact: true }).click();
    await page.getByText('Please clarify the missing information before a conclusion can be given.', { exact: true }).waitFor();
    assert.equal(submissions.length, 2);
    assert.equal(submissions[1].messages[0].parts[0].text, original + '\n\nPassed na ako sa ZZ 4/L.\nHindi pa ako passed sa ZZ 3/L.');
    assert.equal(await dialog.count(), 0, 'no invented details dialog');
    assert.equal(await page.getByRole('button', { name: /Continue clarification|Continue ang clarification|Ituloy ang paglilinaw/ }).count(), 0);
    assert.equal(await page.getByRole('textbox', { name: 'Your question' }).isEnabled(), true);
  } finally { await browser.close(); }
});
