'use client';

import { useCallback, useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { request } from '@/lib/api';
import { prepareLabel, shouldPoll } from '@/lib/intake';
import { REVIEW_CONNECTION } from '@/lib/review-state';

export type Upload = { upload_id: string; kind: string; title: string; edition: string; bytes: number };
type Status = { state: string; exit_code?: number; error?: string; log_tail?: string[];
  gemma_unavailable_fields?: number; assist?: boolean };

function message(error: unknown) { return error instanceof Error ? error.message : 'The request failed.'; }

function UploadRow({ upload, current, onOpen }: { upload: Upload; current: boolean; onOpen: (id: string) => void }) {
  const [status, setStatus] = useState<Status | null>(null), [error, setError] = useState(''), [busy, setBusy] = useState(false);
  const refresh = useCallback(async () => {
    try { setStatus(await (await request(REVIEW_CONNECTION, '/api/intake/prepare/' + upload.upload_id)).json()); setError(''); }
    catch (failure) { setError(message(failure)); }
  }, [upload.upload_id]);

  useEffect(() => { void refresh(); }, [refresh]);
  // poll only while the job is running; a finished, failed or interrupted job never changes by itself
  useEffect(() => {
    if (!shouldPoll(status?.state)) return;
    const timer = setInterval(() => void refresh(), 3000);
    return () => clearInterval(timer);
  }, [status?.state, refresh]);

  async function start(assist: boolean) {
    setBusy(true); setError('');
    try {
      setStatus(await (await request(REVIEW_CONNECTION, '/api/intake/prepare',
        { method: 'POST', body: JSON.stringify({ upload_id: upload.upload_id, assist }) })).json());
    } catch (failure) { setError(message(failure)); }
    finally { setBusy(false); }
  }

  const state = status?.state;
  return <li className="intake-upload">
    <div><strong>{upload.title}</strong> <span className="muted">{upload.edition} · {upload.kind} · {(upload.bytes / 1024 / 1024).toFixed(1)} MiB</span>
      <p className="muted">Upload id <code>{upload.upload_id}</code>{current && <> · <strong>open for review</strong></>}</p></div>
    <div className="intake-actions">
      {state === 'not_started' && <>
        <Button variant="outline" disabled={busy} onClick={() => void start(false)}>Run Docling</Button>
        <Button variant="outline" disabled={busy} onClick={() => void start(true)}>Run Docling + Gemma audit (flagged pages)</Button></>}
      {state === 'done' && <Button disabled={current} onClick={() => onOpen(upload.upload_id)}>{current ? 'Open for review (already open)' : 'Open for review'}</Button>}
    </div>
    {state && state !== 'not_started' && <p className="muted">A retry or a different audit choice needs a new upload: one packet is made per upload.</p>}
    <div aria-live="polite">
      {status && <p className={state === 'failed' || state === 'interrupted' ? 'notice error' : 'notice'} role="status">
        Prepare: {prepareLabel(status.state)}{status.exit_code !== undefined && ` (exit code ${status.exit_code})`}{status.error && ` — ${status.error}`}</p>}
      {state === 'done' && (status?.gemma_unavailable_fields ?? 0) > 0 && <p className="notice hold" role="status">
        Gemma could not assist {status?.gemma_unavailable_fields} fields; review those against the original manually.</p>}
      {error && <p className="notice error" role="alert">{error}</p>}
    </div>
    {!!status?.log_tail?.length && <pre className="intake-log" tabIndex={0} aria-label={`Last log lines for ${upload.title}`}>{status.log_tail.join('\n')}</pre>}
  </li>;
}

export function IntakeUploads({ uploads, currentId, onOpen, error }: {
  uploads: Upload[] | null; currentId: string | null; onOpen: (id: string) => void; error: string }) {
  return <section className="intake-section" aria-labelledby="uploads-heading">
    <h2 id="uploads-heading">2. Prepare and open an upload</h2>
    <p className="muted">Docling converts the PDF into a review packet. The Gemma audit is optional and is chosen here, once, per upload.</p>
    {error && <p className="notice error" role="alert">{error}</p>}
    {uploads === null && !error && <p className="muted" role="status">Loading uploads…</p>}
    {uploads?.length === 0 && <p className="muted">No uploads yet.</p>}
    <ul className="intake-list">{uploads?.map(upload =>
      <UploadRow key={upload.upload_id} upload={upload} current={currentId === upload.upload_id} onOpen={onOpen} />)}</ul>
  </section>;
}
