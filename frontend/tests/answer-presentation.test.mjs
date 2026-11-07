import test from 'node:test';
import assert from 'node:assert/strict';
import { registerHooks } from 'node:module';
import { readFileSync } from 'node:fs';
import babel from 'next/dist/compiled/babel/core.js';
import typescriptPreset from 'next/dist/compiled/babel/preset-typescript.js';
import reactPreset from 'next/dist/compiled/babel/preset-react.js';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';

// Load the real TSX components without a bundler or browser dependency.
const root = new URL('../', import.meta.url);
const hooks = registerHooks({
  resolve(specifier, context, next) {
    if (specifier.startsWith('@/') || specifier.startsWith('./')) {
      const base = specifier.startsWith('@/') ? new URL(specifier.slice(2), root) : new URL(specifier, context.parentURL);
      for (const suffix of ['.tsx', '.ts']) {
        try { readFileSync(new URL(base.href + suffix)); return { url: base.href + suffix, shortCircuit: true }; } catch {}
      }
    }
    return next(specifier, context);
  },
  load(url, context, next) {
    if (url.startsWith(root.href) && /\.(tsx|ts)$/.test(url)) return {
      format: 'module', shortCircuit: true,
      source: babel.transformSync(readFileSync(new URL(url), 'utf8'), {
        filename: new URL(url).pathname, babelrc: false, configFile: false,
        presets: [typescriptPreset, [reactPreset, { runtime: 'automatic' }]],
      }).code,
    };
    return next(url, context);
  },
});
const { AnswerPresentation } = await import('../components/workspace/answer-presentation.tsx');
const id = 'ev-' + 'a'.repeat(64);
const parts = [
  { partId: 'r1', label: 'Part 1', evidenceNeed: 'document', state: 'answered',
    blocks: [{ type: 'explanation', text: '<script>alert(1)</script>\n\n1. Ask the office.\n2. Submit the form.' }], sourceIds: [id] },
  { partId: 'r2', label: 'Part 2', evidenceNeed: 'document', state: 'unavailable',
    blocks: [{ type: 'limitation', text: 'Fee not established.' }], sourceIds: [] },
];

test('real renderer exposes partial status, ordered steps, source controls and safe escaped text', () => {
  const html = renderToStaticMarkup(React.createElement(AnswerPresentation, {
    presentation: { schemaVersion: 'bintanong-answer-presentation-v2', coverageState: 'partial', parts },
    language: 'en', sources: [{ sourceId: id, title: 'Synthetic Handbook, p.1' }], onSource() {},
  }));
  assert.match(html, /Some parts could not be answered/);
  assert.match(html, /aria-label="Part 2: Information unavailable"/);
  assert.match(html, /<ol>/);
  assert.match(html, /<button type="button"/);
  assert.equal((html.match(/answer-part-sources/g) ?? []).length, 1);
  assert.ok(!html.includes('<script>'));
  assert.match(html, /&lt;script&gt;/);
});

test('Taglish status and constrained wrapping are retained without introducing certification copy', () => {
  const html = renderToStaticMarkup(React.createElement(AnswerPresentation, {
    presentation: { schemaVersion: 'bintanong-answer-presentation-v2', coverageState: 'partial', parts },
    language: 'taglish', sources: [], onSource() {},
  }));
  assert.match(html, /Wala pang reviewed information/);
  assert.ok(!html.includes('Approved'));
  const css = readFileSync(new URL('../app/styles.css', import.meta.url), 'utf8');
  assert.match(css, /\.answer-presentation[^}]+min-inline-size: 0; overflow-wrap: anywhere;/);
  assert.match(css, /\.answer-part-header[^}]+flex-wrap: wrap/);
  assert.match(css, /\.answer-part-sources:focus-visible/);
});
test('recovery details are native disclosures while material warnings stay visible', () => {
  const html = renderToStaticMarkup(React.createElement(AnswerPresentation, {
    presentation: { schemaVersion: 'bintanong-answer-presentation-v2', coverageState: 'complete', parts: [
      { partId: 'r1', label: 'Recovery draft', evidenceNeed: 'structured', state: 'answered', sourceIds: [],
        blocks: [{ type: 'limitation', text: 'Load exceeds the prescribed total.' },
          { type: 'details', title: 'Other drafts', text: '<script>unsafe()</script>\n\nAlternative.' }] },
    ] }, language: 'en', sources: [], onSource() {},
  }));
  assert.match(html, /<details[^>]*><summary[^>]*>Other drafts<\/summary>/);
  assert.ok(html.indexOf('Load exceeds') < html.indexOf('<details'));
  assert.ok(!html.includes('<script>'));
  assert.ok(!html.includes('<details open'));
});

test.after(() => hooks.deregister());
