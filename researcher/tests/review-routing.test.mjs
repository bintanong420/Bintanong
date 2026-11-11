import assert from 'node:assert/strict';
import test from 'node:test';
import { itemForTarget, parseReviewPath, reviewPath, targetForItem } from '../lib/review-path.ts';

const items = [{ id: 'handbook:grading', document_id: 'handbook' },
  { id: 'bscs:prospectus', document_id: 'bscs', prospectus_candidate: true }];

test('a review link selects its record, and a record has its own link', () => {
  assert.equal(itemForTarget(items, { kind: 'policy', item: 'handbook:grading' })?.id, 'handbook:grading');
  assert.equal(itemForTarget(items, { kind: 'prospectus', document: 'bscs', question: 'S1-01' })?.id, 'bscs:prospectus');
  // a policy link never opens a prospectus record, and the reverse
  assert.equal(itemForTarget(items, { kind: 'policy', item: 'bscs:prospectus' }), undefined);
  assert.equal(itemForTarget(items, { kind: 'prospectus', document: 'handbook' }), undefined);
  assert.equal(itemForTarget(items, { kind: 'home' }), undefined);
  assert.deepEqual(targetForItem(items[0]), { kind: 'policy', item: 'handbook:grading' });
  assert.deepEqual(targetForItem(items[1], 'S1-01'), { kind: 'prospectus', document: 'bscs', question: 'S1-01' });
});
import { authorizeReview, bodyLimit } from '../lib/review-access.ts';

test('only the PDF upload path may send more than 1 MiB', () => {
  assert.equal(bodyLimit(['intake', 'upload']), 128 * 1024 * 1024);
  for (const path of [['decision'], ['intake', 'uploads'], ['intake', 'upload', 'x'], ['upload'], ['x', 'intake', 'upload']]) {
    assert.equal(bodyLimit(path), 1024 * 1024);
  }
});

test('review paths round-trip, including ids that need escaping', () => {
  assert.deepEqual(parseReviewPath('/review'), { kind: 'home' });
  assert.deepEqual(parseReviewPath('/review/'), { kind: 'home' });
  assert.deepEqual(parseReviewPath('/review/policy/handbook%3Agrading%2F1'), { kind: 'policy', item: 'handbook:grading/1' });
  assert.deepEqual(parseReviewPath('/review/prospectus/bscs-2018'), { kind: 'prospectus', document: 'bscs-2018' });
  assert.deepEqual(parseReviewPath('/review/prospectus/bscs-2018/S1-02%3Aprereq'),
    { kind: 'prospectus', document: 'bscs-2018', question: 'S1-02:prereq' });
  for (const target of [{ kind: 'policy', item: 'handbook:grading/1' }, { kind: 'prospectus', document: 'a b', question: 'S1-02:prereq' },
    { kind: 'prospectus', document: 'bscs' }, { kind: 'home' }]) {
    assert.deepEqual(parseReviewPath(reviewPath(target)), target);
  }
});

test('unknown or malformed review paths fall back to the review home', () => {
  for (const path of ['/', '/chat', '/review/unknown/x', '/review/policy', '/review/policy/a/b', '/review/prospectus',
    '/review/prospectus/a/b/c', '/review/policy/%E0%A4%A']) {
    assert.deepEqual(parseReviewPath(path), { kind: 'home' }, path);
  }
});

const token = 'abcdefghijklmnop0123';
const base = { token, cookie: token, method: 'GET', uiOrigin: 'http://127.0.0.1:3050' };

test('the review API proxy needs the launch cookie', () => {
  assert.equal(authorizeReview(base), null);
  assert.match(authorizeReview({ ...base, cookie: undefined }), /launch link/);
  assert.match(authorizeReview({ ...base, cookie: token + 'x' }), /launch link/);
  assert.match(authorizeReview({ ...base, token: undefined, cookie: undefined }), /not configured/);
  assert.match(authorizeReview({ ...base, token: 'short' }), /not configured/);
});

test('changes must come from the review page itself', () => {
  const post = { ...base, method: 'POST' };
  assert.equal(authorizeReview({ ...post, origin: 'http://127.0.0.1:3050', fetchSite: 'same-origin' }), null);
  assert.match(authorizeReview({ ...post, origin: 'https://attacker.example', fetchSite: 'cross-site' }), /review page/);
  assert.match(authorizeReview({ ...post, origin: undefined }), /review page/);
  assert.match(authorizeReview({ ...post, origin: 'http://127.0.0.1:3050', fetchSite: 'cross-site' }), /review page/);
  // reads from another site are refused too, so page images and records cannot be embedded elsewhere
  assert.match(authorizeReview({ ...base, fetchSite: 'cross-site' }), /review page/);
});
