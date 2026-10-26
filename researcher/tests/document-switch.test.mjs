import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import test from 'node:test';
import { parseConnection } from '../lib/review-state.ts';

const launchFile = process.env.BINTANONG_REVIEW_TEST_LAUNCH;

test('switching documents resets the field draft and keeps the review controls usable',
  { skip: !launchFile, timeout: 45000 }, async t => {
    const url = (await readFile(launchFile, 'utf8')).trim();
    const connection = parseConnection(new URL(url).hash);
    assert(['http://127.0.0.1:3001', 'http://127.0.0.1:3002'].includes(new URL(url).origin));
    const response = await fetch(connection.api + '/api/state', {
      headers: { 'x-review-token': connection.token },
    });
    assert(response.ok, 'use the current running review session launch link');
    const state = await response.json();
    const first = state.items[0];
    const different = state.items.findIndex(row => row.document_id !== first.document_id
      && JSON.stringify(row.fields.map(f => f.name)) !== JSON.stringify(first.fields.map(f => f.name)));
    assert(different > 0, 'use a packet with two documents and different field names');
    const profile = path.join(path.dirname(launchFile), 'document-switch-browser', String(Date.now()));
    await mkdir(profile, { recursive: true });
    const browser = spawn(process.env.BINTANONG_REVIEW_TEST_CHROME
      ?? 'C:/Program Files/Google/Chrome/Application/chrome.exe', [
      '--headless=new', '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=0',
      '--user-data-dir=' + profile, '--no-first-run', '--disable-background-networking', url,
    ], { stdio: 'ignore' });
    let ws, sequence = 0;
    const pending = new Map(), errors = [];
    t.after(async () => {
      if (ws?.readyState === WebSocket.OPEN) await send('Browser.close').catch(() => {});
      ws?.close(); browser.kill();
    });
    async function until(run) {
      const end = Date.now() + 12000;
      while (Date.now() < end) {
        const value = await run();
        if (value) return value;
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      throw Error('Document review did not reach the expected state');
    }
    const port = await until(async () => {
      try { return (await readFile(path.join(profile, 'DevToolsActivePort'), 'utf8')).split('\n')[0]; }
      catch { return null; }
    });
    const page = await until(async () => {
      const pages = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
      return pages.find(page => page.type === 'page' && page.url.startsWith(new URL(url).origin + '/'));
    });
    ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
    ws.onmessage = event => {
      const message = JSON.parse(event.data);
      const call = pending.get(message.id);
      if (call) { pending.delete(message.id); message.error ? call.reject(Error(message.error.message)) : call.resolve(message.result); }
      if (message.method === 'Runtime.exceptionThrown') errors.push(message.params.exceptionDetails);
    };
    async function send(method, params = {}) {
      const id = ++sequence;
      return new Promise((resolve, reject) => {
        const timer = setTimeout(() => { pending.delete(id); reject(Error(method + ' timed out')); }, 12000);
        pending.set(id, { resolve: value => { clearTimeout(timer); resolve(value); }, reject });
        ws.send(JSON.stringify({ id, method, params }));
      });
    }
    async function evaluate(expression) {
      const response = await send('Runtime.evaluate', { expression, returnByValue: true, userGesture: true });
      assert(!response.exceptionDetails, JSON.stringify(response.exceptionDetails));
      return response.result.value;
    }
    await send('Runtime.enable');
    await send('Page.enable');
    await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
    try {
      await until(() => evaluate("document.querySelectorAll('.queue-item').length > 0 && !!document.querySelector('form')"));
    } catch (error) {
      throw Error(await evaluate('JSON.stringify({url:location.href,text:document.body.innerText})'), { cause: error });
    }
    for (const index of [different, 0]) {
      await evaluate(`document.querySelectorAll('.queue-item')[${index}].click()`);
      const expected = state.items[index].fields.map(f => f.name + ' content decision');
      await until(async () => {
        assert.equal(errors.length, 0, 'record switch threw a browser exception');
        const actual = await evaluate("[...document.querySelectorAll('form select[aria-label$=\" content decision\"]')].map(e=>e.getAttribute('aria-label'))");
        return JSON.stringify(actual) === JSON.stringify(expected);
      });
      assert(await evaluate("!!document.querySelector('[aria-label=\"Audience applicability\"]') && !!document.querySelector('button[type=submit]')"));
    }
    assert.equal(await evaluate("document.querySelectorAll('select[multiple]').length"), 0, 'use the searchable related-record picker');
    const relatedIndex = state.items.findIndex((row, index) => index !== 0 && row.document_id === first.document_id
      && row.fields.some(field => field.spans.some(span => span.page === first.fields[0].locator.physical_pages[0])));
    assert(relatedIndex > 0);
    await evaluate("document.querySelector('.record-picker').open = true");
    await evaluate("document.querySelector('.record-picker input[type=search]').focus()");
    await send('Input.insertText', { text: state.items[relatedIndex].title });
    await until(() => evaluate("document.querySelectorAll('.record-choice').length > 0"));
    await evaluate("document.querySelector('.record-choice input').click()");
    await until(() => evaluate("document.querySelectorAll('.related-highlight').length > 0"));
    assert(await evaluate("document.querySelector('.source-legend').textContent.includes('Related context')"));
    assert(await evaluate("!!document.querySelector('.companion .context-pages button')"));
    await evaluate("document.querySelector('.companion .context-pages button').click()");
    await until(() => evaluate("document.querySelector('.pdf-page img')?.complete"));
    if (process.env.BINTANONG_REVIEW_TEST_WRITE === 'isolated-rehearsal') {
      assert.match(state.researcher, /^Automated rehearsal/);
      assert.equal(new URL(url).port, '3002');
      await evaluate("(() => {const e=document.querySelector('[aria-label=\"Audience applicability\"]');e.value='undergraduate';e.dispatchEvent(new Event('change',{bubbles:true}));})()");
      await evaluate("[...document.querySelectorAll('button')].find(b=>b.textContent==='Mark the missed area').click()");
      const point = await evaluate("(() => {const p=document.querySelector('.pdf-page').getBoundingClientRect();const s=document.querySelector('.page-scroll').getBoundingClientRect();return {x:p.left+p.width*.2,y:Math.max(p.top,s.top)+30};})()");
      await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...point, button: 'left', buttons: 1, clickCount: 1 });
      await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: point.x + 100, y: point.y + 60, button: 'left', buttons: 1 });
      await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: point.x + 100, y: point.y + 60, button: 'left', clickCount: 1 });
      assert(await evaluate("!!document.querySelector('.marked-region')"));
      await evaluate("[...document.querySelectorAll('button')].find(b=>b.textContent==='Report missing content').click()");
      await until(() => evaluate("document.querySelector('.feedback-dialog')?.open"));
      await evaluate("document.querySelector('[aria-label=\"Missing source wording\"]').focus()");
      await send('Input.insertText', { text: String(first.fields[0].original_value) });
      await evaluate("document.querySelector('[aria-label=\"Missing content note\"]').focus()");
      const note = 'Automated rehearsal only: tests feedback persistence, not a source-content finding.';
      await send('Input.insertText', { text: note });
      await evaluate("document.querySelector('.feedback-dialog button[type=submit]').click()");
      await until(() => evaluate("!document.querySelector('.feedback-dialog') && document.querySelector('[role=status]')?.textContent.includes('Missing-content note saved')"));
      assert.equal(await evaluate("document.querySelector('[aria-label=\"Audience applicability\"]').value"), 'undergraduate', 'saving feedback must retain the unsaved field review');
      assert(await evaluate("document.querySelectorAll('.companion').length > 0"), 'saving feedback must retain unsaved context links');
      const after = await (await fetch(connection.api + '/api/state', { headers: { 'x-review-token': connection.token } })).json();
      assert.deepEqual(after.items, state.items);
      const report = after.feedback.at(-1);
      assert.equal(report.note, note); assert.equal(report.status, 'pending'); assert.equal(report.region.length, 4);
      const downloads = path.join(profile, 'downloads');
      await mkdir(downloads);
      await send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: downloads });
      await evaluate("[...document.querySelectorAll('button')].find(b=>b.textContent==='Download my reviews').click()");
      const exported = await until(async () => { try { return JSON.parse(await readFile(path.join(downloads,'review-decisions.json'),'utf8')); } catch { return null; } });
      assert.equal(exported.feedback.at(-1).note, note);
      assert(exported.readings.every(row => row.fields.every(field => field.decision === 'pending')));
      await evaluate("[...document.querySelectorAll('button')].find(b=>b.textContent==='Saved reviews').click()");
      await until(() => evaluate("document.querySelector('dialog')?.textContent.includes('Pending feedback')"));
      await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
      await until(() => evaluate("!document.querySelector('dialog')"));
      await evaluate("(() => {const p=document.querySelector('.decision-pane');const r=document.querySelector('.related-records');p.scrollTop += r.getBoundingClientRect().top-p.getBoundingClientRect().top;document.querySelector('.companion details').open=true;window.scrollTo(0,0);})()");
      await writeFile(path.join(path.dirname(launchFile),'related-context-desktop.png'), Buffer.from((await send('Page.captureScreenshot', { format: 'png' })).data, 'base64'));
      for (const width of [390,720]) {
        await send('Emulation.setDeviceMetricsOverride', { width, height: 844, deviceScaleFactor: 1, mobile: width === 390 });
        assert(await evaluate('document.documentElement.scrollWidth <= innerWidth'), `review workspace overflows at ${width}px`);
      }
    }
    assert.equal(errors.length, 0);
  });
