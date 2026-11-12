'use client';

import { useEffect, useId, useRef, useState, type DragEvent, type FormEvent } from 'react';
import { BatchRows } from '@/components/intake-batch-rows';
import { Field } from '@/components/intake-status';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { request, ReviewError } from '@/lib/api';
import { fieldErrors, formatBytes, MAX_UPLOAD_BYTES, uploadQuery } from '@/lib/intake';
import { REVIEW_CONNECTION } from '@/lib/review-state';
import { addFiles, applyToAll, batchReducer, hasProblems, initialBatch, MAX_BATCH_FILES, nextWaiting, progressText, rowProblems,
  retryNotice, startableIds, summaryText, type BatchAction, type BatchRow, type BatchState } from '@/lib/upload-batch';

const NO_NOTES = { office: '', audience: '' };

export function IntakeUpload({ onUploaded, onSelect }: { onUploaded: (uploadId: string) => void; onSelect?: (uploadId: string) => void }) {
  const [rows, setRows] = useState<BatchRow<File>[]>([]), [batch, setBatch] = useState<BatchState>(initialBatch);
  const [kind, setKind] = useState('handbook'), [edition, setEdition] = useState('');
  const [office, setOffice] = useState(''), [audience, setAudience] = useState('');
  const [dragging, setDragging] = useState(false), [showProblems, setShowProblems] = useState(false), [addNote, setAddNote] = useState('');
  const rowsRef = useRef(rows), batchRef = useRef(batch), seq = useRef(1), running = useRef(false);
  const notesRef = useRef({ office, audience }), fileInput = useRef<HTMLInputElement>(null), summaryBox = useRef<HTMLDivElement>(null);
  const uid = useId();
  const idFor = (rowId: string, part: string) => `${uid}-${rowId}-${part}`;
  notesRef.current = { office, audience };

  const commitRows = (next: BatchRow<File>[]) => { rowsRef.current = next; setRows(next); };
  // the upload loop reads the latest state between awaits, so the reducer result is kept in a ref as well as in React state
  const send = (action: BatchAction) => { batchRef.current = batchReducer(batchRef.current, action); setBatch(batchRef.current); };
  const isUploaded = (rowId: string) => batchRef.current.results[rowId]?.status === 'uploaded';

  const busy = batch.phase === 'running' || batch.phase === 'stopping';
  const order = rows.map(row => row.id);
  const problems = Object.fromEntries(rows.map(row => [row.id, rowProblems(row, NO_NOTES)]));
  const noteErrors = fieldErrors({ kind: 'handbook', title: 'x', edition: 'x', office, audience });
  const pending = startableIds(order, batch);
  const uploadedCount = rows.length - pending.length;
  const summary = summaryText(order, batch);
  const progress = progressText(order, Object.fromEntries(rows.map(row => [row.id, row.file.name])), batch);

  function add(files: File[]) {
    if (busy || !files.length) return;
    const result = addFiles(rowsRef.current, files, { kind, edition }, seq.current);
    seq.current = result.nextSeq; commitRows(result.rows);
    const skipped = [result.duplicates && `${result.duplicates} already in the list`, result.overLimit && `${result.overLimit} over the limit of ${MAX_BATCH_FILES} files`].filter(Boolean);
    setAddNote(skipped.length ? `Skipped: ${skipped.join(', ')}.` : '');
  }
  function drop(event: DragEvent) {
    event.preventDefault(); setDragging(false);
    add(Array.from(event.dataTransfer.files));
  }
  function edit(rowId: string, field: 'title' | 'edition' | 'kind', value: string) {
    commitRows(rowsRef.current.map(row => row.id === rowId ? { ...row, [field]: value } : row));
  }
  function remove(rowId: string) {
    commitRows(rowsRef.current.filter(row => row.id !== rowId)); send({ type: 'remove', id: rowId });
    if (!rowsRef.current.length) { send({ type: 'reset' }); setShowProblems(false); fileInput.current?.focus(); }
  }
  function clearUploaded() {
    const done = rowsRef.current.filter(row => isUploaded(row.id)).map(row => row.id);
    commitRows(rowsRef.current.filter(row => !done.includes(row.id)));
    for (const id of done) send({ type: 'remove', id });
    if (!rowsRef.current.length) send({ type: 'reset' });
    fileInput.current?.focus();
  }
  function applyAll() {
    commitRows(rowsRef.current.map(row => isUploaded(row.id) ? row : applyToAll([row], { kind, edition })[0]));
  }

  async function run() {
    if (running.current) return;
    running.current = true;
    try {
      for (;;) {
        const id = nextWaiting(rowsRef.current.map(row => row.id), batchRef.current);
        if (!id) break;
        const row = rowsRef.current.find(candidate => candidate.id === id);
        if (!row) { send({ type: 'remove', id }); continue; }
        send({ type: 'begin', id });
        try {
          // raw bytes in the body, one request per file; the review server adds the session token and re-checks every limit
          const fields = { kind: row.kind, title: row.title, edition: row.edition, ...notesRef.current };
          const response = await request(REVIEW_CONNECTION, '/api/intake/upload?' + uploadQuery(fields),
            { method: 'POST', body: row.file, headers: { 'Content-Type': 'application/pdf' } });
          const result: { upload_id: string } = await response.json();
          if (typeof result?.upload_id !== 'string' || !result.upload_id) throw new Error('Missing upload confirmation');
          send({ type: 'success', id, uploadId: result.upload_id, title: row.title.trim() });
          onUploaded(result.upload_id);
        } catch (failure) {
          send({ type: 'failure', id, uncertain: !(failure instanceof ReviewError) || failure.status >= 500,
            error: failure instanceof ReviewError ? failure.message : 'The server response was lost or incomplete.' });
        }
      }
    } finally {
      send({ type: 'settle' }); running.current = false;
      setTimeout(() => summaryBox.current?.focus(), 0);
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    if (busy || !pending.length) return;
    setShowProblems(true);
    const bad = rows.find(row => pending.includes(row.id) && hasProblems(problems[row.id]));
    if (bad || Object.keys(noteErrors).length) {
      const target = bad ? idFor(bad.id, problems[bad.id].file ? 'remove' : problems[bad.id].fields.title ? 'title' : 'edition')
        : idFor('', noteErrors.office ? 'office' : 'audience');
      document.getElementById(target)?.focus();
      return;
    }
    const warning = retryNotice(pending, batchRef.current);
    if (warning && !window.confirm(warning)) return;
    send({ type: 'start', ids: pending }); void run();
  }
  function retry(rowId: string) {
    const row = rowsRef.current.find(row => row.id === rowId);
    if (running.current || !row || hasProblems(rowProblems(row, notesRef.current))) return;
    const warning = retryNotice([rowId], batchRef.current);
    if (warning && !window.confirm(warning)) return;
    send({ type: 'retry', id: rowId }); void run();
  }

  // a half-sent batch is lost on reload, so ask before the page is left mid-run
  useEffect(() => {
    if (!busy) return;
    const warn = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [busy]);

  const several = rows.length > 1;
  const problemCount = rows.filter(row => pending.includes(row.id) && hasProblems(problems[row.id])).length + Object.keys(noteErrors).length;
  const anyFailed = Object.values(batch.results).some(result => result.status === 'failed');
  const submitLabel = busy ? 'Uploading…' : batch.phase === 'finished' ? `Upload ${pending.length} unfinished`
    : pending.length === 1 ? 'Upload PDF' : `Upload ${pending.length} PDFs`;

  return <section className="intake-section" id="upload" aria-label="Upload documents">
    <p className="muted">PDF only, up to {formatBytes(MAX_UPLOAD_BYTES)} each, {MAX_BATCH_FILES} files at a time. Uploading approves nothing; each file stays a candidate until reviewed.</p>
    <form onSubmit={submit} className="intake-form" noValidate aria-busy={busy} aria-label="Upload PDFs">
      <div className="field">
        <span className="field-label" id={idFor('', 'file-label')}>PDF files</span>
        <label className={`dropzone${dragging ? ' is-dragging' : ''}`} htmlFor={idFor('', 'file')}
          onDragOver={event => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={drop}>
          <input ref={fileInput} id={idFor('', 'file')} className="sr-only" type="file" multiple accept="application/pdf,.pdf" disabled={busy}
            aria-labelledby={idFor('', 'file-label')} aria-describedby={idFor('', 'file-hint')}
            onChange={event => { add(Array.from(event.target.files ?? [])); event.target.value = ''; }} />
          <span className="dropzone-title">{dragging ? 'Release to add these files' : rows.length ? 'Add more PDFs, or drop them here' : 'Choose PDFs, or drop them here'}</span>
          <span className="dropzone-action" aria-hidden="true">Browse files</span>
        </label>
        <p className="hint" id={idFor('', 'file-hint')}>Choose several files if you like. Each becomes its own upload, sent one at a time. The server checks type and size again.</p>
        {addNote && <p className="hint" role="status">{addNote}</p>}
      </div>

      {rows.length > 0 && <>
        {several && <fieldset className="field-group"><legend>Defaults for all files</legend>
          <div className="field-row">
            <Field id={idFor('', 'kind')} label="Kind">{() =>
              <select id={idFor('', 'kind')} value={kind} disabled={busy} onChange={event => setKind(event.target.value)}>
                <option value="handbook">Handbook (also USG and other handbook-style documents)</option>
                <option value="charter">Citizens’ Charter</option></select>}</Field>
            <Field id={idFor('', 'edition')} label="Edition or year">{() =>
              <input id={idFor('', 'edition')} value={edition} maxLength={300} autoComplete="off" disabled={busy} onChange={event => setEdition(event.target.value)} />}</Field>
          </div>
          <div><Button type="button" variant="outline" size="sm" disabled={busy} onClick={applyAll}>Apply kind and edition to all files</Button></div>
        </fieldset>}

        <fieldset className="field-group"><legend>Optional notes{several ? ' for all files' : ''}</legend>
          <Field id={idFor('', 'office')} label="Office (optional)" error={noteErrors.office}>{described =>
            <input id={idFor('', 'office')} value={office} maxLength={300} autoComplete="off" disabled={busy} aria-describedby={described}
              aria-invalid={noteErrors.office ? true : undefined} onChange={event => setOffice(event.target.value)} />}</Field>
          <Field id={idFor('', 'audience')} label="Audience note (optional)" hint="Note only. Who each clause applies to is decided per item in review." error={noteErrors.audience}>{described =>
            <Textarea id={idFor('', 'audience')} rows={2} value={audience} maxLength={300} disabled={busy} aria-describedby={described}
              aria-invalid={noteErrors.audience ? true : undefined} onChange={event => setAudience(event.target.value)} />}</Field>
        </fieldset>

        <div className="batch-list-head"><h3>{rows.length} {rows.length === 1 ? 'file' : 'files'}</h3>
          {uploadedCount > 0 && !busy && <Button type="button" variant="outline" size="sm" onClick={clearUploaded}>Clear uploaded</Button>}</div>
        <BatchRows rows={rows} results={batch.results} problems={problems} showProblems={showProblems} locked={busy}
          idFor={idFor} onEdit={edit} onRemove={remove} onRetry={retry} onView={id => onSelect?.(id)} />
      </>}

      {pending.length > 0 && <div className="form-actions">
        <Button type="submit" disabled={busy}>{busy && <span className="spinner" aria-hidden="true" />}{submitLabel}</Button>
        {batch.phase === 'running' && <Button type="button" variant="outline" onClick={() => send({ type: 'stop' })}>Stop after this file</Button>}
        {!busy && showProblems && problemCount > 0 && <p className="field-error">Fix {problemCount} {problemCount === 1 ? 'problem' : 'problems'} above, then upload again.</p>}
      </div>}
    </form>
    <div aria-live="polite" className="batch-live">
      {progress && <p className="muted">{progress}{batch.phase === 'running' ? ' Large files can take a minute; keep this page open.' : ''}</p>}
      {batch.phase === 'finished' && summary && <div className={`notice ${anyFailed ? 'error' : 'success'}`} role="status" tabIndex={-1} ref={summaryBox}>
        <div><p><strong>{summary}.</strong></p>
          <p>Uploaded files are in the list below, ready to prepare. Prepare stays a separate choice for each one.</p></div></div>}
    </div>
  </section>;
}
