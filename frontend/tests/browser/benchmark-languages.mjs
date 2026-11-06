// Serial live evaluation: use only during an agreed model window and write evidence to an ignored directory.
// Input rows: positive id, curriculumId, questions {en, fil, taglish}; optional startYear and matchedLanguageSubset.
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { performance } from 'node:perf_hooks';
import { pathToFileURL } from 'node:url';

const root = process.env.BINTANONG_BENCHMARK_OUT;
const base = process.env.BINTANONG_BROWSER_URL;
assert.ok(root && base && process.env.BINTANONG_BENCHMARK_INPUT && process.env.PLAYWRIGHT_MODULE);
assert.ok(['localhost', '127.0.0.1'].includes(new URL(base).hostname));
assert.equal(new URL(base).protocol, 'http:');
const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
const dataset = JSON.parse(await readFile(process.env.BINTANONG_BENCHMARK_INPUT, 'utf8'));
const resultName = 'live-results';
assert.ok(dataset.rows.length > 0);
assert.equal(new Set(dataset.rows.map(row => row.id)).size, dataset.rows.length);
for (const row of dataset.rows) {
  assert.ok(Number.isSafeInteger(row.id) && row.id > 0 && row.curriculumId);
  assert.ok(['en', 'fil', 'taglish'].every(language => typeof row.questions[language] === 'string'
    && row.questions[language].trim()));
}
const rosterResponse = await fetch(new URL('/api/curricula', base));
assert.ok(rosterResponse.ok);
const roster = (await rosterResponse.json()).curricula;
const rows = [];
const browser = await chromium.launch({ channel: 'msedge', headless: true });
await mkdir(`${root}/live`, { recursive: true });
try {
  for (const item of dataset.rows) {
    const languages = ['taglish', 'en', 'fil'];
    const rotation = (item.id - 1) % 3;
    const order = [...languages.slice(rotation), ...languages.slice(0, rotation)];
    for (const language of order) {
      const scope = roster.find(c => c.curriculumId === item.curriculumId);
      assert.ok(scope);
      const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
      const page = await context.newPage();
      page.setDefaultTimeout(15000);
      page.setDefaultNavigationTimeout(45000);
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const key = `${String(item.id).padStart(2, '0')}-${language}`;
      const row = { id: item.id, language, question: item.questions[language], scope,
        matchedLanguageSubset: item.matchedLanguageSubset === true, order, errors };
      try {
        await page.route('**/api/chat', async route => {
          const body = route.request().postDataJSON();
          assert.equal(body.curriculumId, scope.curriculumId);
          row.request = body;
          await route.continue();
        });
        await page.goto(`${base}/chat`, { waitUntil: 'networkidle' });
        const privacy = page.getByRole('button', { name: 'I understand', exact: true });
        await privacy.click();
        const picker = page.getByRole('dialog', { name: 'Choose your program', exact: true });
        await picker.waitFor({ state: 'visible' });
        await picker.getByRole('searchbox').fill(scope.programName);
        await picker.locator('.program-option').filter({ hasText: scope.programName }).first().click();
        const year = page.getByRole('dialog', { name: 'When did you start?', exact: true });
        if (roster.filter(c => c.programId === scope.programId).length > 1) {
          await year.waitFor({ state: 'visible' });
          await year.getByRole('radio', { name: item.startYear ?? 'Before 2023', exact: true }).check();
          await year.getByRole('button', { name: 'Use this program', exact: true }).click();
        }
        const input = page.getByRole('textbox', { name: 'Your question', exact: true });
        await input.fill(row.question);
        const responsePromise = page.waitForResponse(response => new URL(response.url()).pathname === '/api/chat', { timeout: 240000 });
        const started = performance.now();
        await page.getByRole('button', { name: 'Send question', exact: true }).click();
        const response = await responsePromise;
        row.httpStatus = response.status();
        const raw = await response.text();
        await writeFile(`${root}/live/${key}.sse`, raw);
        const parts = raw.split('\n').filter(line => line.startsWith('data: ') && !line.includes('[DONE]'))
          .map(line => JSON.parse(line.slice(6)));
        row.metadata = parts.find(part => part.type === 'data-answer')?.data;
        row.answer = parts.filter(part => part.type === 'text-delta').map(part => part.delta).join('');
        await page.getByRole('article', { name: 'Bintanong response', exact: true }).last().waitFor({ timeout: 240000 });
        await page.waitForFunction(() => !document.querySelector('.working-card'), null, { timeout: 240000 });
        row.submitToRenderSeconds = (performance.now() - started) / 1000;
        row.overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
        row.sources = [];
        for (const source of parts.filter(part => part.type === 'source-document')) {
          const sourceResponse = await context.request.get(`${base}/api/sources/${source.sourceId}`);
          row.sources.push({ ...source, httpStatus: sourceResponse.status(),
            evidence: sourceResponse.ok() ? await sourceResponse.json() : null });
        }
        row.screenshot = `live/${key}.png`;
        await page.screenshot({ path: `${root}/${row.screenshot}`, fullPage: true });
      } catch (error) {
        row.error = error.message;
        await page.screenshot({ path: `${root}/live/${key}-error.png`, fullPage: true }).catch(() => {});
      }
      rows.push(row);
      await writeFile(`${root}/${resultName}.json`, JSON.stringify({ pdf_sha256: dataset.pdf_sha256,
        composition: dataset.composition ?? 'local HTTP; fresh browser contexts; record server composition separately', rows }, null, 2));
      console.log(key, row.metadata?.status ?? 'ERROR', row.submitToRenderSeconds?.toFixed(1) ?? '', row.error ?? '');
      await context.close();
    }
  }
} finally { await browser.close(); }
assert.equal(rows.length, dataset.rows.length * 3);
process.exitCode = rows.some(row => row.error || row.errors.length) ? 1 : 0;
