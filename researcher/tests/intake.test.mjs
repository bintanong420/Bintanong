import assert from 'node:assert/strict';
import test from 'node:test';
import { buildPayload, buildProblems, latestLogLine, checkUploadFile, fieldErrors, formatBytes, formatElapsed, pipelineSteps, isNoPacketError, MAX_UPLOAD_BYTES, prepareLabel, shouldPoll, uploadQuery,
  uploadMediaType, validateUploadFields, withheldReason } from '../lib/intake.ts';

test('PDF, PNG, JPG/JPEG and WebP get matching upload MIME types, including blank browser types', () => {
  for (const [extension, type] of [['pdf', 'application/pdf'], ['png', 'image/png'], ['jpg', 'image/jpeg'],
    ['jpeg', 'image/jpeg'], ['webp', 'image/webp']]) {
    assert.equal(uploadMediaType({ name: `document.${extension}`, type }), type);
    assert.equal(uploadMediaType({ name: `document.${extension.toUpperCase()}`, type: '' }), type);
    assert.equal(checkUploadFile({ name: `document.${extension}`, type, size: 10 }), null);
  }
  assert.equal(uploadMediaType({ name: 'movie.gif', type: 'image/gif' }), '');
  assert.equal(uploadMediaType({ name: 'spoof.png', type: 'text/html' }), '');
});

test('a file is refused before sending when unsupported or over 128 MiB', () => {
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
  assert.equal(prepareLabel('done'), 'Done');
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
    [{ selected: [], subjects: {}, claims: [good] }, /passage/i],
    [{ selected: ['r1'], subjects: { r1: ' ' }, claims: [good] }, /topic/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [] }, /claim/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [{ ...good, claim: ' ' }] }, /claim text/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [{ ...good, field_refs: [] }] }, /field/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [{ ...good, field_refs: ['nope'] }] }, /field/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [{ ...good, basis_reading_id: 'r3' }] }, /selected one/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [{ ...good, subject_id: 'other' }] }, /topic/i],
    [{ selected: ['r1'], subjects: { r1: 's1' }, claims: [{ ...good, finding: 'maybe' }] }, /finding/i],
  ];
  for (const [form, pattern] of cases) {
    const result = buildPayload(plan, form);
    assert.equal(result.payload, null);
    assert.ok(result.errors.some(e => pattern.test(e)), `${pattern}: ${result.errors.join(' | ')}`);
  }
});

test('sizes read in MiB or KiB with one decimal and never as zero for a non-empty file', () => {
  assert.equal(formatBytes(0), '0 B');
  assert.equal(formatBytes(512), '512 B');
  assert.equal(formatBytes(1536), '1.5 KiB');
  assert.equal(formatBytes(5 * 1024 * 1024), '5.0 MiB');
  assert.equal(formatBytes(1), '1 B');
  assert.equal(formatBytes(-5), '0 B');
});

test('elapsed time is minutes and seconds, and bad input reads as zero', () => {
  assert.equal(formatElapsed(0), '0 s');
  assert.equal(formatElapsed(9_400), '9 s');
  assert.equal(formatElapsed(65_000), '1 min 05 s');
  assert.equal(formatElapsed(3_600_000 + 61_000), '1 h 01 min');
  assert.equal(formatElapsed(-1), '0 s');
  assert.equal(formatElapsed(Number.NaN), '0 s');
});

test('field errors name the field that needs fixing and agree with the single-message check', () => {
  const ok = { kind: 'handbook', title: 'T', edition: 'E', office: '', audience: '' };
  assert.deepEqual(fieldErrors(ok), {});
  assert.deepEqual(Object.keys(fieldErrors({ ...ok, title: ' ', edition: '' })).sort(), ['edition', 'title']);
  assert.match(fieldErrors({ ...ok, office: 'x'.repeat(301) }).office ?? '', /300/);
  assert.match(fieldErrors({ ...ok, audience: 'x'.repeat(301) }).audience ?? '', /300/);
  assert.match(fieldErrors({ ...ok, kind: 'law' }).kind ?? '', /kind/i);
  for (const bad of [{ ...ok, title: '' }, { ...ok, kind: 'x' }, { ...ok, office: 'x'.repeat(301) }])
    assert.equal(validateUploadFields(bad), Object.values(fieldErrors(bad))[0]);
});

test('each upload shows four steps, and a step is blocked until the one before it is done', () => {
  const keys = pipelineSteps('running', false).map(step => step.key);
  assert.deepEqual(keys, ['upload', 'prepare', 'review', 'build']);
  const by = (state, open) => Object.fromEntries(pipelineSteps(state, open).map(step => [step.key, step]));
  assert.equal(by('running', false).upload.status, 'done');
  assert.equal(by('running', false).prepare.status, 'active');
  assert.equal(by('running', false).review.status, 'blocked');
  assert.equal(by('done', false).prepare.status, 'done');
  assert.equal(by('done', false).review.status, 'todo');
  assert.equal(by('running', false).build.status, 'blocked');
  assert.equal(by('done', false).build.status, 'todo');  // Build needs a prepared upload, not an open one
  assert.equal(by('done', true).review.status, 'active');
  assert.equal(by('done', true).build.status, 'todo');
  assert.equal(by('failed', false).prepare.status, 'failed');
  assert.equal(by('interrupted', false).prepare.status, 'failed');
  assert.match(by('interrupted', false).prepare.text, /Interrupted/);
  assert.equal(by('not_started', false).prepare.status, 'todo');
  assert.equal(by(undefined, false).prepare.status, 'unknown');
  for (const step of pipelineSteps('failed', false)) assert.ok(step.text.length > 0);  // status is always words, never colour alone
});

test('build problems point at the reading or claim field they belong to', () => {
  const plan = { readings: [{ reading_id: 'r1', fields: ['a'], pending_fields: [], ready: true }] };
  const none = buildProblems(plan, { selected: [], subjects: {}, claims: [] });
  assert.ok(none.some(p => p.scope === 'selection'));
  assert.ok(none.some(p => p.scope === 'claims'));
  const form = { selected: ['r1'], subjects: { r1: '' }, claims: [{ subject_id: 'zz', claim: '', finding: 'visible_fields', field_refs: [], basis_reading_id: '' }] };
  const problems = buildProblems(plan, form);
  assert.ok(problems.some(p => p.scope === 'reading' && p.readingId === 'r1'));
  const fields = problems.filter(p => p.scope === 'claim' && p.index === 0).map(p => p.field).sort();
  assert.deepEqual(fields, ['basis', 'claim', 'fields', 'subject']);
  assert.deepEqual(buildPayload(plan, form).errors, problems.map(p => p.message));  // flat messages unchanged
});
test('the log summary is the latest line that is not a progress bar or a warning, trimmed', () => {
  assert.equal(latestLogLine([]), '');
  assert.equal(latestLogLine(['Converting page 3', '  ', 'Fetching: 40%|####   | 4/10 [00:01<00:02, 2.0it/s]']), 'Converting page 3');
  assert.equal(latestLogLine(['Wrote packet', 'UserWarning: CPU only, no CUDA']), 'Wrote packet');
  assert.equal(latestLogLine(['x'.repeat(300)]).length <= 160, true);
  assert.equal(latestLogLine(['10%|# | 1/10', 'warning: x']), '');
});
import { buildBlocker, buildChecklist as checklist, passageLabel, nextStep } from '../lib/intake.ts';

test('the packet JSON line is summarised, not shown raw', () => {
  const raw = JSON.stringify({ packet_id: 'a'.repeat(64), items: 12, revision: 1 });
  assert.equal(latestLogLine(['Converting', raw]), 'Prepared: 12 items');
  assert.equal(latestLogLine([JSON.stringify({ packet_id: 'a'.repeat(64), items: 1 })]), 'Prepared: 1 item');
  assert.equal(latestLogLine([JSON.stringify({ packet_id: 'a'.repeat(64) })]), 'Prepared: the review draft is written');
  assert.equal(latestLogLine(['{"other": 1}']), '{"other": 1}');
});

test('Build waits for a form saved in this review, and says why', () => {
  assert.equal(buildBlocker(true, true), '');
  assert.match(buildBlocker(false, true), /prepare/i);
  assert.match(buildBlocker(true, false), /save the passages and claims form/i);
  assert.match(buildBlocker(true, undefined), /checking/i);
  assert.match(buildBlocker(true, false, true), /form below/i);
  assert.equal(checklist(true, true)[1].status, 'done');
  assert.equal(checklist(true, false)[1].status, 'blocked');
  assert.equal(checklist(true, undefined)[1].status, 'unknown');
});

test('passages are named by their first words, not their ids', () => {
  assert.equal(passageLabel({ reading_id: 'abc:text-0', preview: 'Shifting of programs' }), '“Shifting of programs”');
  assert.equal(passageLabel({ reading_id: 'abc:text-0' }), 'Passage abc:text-0');
});

test('each upload state names one next step', () => {
  assert.match(nextStep({ prepare: undefined }), /checking/i);
  assert.match(nextStep({ prepare: 'not_started' }), /prepare/i);
  assert.match(nextStep({ prepare: 'running' }), /wait/i);
  assert.match(nextStep({ prepare: 'done', open: false }), /open it for review/i);
  assert.match(nextStep({ prepare: 'done', open: true, build: undefined }), /build chunks/i);
  assert.match(nextStep({ prepare: 'done', open: true, build: 'done' }), /knowledge/i);
  assert.match(nextStep({ prepare: 'failed' }), /upload the document again/i);
});

import { nextStep as step, findingLabel } from '../lib/intake.ts';

test('after the form is saved the next step is to build', () => {
  assert.match(step({ prepare: 'done', open: true, formSaved: true }), /build chunks/i);
  assert.doesNotMatch(step({ prepare: 'done', open: true, formSaved: true }), /save the form/i);
  assert.match(step({ prepare: 'done', open: true, formSaved: false }), /save the form/i);
});

test('finding choices read as plain statements', () => {
  assert.equal(findingLabel('visible_fields'), 'The text shows this');
  assert.equal(findingLabel('not_stated_in_selected_fields'), 'The text does not say this');
});
