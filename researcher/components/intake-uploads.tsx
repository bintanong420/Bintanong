'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { PipelineSteps, StatusTag } from '@/components/intake-status';
import { Button } from '@/components/ui/button';
import { request } from '@/lib/api';
import { formatBytes, formatElapsed, latestLogLine, pipelineSteps, shouldPoll } from '@/lib/intake';
import { REVIEW_CONNECTION } from '@/lib/review-state';

export type Upload = { upload_id: string; kind: string; title: string; edition: string; bytes: number };
type Status = { state: string; exit_code?: number; error?: string; log_tail?: string[];
  gemma_unavailable_fields?: number; assist?: boolean };

const KIND_LABEL: Record<string, string> = { handbook: 'Handbook', charter: 'Citizens’ Charter' };
function message(error: unknown) { return error instanceof Error ? error.message : 'The request failed.'; }

// Counts up from the moment this page first saw the job running. The server keeps no start time, so this is a lower bound.
function useElapsed(running: boolean) {
  const since = useRef<number | null>(null);
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!running) { since.current = null; return; }
    since.current ??= Date.now();
    setNow(Date.now());
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [running]);
  return running && since.current !== null ? now - since.current : 0;
}

function UploadRow({ upload, current, onOpen }: { upload: Upload; current: boolean; onOpen: (id: string) => void }) {
  const [status, setStatus] = useState<Status | null>(null), [error, setError] = useState(''), [busy, setBusy] = useState(false);
  const [refused, setRefused] = useState('');
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
    setBusy(true); setError(''); setRefused('');
    try {
      setStatus(await (await request(REVIEW_CONNECTION, '/api/intake/prepare',
        { method: 'POST', body: JSON.stringify({ upload_id: upload.upload_id, assist }) })).json());
    } catch (failure) {
      // the server decides whether Docling or Gemma is configured; its refusal is shown as written and the upload stays not started
      setRefused(message(failure));
    } finally { setBusy(false); }
  }

  const state = status?.state, steps = pipelineSteps(state, current);
  const elapsed = useElapsed(state === 'running');
  const logLines = status?.log_tail ?? [];
  const gemmaGaps = status?.gemma_unavailable_fields ?? 0;
  const baseId = 'upload-' + upload.upload_id;
  const titleId = baseId + '-title';
  const stopped = state === 'failed' || state === 'interrupted';

  return <li className="intake-upload" aria-labelledby={titleId}>
    <div className="upload-head">
      <h3 id={titleId}>{upload.title}</h3>
      {current && <StatusTag status="active">Open for review</StatusTag>}
    </div>
    <dl className="upload-meta">
      <div><dt>Edition</dt><dd>{upload.edition}</dd></div>
      <div><dt>Kind</dt><dd>{KIND_LABEL[upload.kind] ?? upload.kind}</dd></div>
      <div><dt>Size</dt><dd>{formatBytes(upload.bytes)}</dd></div>
      <div><dt>Upload id</dt><dd><code>{upload.upload_id}</code></dd></div>
    </dl>
    <PipelineSteps steps={steps} label={`Progress for ${upload.title}`} />

    <div aria-live="polite" className="upload-status">
      {state === 'running' && <p className="notice"><span className="spinner" aria-hidden="true" /><span>Docling is preparing this document. This page checks every 3 seconds.</span></p>}
      {state === 'done' && <p className="notice success"><span>Prepared{status?.assist ? ' with the Gemma audit of flagged pages' : ''}. It can now be opened for review.</span></p>}
      {state === 'done' && gemmaGaps > 0 && <p className="notice hold"><span><strong>Gemma could not assist {gemmaGaps} {gemmaGaps === 1 ? 'field' : 'fields'}.</strong> Review {gemmaGaps === 1 ? 'it' : 'those'} against the original page by hand.</span></p>}
      {state === 'not_started' && <p className="notice"><span>Not prepared yet. Choose one option below. The choice is made once per upload.</span></p>}
    </div>
    {state === 'running' && <p className="muted" aria-hidden="true">Seen running for {formatElapsed(elapsed)} on this page.</p>}
    {stopped && <p className="notice error" role="alert"><span>
      <strong>{state === 'failed' ? 'Prepare failed.' : 'Prepare was interrupted.'}</strong>{' '}
      {state === 'interrupted' ? 'The review server restarted while it ran. ' : ''}
      {status?.exit_code !== undefined && `Exit code ${status.exit_code}. `}{status?.error ?? ''}{' '}
      To retry, upload the document again: one packet is made per upload.</span></p>}
    {refused && <p className="notice error" role="alert"><span><strong>The server did not start Prepare.</strong> {refused}{' '}
      Nothing was started, so you can choose the other option or fix the setup and try again.</span></p>}
    {error && <p className="notice error" role="alert"><span>{error}</span><Button variant="outline" size="sm" onClick={() => void refresh()}>Check again</Button></p>}

    {state === 'not_started' && <div className="intake-actions">
      <div className="action-choice">
        <Button disabled={busy} onClick={() => void start(false)} aria-describedby={baseId + '-plain'}>Run Docling</Button>
        <p className="hint" id={baseId + '-plain'}>Converts the PDF into a review packet.</p></div>
      <div className="action-choice">
        <Button variant="outline" disabled={busy} onClick={() => void start(true)} aria-describedby={baseId + '-gemma'}>Run Docling + Gemma audit</Button>
        <p className="hint" id={baseId + '-gemma'}>Also asks a local Gemma model to audit flagged pages. It needs that model configured on the review command; the server says if it is not.</p></div>
    </div>}
    {state && state !== 'not_started' && <p className="hint">The Docling or Gemma choice cannot be changed for this upload. A different choice needs a new upload.</p>}
    <div className="intake-actions">
      <div className="action-choice">
        <Button disabled={state !== 'done' || current} onClick={() => onOpen(upload.upload_id)} aria-describedby={baseId + '-open'}>
          {current ? 'Open for review (already open)' : 'Open for review'}</Button>
        <p className="hint" id={baseId + '-open'}>{current ? 'Continue on the review page.'
          : state === 'done' ? 'Opens this packet in the review tool.' : state === undefined ? 'Waiting for the Prepare status.'
          : 'Available once Prepare is done.'}</p></div>
      {current && <div className="action-choice"><Button variant="outline" asChild><a href="/review">Go to review</a></Button></div>}
    </div>

    {!!logLines.length && <div className="log-viewer">
      {latestLogLine(logLines) && <p className="muted">Latest message: {latestLogLine(logLines)}</p>}
      <details>
        <summary>Technical log ({logLines.length} {logLines.length === 1 ? 'line' : 'lines'}, raw)</summary>
        <pre className="intake-log" tabIndex={0} role="region" aria-label={`Technical log for ${upload.title}`}>{logLines.join('\n')}</pre>
      </details></div>}
  </li>;
}

function Skeleton() {
  return <ul className="intake-list" aria-hidden="true">{[0, 1].map(n => <li key={n} className="intake-upload">
    <span className="skeleton skeleton-title" /><span className="skeleton" /><span className="skeleton skeleton-short" /></li>)}</ul>;
}

export function IntakeUploads({ uploads, currentId, onOpen, error, onRetry }: {
  uploads: Upload[] | null; currentId: string | null; onOpen: (id: string) => void; error: string; onRetry: () => void }) {
  return <section className="intake-section" id="prepare" aria-labelledby="uploads-heading">
    <div className="section-head"><span className="section-number" aria-hidden="true">2</span>
      <div><h2 id="uploads-heading">Prepare and open an upload</h2>
        <p className="muted">Docling converts the PDF into a review packet. The Gemma audit is optional and is chosen here, once, per upload.</p></div></div>
    {error && <div className="notice error" role="alert"><span><strong>The uploads could not be loaded.</strong> {error}</span>
      <Button variant="outline" size="sm" onClick={onRetry}>Try again</Button></div>}
    {uploads === null && !error && <div role="status" aria-busy="true"><p className="muted"><span className="spinner" aria-hidden="true" /> Loading uploads…</p><Skeleton /></div>}
    {uploads?.length === 0 && <div className="empty-state"><h3>No uploads yet</h3>
      <p className="muted">Upload a PDF in step 1. It will appear here with its progress, ready to prepare.</p>
      <p><a href="#upload">Go to step 1</a></p></div>}
    {!!uploads?.length && <p className="muted">{uploads.length} {uploads.length === 1 ? 'upload' : 'uploads'}</p>}
    <ul className="intake-list">{uploads?.map(upload =>
      <UploadRow key={upload.upload_id} upload={upload} current={currentId === upload.upload_id} onOpen={onOpen} />)}</ul>
  </section>;
}
