import assert from 'node:assert/strict';
import test from 'node:test';
import { addFiles, applyToAll, batchReducer, editionFromFileName, initialBatch, MAX_BATCH_FILES, nextWaiting, progressText,
  retryNotice, rowProblems, startableIds, summaryText, titleFromFileName } from '../lib/upload-batch.ts';

const pdf = (name, size = 1000) => ({ name, size, type: 'application/pdf' });
const defaults = { kind: 'handbook', edition: '', office: '', audience: '' };

test('title is the file name without extension, tidied', () => {
  assert.equal(titleFromFileName('USG_Student_Handbook-2026.pdf'), 'USG Student Handbook 2026');
  assert.equal(titleFromFileName('  citizens__charter --  final.PDF '), 'citizens charter final');
  assert.equal(titleFromFileName('Handbook.v2.pdf'), 'Handbook.v2');
  assert.equal(titleFromFileName('Memo_2026.JPEG'), 'Memo 2026');
  assert.equal(titleFromFileName('Student_Notice.webp'), 'Student Notice');
  assert.equal(titleFromFileName('.pdf'), '');
});

test('edition is taken from a four-digit year or a year range in the name, else left empty', () => {
  assert.equal(editionFromFileName('USG_Handbook_2026.pdf'), '2026');
  assert.equal(editionFromFileName('Handbook 2025-2026.pdf'), '2025-2026');
  assert.equal(editionFromFileName('Handbook_2025_2026.pdf'), '2025-2026');
  assert.equal(editionFromFileName('handbook.pdf'), '');
  assert.equal(editionFromFileName('scan12345.pdf'), '');  // five digits is not a year
  assert.equal(editionFromFileName('Memo 1999 and 2026.pdf'), '1999');
  assert.equal(editionFromFileName('Handbook 3026.pdf'), '');
});

test('added files become rows with prefilled fields; duplicates are skipped and the batch is capped', () => {
  const first = addFiles([], [pdf('A_Handbook_2026.pdf'), pdf('b-charter.pdf')], defaults, 1);
  assert.equal(first.rows.length, 2);
  assert.deepEqual(first.rows.map(row => [row.id, row.title, row.edition, row.kind]),
    [['r1', 'A Handbook 2026', '2026', 'handbook'], ['r2', 'b charter', '', 'handbook']]);
  assert.equal(first.nextSeq, 3);
  const again = addFiles(first.rows, [first.rows[1].file, pdf('c.pdf', 5)], defaults, first.nextSeq);
  assert.equal(again.duplicates, 1);
  assert.equal(again.rows.length, 3);
  const many = Array.from({ length: 25 }, (_, n) => pdf(`f${n}.pdf`));
  const capped = addFiles([], many, defaults, 1);
  assert.equal(capped.rows.length, MAX_BATCH_FILES);
  assert.equal(capped.overLimit, 5);
  assert.equal(MAX_BATCH_FILES, 20);
});

test('different PDFs with the same filename and size remain separate uploads', () => {
  const { rows } = addFiles([], [pdf('scan.pdf'), pdf('scan.pdf')], defaults, 1);
  assert.equal(rows.length, 2);
});

test('a lost response requires a duplicate warning on either retry path', () => {
  let state = batchReducer(initialBatch, { type: 'start', ids: ['r1', 'r2'] });
  state = batchReducer(state, { type: 'failure', id: 'r1', error: 'Response lost', uncertain: true });
  state = batchReducer(state, { type: 'failure', id: 'r2', error: 'Rejected' });
  state = batchReducer(state, { type: 'settle' });
  assert.match(retryNotice(['r1'], state), /already be saved.*duplicate/);
  assert.match(retryNotice(startableIds(['r1', 'r2'], state), state), /duplicate/);
  assert.equal(retryNotice(['r2'], state), '');
});

test('retry cannot change an active batch or undo Stop after this file', () => {
  let state = batchReducer(initialBatch, { type: 'start', ids: ['r1', 'r2', 'r3'] });
  state = batchReducer(state, { type: 'failure', id: 'r1', error: 'Rejected' });
  state = batchReducer(state, { type: 'begin', id: 'r2' });
  assert.deepEqual(batchReducer(state, { type: 'retry', id: 'r1' }), state);
  state = batchReducer(state, { type: 'stop' });
  assert.deepEqual(batchReducer(state, { type: 'retry', id: 'r1' }), state);
  assert.equal(nextWaiting(['r1', 'r2', 'r3'], state), null);
});

test('batch default edition and kind prefill rows that have no year of their own', () => {
  const { rows } = addFiles([], [pdf('plain.pdf'), pdf('x_2024.pdf')], { ...defaults, kind: 'charter', edition: '2026' }, 1);
  assert.deepEqual(rows.map(row => [row.kind, row.edition]), [['charter', '2026'], ['charter', '2024']]);
});

test('apply to all sets the kind and a non-empty edition on every row', () => {
  const { rows } = addFiles([], [pdf('a.pdf'), pdf('b_2024.pdf')], defaults, 1);
  const changed = applyToAll(rows, { kind: 'charter', edition: ' 2027 ' });
  assert.deepEqual(changed.map(row => [row.kind, row.edition]), [['charter', '2027'], ['charter', '2027']]);
  assert.deepEqual(applyToAll(rows, { kind: 'handbook', edition: '' }).map(row => row.edition), ['', '2024']);
});

test('a row reports file problems and field problems; the shared notes count too', () => {
  const { rows } = addFiles([], [pdf('ok_2026.pdf'), { name: 'notes.docx', size: 10, type: 'application/msword' }, pdf('big.pdf', 129 * 1024 * 1024)], defaults, 1);
  assert.deepEqual(rowProblems(rows[0], { office: '', audience: '' }), { fields: {} });
  assert.match(rowProblems(rows[1], { office: '', audience: '' }).file ?? '', /PDF/);
  assert.match(rowProblems(rows[1], { office: '', audience: '' }).fields.edition ?? '', /edition/i);
  assert.match(rowProblems(rows[2], { office: '', audience: '' }).file ?? '', /128 MiB/);
  assert.match(rowProblems(rows[0], { office: 'x'.repeat(301), audience: '' }).fields.office ?? '', /300/);
  assert.match(rowProblems({ ...rows[0], title: ' ' }, { office: '', audience: '' }).fields.title ?? '', /title/i);
});

test('only rows not yet uploaded are startable', () => {
  let state = batchReducer(initialBatch, { type: 'start', ids: ['r1', 'r2'] });
  state = batchReducer(state, { type: 'begin', id: 'r1' });
  state = batchReducer(state, { type: 'success', id: 'r1', uploadId: 'up-1', title: 'One' });
  assert.deepEqual(startableIds(['r1', 'r2', 'r3'], state), ['r2', 'r3']);
});

test('batch runs one file at a time, a failure does not stop the rest, and the summary counts both', () => {
  const order = ['r1', 'r2', 'r3'];
  let state = batchReducer(initialBatch, { type: 'start', ids: order });
  assert.equal(state.phase, 'running');
  assert.deepEqual(order.map(id => state.results[id].status), ['waiting', 'waiting', 'waiting']);
  assert.equal(nextWaiting(order, state), 'r1');

  state = batchReducer(state, { type: 'begin', id: 'r1' });
  assert.equal(nextWaiting(order, state), 'r2');  // r1 is uploading, not waiting
  state = batchReducer(state, { type: 'success', id: 'r1', uploadId: 'up-1', title: 'One' });
  state = batchReducer(state, { type: 'begin', id: 'r2' });
  state = batchReducer(state, { type: 'failure', id: 'r2', error: 'Only PDF files can be uploaded.' });
  assert.equal(state.results.r2.error, 'Only PDF files can be uploaded.');
  assert.equal(nextWaiting(order, state), 'r3');
  state = batchReducer(state, { type: 'begin', id: 'r3' });
  state = batchReducer(state, { type: 'success', id: 'r3', uploadId: 'up-3', title: 'Three' });
  assert.equal(nextWaiting(order, state), null);
  state = batchReducer(state, { type: 'settle' });
  assert.equal(state.phase, 'finished');
  assert.equal(summaryText(order, state), '2 uploaded, 1 failed');
  assert.equal(state.results.r1.uploadId, 'up-1');
});

test('stop lets the current file finish, then the rest are marked not sent', () => {
  const order = ['r1', 'r2', 'r3'];
  let state = batchReducer(initialBatch, { type: 'start', ids: order });
  state = batchReducer(state, { type: 'begin', id: 'r1' });
  state = batchReducer(state, { type: 'stop' });
  assert.equal(state.phase, 'stopping');
  assert.equal(nextWaiting(order, state), null);  // nothing new starts
  assert.equal(state.results.r1.status, 'uploading');
  state = batchReducer(state, { type: 'success', id: 'r1', uploadId: 'up-1', title: 'One' });
  state = batchReducer(state, { type: 'settle' });
  assert.equal(state.phase, 'finished');
  assert.deepEqual(order.map(id => state.results[id].status), ['uploaded', 'skipped', 'skipped']);
  assert.equal(summaryText(order, state), '1 uploaded, 2 not sent');
});

test('a failed or unsent row can be retried and the next run picks it up', () => {
  const order = ['r1', 'r2'];
  let state = batchReducer(initialBatch, { type: 'start', ids: order });
  state = batchReducer(state, { type: 'begin', id: 'r1' });
  state = batchReducer(state, { type: 'failure', id: 'r1', error: 'boom' });
  state = batchReducer(state, { type: 'begin', id: 'r2' });
  state = batchReducer(state, { type: 'success', id: 'r2', uploadId: 'up-2', title: 'Two' });
  state = batchReducer(state, { type: 'settle' });
  state = batchReducer(state, { type: 'retry', id: 'r1' });
  assert.equal(state.results.r1.status, 'waiting');
  assert.equal(state.results.r1.error, undefined);
  assert.equal(state.phase, 'running');
  assert.equal(nextWaiting(order, state), 'r1');
  state = batchReducer(state, { type: 'retry', id: 'r2' });  // an uploaded row cannot be re-sent
  assert.equal(state.results.r2.status, 'uploaded');
});

test('removing a row drops its result; reset clears the batch', () => {
  let state = batchReducer(initialBatch, { type: 'start', ids: ['r1', 'r2'] });
  state = batchReducer(state, { type: 'remove', id: 'r2' });
  assert.deepEqual(Object.keys(state.results), ['r1']);
  assert.deepEqual(batchReducer(state, { type: 'reset' }), initialBatch);
});

test('progress and summary wording', () => {
  const order = ['r1', 'r2', 'r3'];
  const names = { r1: 'a.pdf', r2: 'b.pdf', r3: 'c.pdf' };
  let state = batchReducer(initialBatch, { type: 'start', ids: order });
  state = batchReducer(state, { type: 'begin', id: 'r1' });
  assert.equal(progressText(order, names, state), 'Uploading 1 of 3: a.pdf');
  state = batchReducer(state, { type: 'success', id: 'r1', uploadId: 'u', title: 'A' });
  state = batchReducer(state, { type: 'begin', id: 'r2' });
  assert.equal(progressText(order, names, state), 'Uploading 2 of 3: b.pdf');
  state = batchReducer(state, { type: 'stop' });
  assert.match(progressText(order, names, state), /Stopping after b\.pdf/);
  assert.equal(summaryText(order, initialBatch), '');
  const one = batchReducer(batchReducer(batchReducer(initialBatch, { type: 'start', ids: ['r1'] }), { type: 'begin', id: 'r1' }),
    { type: 'success', id: 'r1', uploadId: 'u', title: 'A' });
  assert.equal(summaryText(['r1'], one), '1 uploaded');
});
