import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { readFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import test from 'node:test';
import { parseConnection } from '../lib/review-state.ts';

const launchFile = process.env.BINTANONG_REVIEW_TEST_LAUNCH;

test('switching documents resets the field draft and keeps the review controls usable',
  { skip: !launchFile, timeout: 45000 }, async t => {
    const url = (await readFile(launchFile, 'utf8')).trim();
    const connection = parseConnection(new URL(url).hash);
    assert.equal(new URL(url).origin, 'http://127.0.0.1:3001');
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
      const response = await send('Runtime.evaluate', { expression, returnByValue: true });
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
    assert.equal(errors.length, 0);
  });
