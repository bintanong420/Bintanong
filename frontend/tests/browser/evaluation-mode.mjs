import test from 'node:test';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

// The owner works only on this page: all 72 listed, click or type, read both lists and the key, mark, reload.
const languages = ['EN', 'TG', 'TL'];
const key = { key_id: 'row-1', key_status: 'keyed', relevant_chunk_ids: ['a'], expected_facts: ['Synthetic fact'],
  expected_route: 'RAG', expected_outcome: 'answer', source_note: 'Synthetic note' };
const noKey = { key_id: null, key_status: 'human_judged', relevant_chunk_ids: [], expected_facts: [], expected_route: null,
  expected_outcome: null, source_note: null };
const cases = Array.from({ length: 24 }, (_, index) => languages.map(language => ({
  case_id: `${index < 10 ? 'A' : 'B'}${String(index + 1).padStart(2, '0')}-${language}`, row: index + 1,
  subset: index < 10 ? 'A' : 'B', category: 'Synthetic', language, question: `Synthetic question ${index + 1} ${language}?`,
  key: index === 0 ? key : noKey }))).flat();
const chunk = (id, rank, sent = false) => ({ rank, chunk_id: id, similarity: .9 - rank / 10, text: `Synthetic clause ${id}.`,
  source_label: 'Synthetic.pdf', pages: [3], section_path: [], sent_to_writer: sent, attached_count: 0 });

async function open(width = 1280) {
  const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await browser.newPage({ viewport: { width, height: 844 } });
  page.setDefaultTimeout(5000);
  const state = { runs: [], fail: false };
  const allowed = route => route.request().headers()['x-bintanong-evaluator'] === 'synthetic-passcode';
  await page.route('**/api/evaluation/cases', route => allowed(route)
    ? route.fulfill({ json: { code_commit: 'abc1234', cases } })
    : route.fulfill({ status: 404, json: { error: 'route_unavailable' } }));
  await page.route('**/api/evaluation/runs', route => route.fulfill({ json: { runs: state.runs } }));
  await page.route('**/api/evaluation/run', route => {
    const { question } = route.request().postDataJSON();
    const match = cases.find(item => item.question === question);
    const failed = state.fail;
    const run = { record_type: 'run', run_id: `run-${String(state.runs.length).padStart(16, '0')}`, case_id: match?.case_id ?? null, question,
      outcome: failed ? 'infrastructure_error' : 'completed', error: failed ? 'tool_error' : null, route_label: failed ? null : 'RAG',
      topics: failed ? [] : [{ subject_id: 'synthetic_topic', claims: [] }],
      answer: failed ? null : { status: 'answered', language: 'en', text: 'Synthetic answer.', reason: null, sources: ['Synthetic.pdf, p.3'] },
      searches: failed ? [] : [{ query: question, subject_id: 'synthetic_topic', topic_bound: [chunk('a', 1, true)], all_chunks: [chunk('x', 1), chunk('a', 2, true), chunk('y', 3)] }],
      key: match?.key ?? null, judgment: null };
    state.runs.push(run);
    return route.fulfill({ json: run });
  });
  await page.route('**/api/evaluation/runs/*/judgment', route => {
    const id = route.request().url().split('/').at(-2);
    state.runs.find(run => run.run_id === id).judgment = route.request().postDataJSON();
    return route.fulfill({ json: {} });
  });
  await page.goto(new URL('/dev/evaluation', process.env.BINTANONG_BROWSER_URL).href, { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: 'I understand', exact: true }).click();
  return { browser, page, state };
}

async function unlock(page, passcode = 'synthetic-passcode') {
  await page.getByLabel('Passcode').fill(passcode);
  await page.getByRole('button', { name: 'Open', exact: true }).click();
}

test('a wrong passcode says so and shows no queries', async () => {
  const { browser, page } = await open();
  try {
    await unlock(page, 'wrong');
    await page.getByText('Evaluation mode is off or the passcode is wrong.').waitFor();
    assert.equal(await page.getByText('Synthetic question 1 EN?').count(), 0);
  } finally { await browser.close(); }
});

test('all 72 queries are listed, and clicking one fills the box and shows its key', async () => {
  const { browser, page } = await open();
  try {
    await unlock(page);
    const list = page.getByRole('navigation', { name: 'The 72 benchmark queries' });
    await list.waitFor();
    assert.equal(await list.getByRole('button').count(), 72);
    await list.getByRole('button', { name: /Synthetic question 1 EN\?/ }).click();
    assert.equal(await page.getByLabel('Query').inputValue(), 'Synthetic question 1 EN?');
    await page.getByText('Synthetic fact').waitFor();
    assert.match(await page.locator('header').innerText(), /Ran 0\/72 · Marked 0\/72/);
  } finally { await browser.close(); }
});

test('a typed query outside the 72 is warned about', async () => {
  const { browser, page } = await open();
  try {
    await unlock(page);
    await page.getByLabel('Query').fill('Synthetic typo?');
    await page.getByText('Not in the 72, will not be scored.').waitFor();
    await page.getByLabel('Query').fill('  synthetic question 2 tl? ');
    assert.equal(await page.getByText('Not in the 72, will not be scored.').count(), 0);
  } finally { await browser.close(); }
});

test('a run shows both lists, and marks are saved and return after a reload', async () => {
  const { browser, page } = await open();
  try {
    await unlock(page);
    await page.getByLabel('Query').fill('Synthetic question 1 EN?');
    await page.getByRole('button', { name: 'Run query', exact: true }).click();
    await page.getByText('Synthetic answer.', { exact: true }).waitFor();
    const topic = page.getByRole('region', { name: 'Topic-bound' });
    const everything = page.getByRole('region', { name: 'All chunks' });
    assert.equal(await topic.getByRole('article').count(), 1);
    assert.equal(await everything.getByRole('article').count(), 3);
    assert.equal(await everything.getByText('In answer key').count(), 1);
    await topic.getByRole('group').getByRole('button', { name: 'Yes', exact: true }).click();
    assert.equal(await everything.getByRole('article').nth(1).getByRole('button', { name: 'Yes', exact: true }).getAttribute('aria-pressed'), 'true');
    await page.getByRole('group', { name: 'Answer mark' }).getByRole('button', { name: 'Partial', exact: true }).click();
    await page.getByLabel('Note (optional)').fill('Synthetic note text');
    await page.getByRole('button', { name: 'Save marks', exact: true }).click();
    await page.getByRole('status').getByText('Saved', { exact: true }).waitFor();
    assert.match(await page.locator('header').innerText(), /Ran 1\/72 · Marked 1\/72/);
    await page.reload({ waitUntil: 'networkidle' });
    await unlock(page);
    await page.getByRole('navigation', { name: 'The 72 benchmark queries' }).getByRole('button', { name: /Synthetic question 1 EN\?/ }).click();
    assert.equal(await page.getByRole('group', { name: 'Answer mark' }).getByRole('button', { name: 'Partial', exact: true }).getAttribute('aria-pressed'), 'true');
    assert.equal(await page.getByLabel('Note (optional)').inputValue(), 'Synthetic note text');
    assert.match(await page.locator('header').innerText(), /Marked 1\/72/);
  } finally { await browser.close(); }
});

test('a failed run says so and does not count as done', async () => {
  const { browser, page, state } = await open();
  try {
    await unlock(page);
    state.fail = true;
    const list = page.getByRole('navigation', { name: 'The 72 benchmark queries' });
    const item = list.getByRole('button', { name: /Synthetic question 3 TG\?/ });
    await item.click();
    await page.getByRole('button', { name: 'Run query', exact: true }).click();
    await page.getByText(/This run failed \(tool_error\)/).waitFor();
    assert.match(await item.innerText(), /Failed, run again/);
    assert.match(await page.locator('header').innerText(), /Ran 0\/72/);
  } finally { await browser.close(); }
});

test('nothing scrolls sideways at phone width', async () => {
  const { browser, page } = await open(375);
  try {
    await unlock(page);
    await page.getByLabel('Query').fill('Synthetic question 1 EN?');
    await page.getByRole('button', { name: 'Run query', exact: true }).click();
    await page.getByText('Synthetic answer.', { exact: true }).waitFor();
    const widths = await page.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
    assert.ok(widths[0] <= widths[1], `page is ${widths[0]}px wide in a ${widths[1]}px window`);
  } finally { await browser.close(); }
});
