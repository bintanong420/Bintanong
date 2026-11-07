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
const { Conversation } = await import('../components/workspace/conversation.tsx');
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

function conversationHtml(presentation, sources = [{ sourceId: id, title: 'Synthetic Handbook' }]) {
  return renderToStaticMarkup(React.createElement(Conversation, {
    state: { messages: [{ id: 'answer-1', role: 'assistant', text: 'Full copy text.',
      answer: { status: 'answered', conditional: true, language: 'en', sources,
        notice: 'Not official university guidance.', presentation } }], pending: null },
    progress: '', onSource() {}, onClarify() {}, onEdit() {}, onRephrase() {}, canClarify: false,
  }));
}

test('single recovery answer has one source action and one quiet footer, without redundant labels', () => {
  const html = conversationHtml({ schemaVersion: 'bintanong-answer-presentation-v2', coverageState: 'complete',
    parts: [{ partId: 'r1', label: 'Recovery draft', evidenceNeed: 'structured', conditional: true,
      state: 'answered', sourceIds: [id], blocks: [{ type: 'summary', text: '### Plan D: Special classes and summer as needed\n\nAssuming the earlier courses were passed.' }] }] });
  assert.equal((html.match(/Sources \(1\)/g) ?? []).length, 1);
  assert.equal((html.match(/Not official university guidance\./g) ?? []).length, 1);
  assert.ok(!html.includes('<h3>Recovery draft</h3>'));
  assert.ok(!html.includes('This check depends'));
  assert.match(html, /Course checks use the details you shared/);
});

test('multi-part answer keeps part sources and offers only uncategorized sources in its footer', () => {
  const other = 'ev-' + 'b'.repeat(64);
  const html = conversationHtml({ schemaVersion: 'bintanong-answer-presentation-v2', coverageState: 'partial', parts },
    [{ sourceId: id, title: 'Handbook' }, { sourceId: other, title: 'Another source' }]);
  assert.equal((html.match(/answer-part-sources/g) ?? []).length, 1);
  assert.match(html, /Other sources \(1\)/);
  assert.ok(!html.includes('Sources (2)'));
});

test('plan table cells retain their header labels for a stacked narrow-screen view', () => {
  const html = conversationHtml({ schemaVersion: 'bintanong-answer-presentation-v2', coverageState: 'complete',
    parts: [{ partId: 'r1', label: 'Recovery draft', evidenceNeed: 'structured', state: 'answered', sourceIds: [],
      blocks: [{ type: 'summary', text: '| Term | Courses | Notes |\n| --- | --- | --- |\n| 2nd year, 2nd sem | A1 | Needs approval. |' }] }] });
  assert.match(html, /class="md-cell-label" aria-hidden="true">Term<\/span>/);
  assert.match(html, /role="columnheader"/);
  assert.match(html, /role="cell"/);
});

test.after(() => hooks.deregister());
