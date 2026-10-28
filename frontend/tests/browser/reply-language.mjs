import { dismissInitialScope } from './scope-helper.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

test('validated Taglish language reaches notices, clarification replies and retained choices', async () => {
  const url = process.env.BINTANONG_BROWSER_URL;
  assert.ok(url && ['127.0.0.1', 'localhost'].includes(new URL(url).hostname));
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const context = await browser.newContext({ storageState: process.env.BINTANONG_BROWSER_STATE });
    const page = await context.newPage(), submissions = [];
    page.setDefaultTimeout(5000);
    await page.route('**/api/chat', async route => {
      submissions.push(route.request().postDataJSON());
      const parts = [{ type: 'start', messageId: 'synthetic-language' }, { type: 'text-start', id: 'answer' },
        { type: 'text-delta', id: 'answer', delta: 'May kulang pang course details.' }, { type: 'text-end', id: 'answer' },
        { type: 'data-answer', data: { status: 'clarification_needed', conditional: true, language: 'taglish',
          missingFields: ['course_status'], clarification: { courses: [{ code: 'Z 4/L', kind: 'completion' }],
            scope: { programId: 'bscs', curriculumId: 'bscs-2018' } } } }, { type: 'finish', finishReason: 'stop' }];
      await route.fulfill({ headers: { 'Content-Type': 'text/event-stream', 'x-vercel-ai-ui-message-stream': 'v1' },
        body: parts.map(part => 'data: ' + JSON.stringify(part) + '\n\n').join('') + 'data: [DONE]\n\n' });
    });
    await page.goto(new URL('/chat', url).href, { waitUntil: 'networkidle' });
    await dismissInitialScope(page);
    await page.getByRole('textbox', { name: 'Your question', exact: true }).fill('Pwede ko bang kunin ang Z 5/L?');
    await page.getByRole('button', { name: 'Send question', exact: true }).click();
    await page.getByRole('button', { name: 'Continue clarification', exact: true }).waitFor();
    assert.equal(await page.locator('.answer-notice').innerText(), 'May kulang pang details');
    await page.getByRole('button', { name: 'Continue clarification', exact: true }).click();
    const dialog = page.getByRole('dialog', { name: 'May kulang pang details', exact: true });
    await dialog.getByRole('heading', { name: 'Passed ka na ba sa Z 4/L?', exact: true }).waitFor();
    await dialog.getByRole('radio', { name: 'Passed na', exact: true }).check();
    await dialog.getByRole('button', { name: 'Continue', exact: true }).click();
    await dialog.getByRole('button', { name: 'Confirm at send', exact: true }).click();
    await page.waitForFunction(() => !document.querySelector('.working-card'));
    assert.equal(submissions[1].messages[0].parts[0].text, 'Pwede ko bang kunin ang Z 5/L?\n\nPassed na ako sa Z 4/L.');
    await page.getByRole('button', { name: 'You supplied (1)', exact: true }).click();
    await page.getByRole('dialog', { name: 'You supplied', exact: true }).getByText('Passed na ako sa Z 4/L.', { exact: true }).waitFor();
  } finally { await browser.close(); }
});
