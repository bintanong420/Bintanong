import assert from 'node:assert/strict';
import test from 'node:test';
import { recordHeading } from '../lib/review-state.ts';

test('a heading path shows only its last heading', () => {
  assert.equal(recordHeading('THE CONSTITUTION / PREAMBLE / ARTICLE XI / The Executive Department / Section 3. Duties'), 'Section 3. Duties');
});

test('a plain title is its own heading; empty parts are skipped', () => {
  assert.equal(recordHeading('Shifting of programs'), 'Shifting of programs');
  assert.equal(recordHeading(' A /  / B '), 'B');
  assert.equal(recordHeading(''), '');
});
