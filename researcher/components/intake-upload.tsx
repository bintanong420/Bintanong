'use client';

import { useEffect, useId, useRef, useState, type DragEvent, type FormEvent } from 'react';
import { Field } from '@/components/intake-status';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { request, ReviewError } from '@/lib/api';
import { checkUploadFile, fieldErrors, formatBytes, MAX_UPLOAD_BYTES, uploadQuery, type UploadField } from '@/lib/intake';
import { REVIEW_CONNECTION } from '@/lib/review-state';

type Errors = Partial<Record<UploadField, string>>;
const ORDER = ['kind', 'title', 'edition', 'office', 'audience'] as const;

export function IntakeUpload({ onUploaded }: { onUploaded: (uploadId: string) => void }) {
  const [kind, setKind] = useState('handbook'), [title, setTitle] = useState(''), [edition, setEdition] = useState('');
  const [office, setOffice] = useState(''), [audience, setAudience] = useState('');
  const [file, setFile] = useState<File | null>(null), [dragging, setDragging] = useState(false);
  const [errors, setErrors] = useState<Errors>({}), [fileProblem, setFileProblem] = useState('');
  const [busy, setBusy] = useState(false), [serverError, setServerError] = useState('');
  const [uploaded, setUploaded] = useState<{ id: string; title: string; name: string; bytes: number } | null>(null);
  const successBox = useRef<HTMLDivElement>(null), errorBox = useRef<HTMLDivElement>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const uid = useId();
  const id = (name: string) => `${uid}-${name}`;

  function choose(next: File | null) {
    setFile(next); setUploaded(null); setServerError('');
    // a client check is only a hint: the server re-checks the type, size and fields, and its answer is shown as written
    setFileProblem(next ? checkUploadFile(next) ?? '' : '');
  }
  function drop(event: DragEvent) {
    event.preventDefault(); setDragging(false);
    const dropped = event.dataTransfer.files;
    if (busy || !dropped.length || !fileInput.current) return;
    fileInput.current.files = dropped;
    choose(dropped[0]);
  }
  function clearFile() {
    if (fileInput.current) { fileInput.current.value = ''; fileInput.current.focus(); }
    choose(null);
  }
  function edit(field: UploadField, set: (value: string) => void) {
    return (value: string) => { set(value); setErrors(current => ({ ...current, [field]: undefined })); };
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setServerError(''); setUploaded(null);
    const fields = { kind, title, edition, office, audience };
    const found = fieldErrors(fields), fileCheck = checkUploadFile(file);
    setErrors(found); setFileProblem(fileCheck ?? '');
    if (fileCheck || !file || Object.keys(found).length) {
      const first = fileCheck ? 'file' : ORDER.find(key => found[key]);
      document.getElementById(id(first ?? 'file'))?.focus();
      return;
    }
    setBusy(true);
    try {
      // raw bytes in the body; the review server adds the session token, and the server re-checks every limit
      const response = await request(REVIEW_CONNECTION, '/api/intake/upload?' + uploadQuery(fields),
        { method: 'POST', body: file, headers: { 'Content-Type': 'application/pdf' } });
      const result: { upload_id: string } = await response.json();
      setUploaded({ id: result.upload_id, title: title.trim(), name: file.name, bytes: file.size });
      setTitle(''); setEdition(''); setOffice(''); setAudience(''); setErrors({}); setFile(null); setFileProblem('');
      if (fileInput.current) fileInput.current.value = '';
      onUploaded(result.upload_id);
    } catch (failure) {
      setServerError(failure instanceof ReviewError ? failure.message : 'The upload could not be sent. Check that the review command is still running, then try again.');
    } finally { setBusy(false); }
  }

  // move focus to the outcome so keyboard and screen-reader users land on it
  useEffect(() => { if (uploaded) successBox.current?.focus(); }, [uploaded]);
  useEffect(() => { if (serverError) errorBox.current?.focus(); }, [serverError]);
  const problemCount = Object.keys(errors).filter(key => errors[key as UploadField]).length + (fileProblem ? 1 : 0);
  return <section className="intake-section" id="upload" aria-label="Upload a document">
    <p className="muted">PDF only, up to {formatBytes(MAX_UPLOAD_BYTES)}. Uploading approves nothing: the file stays a candidate until it is reviewed.</p>
    <form onSubmit={event => void submit(event)} className="intake-form" noValidate aria-busy={busy}>
      <div className="field">
        <span className="field-label" id={id('file-label')}>PDF file</span>
        <label className={`dropzone${dragging ? ' is-dragging' : ''}${fileProblem ? ' is-invalid' : ''}`} htmlFor={id('file')}
          onDragOver={event => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={drop}>
          <input ref={fileInput} id={id('file')} className="sr-only" type="file" accept="application/pdf,.pdf" disabled={busy}
            aria-labelledby={id('file-label')} aria-describedby={[id('file-hint'), fileProblem ? id('file-error') : ''].filter(Boolean).join(' ')}
            aria-invalid={fileProblem ? true : undefined}
            onChange={event => choose(event.target.files?.[0] ?? null)} />
          <span className="dropzone-title">{dragging ? 'Release to choose this file' : 'Choose a PDF, or drop it here'}</span>
          <span className="dropzone-action" aria-hidden="true">Browse files</span>
        </label>
        <p className="hint" id={id('file-hint')}>The type and size are checked here as a hint. The review server checks them again when you upload.</p>
        {file && <div className="file-chosen"><p><strong className="file-name">{file.name}</strong> <span className="muted">{formatBytes(file.size)}</span></p>
          <Button type="button" variant="outline" size="sm" disabled={busy} onClick={clearFile} aria-label={`Remove ${file.name}`}>Remove file</Button></div>}
        {fileProblem && <p className="field-error" id={id('file-error')}>{fileProblem}</p>}
        {serverError && <div className="notice error" role="alert" tabIndex={-1} ref={errorBox}><span><strong>Upload failed.</strong> {serverError}</span></div>}
      </div>

      <fieldset className="field-group"><legend>About this document</legend>
        <Field id={id('kind')} label="Kind" error={errors.kind}>{described =>
          <select id={id('kind')} value={kind} aria-describedby={described} aria-invalid={errors.kind ? true : undefined}
            onChange={event => edit('kind', setKind)(event.target.value)}>
            <option value="handbook">Handbook (also use this for USG and other handbook-style documents)</option>
            <option value="charter">Citizens’ Charter</option>
          </select>}</Field>
        <Field id={id('title')} label="Title" error={errors.title}>{described =>
          <input id={id('title')} value={title} maxLength={300} autoComplete="off" aria-describedby={described} aria-invalid={errors.title ? true : undefined}
            onChange={event => edit('title', setTitle)(event.target.value)} />}</Field>
        <Field id={id('edition')} label="Edition or year" error={errors.edition}>{described =>
          <input id={id('edition')} value={edition} maxLength={300} autoComplete="off" aria-describedby={described} aria-invalid={errors.edition ? true : undefined}
            onChange={event => edit('edition', setEdition)(event.target.value)} />}</Field>
      </fieldset>

      <fieldset className="field-group"><legend>Optional notes</legend>
        <Field id={id('office')} label="Office (optional)" error={errors.office}>{described =>
          <input id={id('office')} value={office} maxLength={300} autoComplete="off" aria-describedby={described} aria-invalid={errors.office ? true : undefined}
            onChange={event => edit('office', setOffice)(event.target.value)} />}</Field>
        <Field id={id('audience')} label="Audience note (optional)" hint="Note only. Who each clause applies to is decided per item in review." error={errors.audience}>{described =>
          <Textarea id={id('audience')} rows={2} value={audience} maxLength={300} aria-describedby={described} aria-invalid={errors.audience ? true : undefined}
            onChange={event => edit('audience', setAudience)(event.target.value)} />}</Field>
      </fieldset>

      <div className="form-actions">
        <Button type="submit" disabled={busy}>{busy && <span className="spinner" aria-hidden="true" />}{busy ? 'Uploading…' : 'Upload PDF'}</Button>
        {busy && <p className="muted">Sending {file ? `${file.name} (${formatBytes(file.size)})` : 'the file'}. Large files can take a minute; keep this page open.</p>}
        {!busy && problemCount > 0 && <p className="field-error">Fix {problemCount} {problemCount === 1 ? 'problem' : 'problems'} above, then upload again.</p>}
      </div>
    </form>
    <div aria-live="polite">
      {uploaded && <div className="notice success" role="status" tabIndex={-1} ref={successBox}><div>
        <p><strong>Uploaded: {uploaded.title}</strong></p>
        <dl className="upload-meta"><div><dt>File</dt><dd className="file-name">{uploaded.name}</dd></div>
          <div><dt>Size</dt><dd>{formatBytes(uploaded.bytes)}</dd></div><div><dt>Upload id</dt><dd><code>{uploaded.id}</code></dd></div></dl>
        <p>It is selected in the list, ready to prepare. The form is cleared so you can add another.</p></div></div>}
    </div>
  </section>;
}
