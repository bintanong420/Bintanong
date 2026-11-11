'use client';

import { useRef, useState, type FormEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { request, ReviewError } from '@/lib/api';
import { checkUploadFile, uploadQuery, validateUploadFields } from '@/lib/intake';
import { REVIEW_CONNECTION } from '@/lib/review-state';

export function IntakeUpload({ onUploaded }: { onUploaded: () => void }) {
  const [kind, setKind] = useState('handbook'), [title, setTitle] = useState(''), [edition, setEdition] = useState('');
  const [office, setOffice] = useState(''), [audience, setAudience] = useState('');
  const [busy, setBusy] = useState(false), [error, setError] = useState(''), [message, setMessage] = useState('');
  const fileInput = useRef<HTMLInputElement>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setError(''); setMessage('');
    const file = fileInput.current?.files?.[0] ?? null;
    const fields = { kind, title, edition, office, audience };
    const problem = checkUploadFile(file) ?? validateUploadFields(fields);
    if (problem || !file) { setError(problem ?? 'Choose a PDF file first.'); return; }
    setBusy(true);
    try {
      // raw bytes in the body; the review server adds the session token, and the server re-checks every limit
      const response = await request(REVIEW_CONNECTION, '/api/intake/upload?' + uploadQuery(fields),
        { method: 'POST', body: file, headers: { 'Content-Type': 'application/pdf' } });
      const result: { upload_id: string } = await response.json();
      setMessage(`Uploaded as ${result.upload_id}. Next, run Docling on it in the list below.`);
      setTitle(''); setEdition(''); setOffice(''); setAudience('');
      if (fileInput.current) fileInput.current.value = '';
      onUploaded();
    } catch (failure) {
      setError(failure instanceof ReviewError ? failure.message : 'The upload could not be sent. Check that the review command is still running.');
    } finally { setBusy(false); }
  }

  return <section className="intake-section" aria-labelledby="upload-heading">
    <h2 id="upload-heading">1. Upload a document</h2>
    <p className="muted">PDF only, up to 128 MiB. Uploading approves nothing: the file stays a candidate until it is reviewed.</p>
    <form onSubmit={event => void submit(event)} className="intake-form" noValidate>
      <label>PDF file<input ref={fileInput} type="file" accept="application/pdf" required /></label>
      <label>Kind<select value={kind} onChange={event => setKind(event.target.value)}>
        <option value="handbook">Handbook (also use this for USG and other handbook-style documents)</option>
        <option value="charter">Citizens’ Charter</option>
      </select></label>
      <label>Title<input value={title} onChange={event => setTitle(event.target.value)} maxLength={300} required /></label>
      <label>Edition or year<input value={edition} onChange={event => setEdition(event.target.value)} maxLength={300} required /></label>
      <label>Office (optional)<input value={office} onChange={event => setOffice(event.target.value)} maxLength={300} /></label>
      <label>Audience note (optional)
        <Textarea rows={2} value={audience} onChange={event => setAudience(event.target.value)} maxLength={300} aria-describedby="audience-help" />
        <span id="audience-help" className="muted">Note only; who each clause applies to is decided per item in review.</span></label>
      <div><Button type="submit" disabled={busy}>{busy ? 'Uploading…' : 'Upload PDF'}</Button></div>
    </form>
    <div aria-live="polite">
      {error && <p className="notice error" role="alert">{error}</p>}
      {message && <p className="notice success" role="status">{message}</p>}
    </div>
  </section>;
}
