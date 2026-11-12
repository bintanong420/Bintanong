import assert from 'node:assert/strict';
import test from 'node:test';
import { recordHeading } from '../lib/review-state.ts';

test('a heading path shows its nearest heading, with the two headings above it as context', () => {
  assert.deepEqual(recordHeading('THE CONSTITUTION / PREAMBLE / ARTICLE XI / The Executive Department / Section 3. Duties'),
    { heading: 'Section 3. Duties', context: 'ARTICLE XI / The Executive Department' });
});

test('a plain title is its own heading and has no context', () => {
  assert.deepEqual(recordHeading('Shifting of programs'), { heading: 'Shifting of programs', context: '' });
  assert.deepEqual(recordHeading(' A /  / B '), { heading: 'B', context: 'A' });
  assert.deepEqual(recordHeading(''), { heading: '', context: '' });
});
