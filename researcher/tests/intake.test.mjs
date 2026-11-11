import assert from 'node:assert/strict';
import test from 'node:test';
import { buildPayload, checkUploadFile, isNoPacketError, MAX_UPLOAD_BYTES, prepareLabel, shouldPoll, uploadQuery,
  validateUploadFields, withheldReason } from '../lib/intake.ts';

test('a file is refused before sending when it is not a PDF or is over 128 MiB', () => {
  assert.equal(MAX_UPLOAD_BYTES, 128 * 1024 * 1024);
  assert.equal(checkUploadFile({ name: 'usg.pdf', type: 'application/pdf', size: 10 }), null);
  assert.equal(checkUploadFile({ name: 'USG.PDF', type: '', size: 10 }), null);  // some browsers send no type
  assert.match(checkUploadFile({ name: 'a.docx', type: 'application/msword', size: 10 }) ?? '', /PDF/);
  assert.match(checkUploadFile({ name: 'a.pdf', type: 'application/pdf', size: MAX_UPLOAD_BYTES + 1 }) ?? '', /128 MiB/);
  assert.equal(checkUploadFile({ name: 'a.pdf', type: 'application/pdf', size: MAX_UPLOAD_BYTES }), null);
  assert.match(checkUploadFile({ name: 'a.pdf', type: 'application/pdf', size: 0 }) ?? '', /empty/);
  assert.match(checkUploadFile(null) ?? '', /Choose/);
});

test('upload fields are required or trimmed, and the query escapes them', () => {
  assert.match(validateUploadFields({ kind: 'handbook', title: ' ', edition: 'x', office: '', audience: '' }) ?? '', /title/i);
  assert.match(validateUploadFields({ kind: 'handbook', title: 'x', edition: '', office: '', audience: '' }) ?? '', /edition/i);
  assert.match(validateUploadFields({ kind: 'law', title: 'x', edition: 'y', office: '', audience: '' }) ?? '', /kind/i);
  assert.match(validateUploadFields({ kind: 'charter', title: 'x'.repeat(301), edition: 'y', office: '', audience: '' }) ?? '', /300/);
  assert.equal(validateUploadFields({ kind: 'charter', title: 'x', edition: 'y', office: '', audience: '' }), null);
  const query = uploadQuery({ kind: 'handbook', title: ' USG & Co / 2026 ', edition: '2026', office: '', audience: 'note #1' });
  assert.equal(query, 'kind=handbook&title=USG+%26+Co+%2F+2026&edition=2026&audience=note+%231');
});

test('prepare status labels, polling and the Gemma warning', () => {
  assert.equal(prepareLabel('running'), 'Running');
  assert.equal(prepareLabel('done'), 'Finished');
  assert.equal(prepareLabel('failed'), 'Failed');
  assert.equal(prepareLabel('interrupted'), 'Interrupted (the review server restarted while it ran)');
  assert.equal(prepareLabel('not_started'), 'Not started');
  assert.equal(prepareLabel('???'), 'Unknown state');
  assert.equal(shouldPoll('running'), true);
  for (const state of ['done', 'failed', 'interrupted', 'not_started', undefined]) assert.equal(shouldPoll(state), false);
});

test('only the "nothing open" 422 is a no-packet error', () => {
  assert.equal(isNoPacketError('Open an upload for review first.', 422), true);
  assert.equal(isNoPacketError('Open an upload for review first.', 500), false);
  assert.equal(isNoPacketError('Something else', 422), false);
});

test('withheld reasons are readable', () => {
  assert.match(withheldReason('prior_review_reference'), /prior|existing/i);
  assert.match(withheldReason('missing_policy_fields_or_pages'), /fields|pages/i);
  assert.equal(withheldReason('new_reason'), 'new_reason');
});

const plan = { readings: [
  { reading_id: 'r1', fields: ['title', 'body'], pending_fields: [], ready: true },
  { reading_id: 'r2', fields: ['title'], pending_fields: ['title'], ready: false },
  { reading_id: 'r3', fields: ['body'], pending_fields: [], ready: true }] };

test('the form becomes the build payload only when it is complete', () => {
  const form = {
    subjects: { r1: ' s1 ', r3: 's1', r2: 'ignored' },
    selected: ['r1', 'r3', 'r2'],
    claims: [{ subject_id: 's1', claim: ' Late fee applies ', finding: 'visible_fields', field_refs: ['body'], basis_reading_id: 'r1' },
      { subject_id: 's1', claim: 'No refund rule', finding: 'not_stated_in_selected_fields', field_refs: ['body'], basis_reading_id: 'r3' }] };
  const result = buildPayload(plan, form);
  assert.deepEqual(result.errors, []);
  // pending readings are never sent, even if somehow selected; not-stated claims carry no field refs
  assert.deepEqual(result.payload, {
    reading_ids: ['r1', 'r3'],
    assignments: [{ reading_id: 'r1', subject_id: 's1' }, { reading_id: 'r3', subject_id: 's1' }],
    claim_reviews: [
      { subject_id: 's1', claim: 'Late fee applies', finding: 'visible_fields', field_refs: [{ reading_id: 'r1', field_name: 'body' }], basis_reading_id: 'r1' },
      { subject_id: 's1', claim: 'No refund rule', finding: 'not_stated_in_selected_fields', field_refs: [], basis_reading_id: 'r3' }] });
});

test('incomplete or inconsistent forms list every problem instead of sending', () => {
  const good = { subject_id: 's1', claim: 'c', finding: 'visible_fields', field_refs: ['body'], basis_reading_id: 'r1' };
  const cases = [
    [{ selected: [], subjects: {}, claims: [good] }, /reading/i],
    [{ selected: ['r1'], subjects: { r1: ' ' }, claims: [good] }, /subject/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [] }, /claim/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [{ ...good, claim: ' ' }] }, /claim text/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [{ ...good, field_refs: [] }] }, /field/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [{ ...good, field_refs: ['nope'] }] }, /field/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [{ ...good, basis_reading_id: 'r3' }] }, /selected reading/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [{ ...good, subject_id: 'other' }] }, /subject/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [{ ...good, finding: 'maybe' }] }, /finding/i],
  ];
  for (const [form, pattern] of cases) {
    const result = buildPayload(plan, form);
    assert.equal(result.payload, null);
    assert.ok(result.errors.some(e => pattern.test(e)), `${pattern}: ${result.errors.join(' | ')}`);
  }
});
