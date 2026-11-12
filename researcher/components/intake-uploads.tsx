'use client';

import { forwardRef, useEffect, useRef, useState } from 'react';
import { IntakeBuild } from '@/components/intake-build';
import { PipelineSteps, StatusIcon, StatusTag } from '@/components/intake-status';
import { Button } from '@/components/ui/button';
import type { UploadState } from '@/components/use-upload-states';
import { request, ReviewError } from '@/lib/api';
import { buildBlocker, buildChecklist, buildControl, nextStep, buildSummary, formatBytes, INTERRUPTED_NOTE, opensMetadataForm, REBUILD_NOTE, formatElapsed, latestLogLine, pipelineSteps } from '@/lib/intake';
import { knowledgeUrl, packageSourceId } from '@/lib/knowledge';
import { REVIEW_CONNECTION } from '@/lib/review-state';

export type Upload = { upload_id: string; kind: string; title: string; edition: string; bytes: number; sha256?: string };

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

function Skeleton() {
  return <ul className="upload-rows" aria-hidden="true">{[0, 1, 2].map(n => <li key={n} className="upload-row"><span className="skeleton skeleton-title" /><span className="skeleton skeleton-short" /></li>)}</ul>;
}

export function UploadList({ uploads, states, currentId, selectedId, onSelect, error, onRetry }: {
  uploads: Upload[] | null; states: Record<string, UploadState>; currentId: string | null; selectedId: string | null;
  onSelect: (id: string) => void; error: string; onRetry: () => void }) {
  return <section className="upload-list" aria-labelledby="uploads-heading">
    <div className="list-head"><h2 id="uploads-heading">Uploads</h2>
      {!!uploads?.length && <span className="muted">{uploads.length}</span>}</div>
    {error && <div className="notice error" role="alert"><span><strong>The uploads could not be loaded.</strong> {error}</span>
      <Button variant="outline" size="sm" onClick={onRetry}>Try again</Button></div>}
    {uploads === null && !error && <div role="status" aria-busy="true"><p className="muted"><span className="spinner" aria-hidden="true" /> Loading uploads…</p><Skeleton /></div>}
    {uploads?.length === 0 && <div className="empty-state"><h3>No uploads yet</h3>
      <p className="muted">Upload a PDF above. It appears here with its progress.</p></div>}
    <ul className="upload-rows">{uploads?.map(upload => {
      const state = states[upload.upload_id], steps = pipelineSteps(state?.prepare?.state, currentId === upload.upload_id, state?.build);
      return <li key={upload.upload_id}>
        <button type="button" className="upload-row" aria-current={selectedId === upload.upload_id ? 'true' : undefined} onClick={() => onSelect(upload.upload_id)}>
          <span className="row-top"><strong className="row-title">{upload.title}</strong>
            {currentId === upload.upload_id && <span className="row-open">Open for review</span>}</span>
          <span className="row-meta">{upload.edition} · {KIND_LABEL[upload.kind] ?? upload.kind} · {formatBytes(upload.bytes)}</span>
          <span className="row-meta">Upload ending {upload.upload_id.slice(-6)}</span>
          <span className="mini-steps">{steps.map(step => <span key={step.key} className={`mini-step tag-${step.status}`}>
            <StatusIcon status={step.status} />{step.label}<span className="sr-only">: {step.text}</span></span>)}</span>
        </button></li>;
    })}</ul>
  </section>;
}

type DetailProps = { upload: Upload; state: UploadState | undefined; current: boolean; onOpen: (id: string) => void;
  onChanged: (id: string) => Promise<void>; onPatch: (id: string, change: Partial<UploadState>) => void;
  onCompare: () => void; comparing: boolean };

export const UploadDetail = forwardRef<HTMLHeadingElement, DetailProps>(function UploadDetail(
    { upload, state: entry, current, onOpen, onChanged, onPatch, onCompare, comparing }, headingRef) {
  const [busy, setBusy] = useState(false), [refused, setRefused] = useState(''), [buildRefused, setBuildRefused] = useState('');
  const [buildCode, setBuildCode] = useState<string | undefined>(), [formOpen, setFormOpen] = useState(false);
  const [planSaved, setPlanSaved] = useState<boolean | undefined>();
  const formSummary = useRef<HTMLElement>(null);
  const status = entry?.prepare, build = entry?.build, state = status?.state;
  const steps = pipelineSteps(state, current, build);
  const prepareElapsed = useElapsed(state === 'running'), buildElapsed = useElapsed(build?.state === 'running');
  const logLines = status?.log_tail ?? [], buildLog = build?.log_tail ?? [];
  const gemmaGaps = status?.gemma_unavailable_fields ?? 0;
  const id = upload.upload_id, base = 'upload-' + id;
  const stopped = state === 'failed' || state === 'interrupted';
  const buildStopped = build?.state === 'failed' || build?.state === 'interrupted';
  const control = buildControl(state === 'done', build);
  // the open upload's form is checked against the current review; any other upload only shows whether a form file exists
  const formSaved = current ? planSaved : build ? build.metadata_saved : undefined;
  const blocker = buildBlocker(state === 'done', formSaved, current);

  async function start(assist: boolean) {
    setBusy(true); setRefused('');
    try {
      onPatch(id, { prepare: await (await request(REVIEW_CONNECTION, '/api/intake/prepare',
        { method: 'POST', body: JSON.stringify({ upload_id: id, assist }) })).json() });
    } catch (failure) {
      // the server decides whether Docling or Gemma is configured; its refusal is shown as written and the upload stays not started
      setRefused(message(failure));
    } finally { setBusy(false); }
  }

  async function startBuild() {
    setBusy(true); setBuildRefused(''); setBuildCode(undefined);
    try {
      await request(REVIEW_CONNECTION, '/api/intake/build', { method: 'POST', body: JSON.stringify({ upload_id: id }) });
      await onChanged(id);
    } catch (failure) {
      // the server's wording is shown as written; its code only decides what else to do
      setBuildRefused(message(failure));
      const code = failure instanceof ReviewError ? failure.code : undefined;
      setBuildCode(code);
      if (opensMetadataForm(code) && current) { setFormOpen(true); setTimeout(() => formSummary.current?.focus(), 0); }
      if (code === 'package_exists' || code === 'build_running') await onChanged(id);
    }
    finally { setBusy(false); }
  }

  return <article className="upload-detail" aria-labelledby={base + '-title'}>
    <div className="upload-head">
      <h2 id={base + '-title'} tabIndex={-1} ref={headingRef}>{upload.title}</h2>
      {current && <StatusTag status="active">Open for review</StatusTag>}
    </div>
    <dl className="upload-meta">
      <div><dt>Edition</dt><dd>{upload.edition}</dd></div>
      <div><dt>Kind</dt><dd>{KIND_LABEL[upload.kind] ?? upload.kind}</dd></div>
      <div><dt>Size</dt><dd>{formatBytes(upload.bytes)}</dd></div>
      <div><dt>Upload id</dt><dd><code>{id}</code></dd></div>
    </dl>
    <p className="next-step" role="status"><strong>{nextStep({ prepare: state, open: current, build: build?.state, formSaved })}</strong></p>
    <PipelineSteps steps={steps} label={`Progress for ${upload.title}`} />
    {entry?.error && <p className="notice error" role="alert"><span>{entry.error}</span>
      <Button variant="outline" size="sm" onClick={() => void onChanged(id)}>Check again</Button></p>}

    <section className="step-block" aria-labelledby={base + '-prepare'}>
      <h3 id={base + '-prepare'}>Prepare</h3>
      <div aria-live="polite" className="upload-status">
        {state === 'running' && <p className="notice"><span className="spinner" aria-hidden="true" /><span>Docling is preparing this document. This page checks every 3 seconds. Seen running for {formatElapsed(prepareElapsed)} on this page.</span></p>}
        {state === 'done' && <p className="notice success"><span>Prepared{status?.assist ? ' with the Gemma audit of flagged pages' : ''}. It can now be opened for review.</span></p>}
        {state === 'done' && gemmaGaps > 0 && <p className="notice hold"><span><strong>Gemma could not assist {gemmaGaps} {gemmaGaps === 1 ? 'field' : 'fields'}.</strong> Review {gemmaGaps === 1 ? 'it' : 'those'} against the original page by hand.</span></p>}
        {state === 'not_started' && <p className="notice"><span>Not prepared yet. Choose one option below. The choice is made once per upload.</span></p>}
      </div>
      {stopped && <p className="notice error" role="alert"><span>
        <strong>{state === 'failed' ? 'Prepare failed.' : 'Prepare was interrupted.'}</strong>{' '}
        {state === 'interrupted' ? 'The review server restarted while it ran. ' : ''}
        {status?.exit_code !== undefined && `Exit code ${status.exit_code}. `}{status?.error ?? ''}{' '}
        To retry, upload the document again: each upload is prepared once.</span></p>}
      {refused && <p className="notice error" role="alert"><span><strong>The server did not start Prepare.</strong> {refused}{' '}
        Nothing was started, so you can choose the other option or fix the setup and try again.</span></p>}
      {state === 'not_started' && <div className="intake-actions">
        <div className="action-choice">
          <Button disabled={busy} onClick={() => void start(false)} aria-describedby={base + '-plain'}>Prepare with Docling</Button>
          <p className="hint" id={base + '-plain'}>Turns the PDF into a draft you can review.</p></div>
        <div className="action-choice">
          <Button variant="outline" disabled={busy} onClick={() => void start(true)} aria-describedby={base + '-gemma'}>Prepare with Gemma audit</Button>
          <p className="hint" id={base + '-gemma'}>Also has a local Gemma model double-check flagged pages. It needs that model set up when the tool starts; the server says if it is missing.</p></div>
      </div>}
      {state && state !== 'not_started' && <p className="hint">This choice cannot be changed. To prepare differently, upload the file again.</p>}
      {!!logLines.length && <div className="log-viewer">
        {latestLogLine(logLines) && <p className="muted">Latest message: {latestLogLine(logLines)}</p>}
        <details open={stopped}>
          <summary>Log ({logLines.length} {logLines.length === 1 ? 'line' : 'lines'})</summary>
          <pre className="intake-log" tabIndex={0} role="region" aria-label={`Technical log for ${upload.title}`}>{logLines.join('\n')}</pre>
        </details></div>}
    </section>

    <section className="step-block" aria-labelledby={base + '-review'}>
      <h3 id={base + '-review'}>Review</h3>
      <div className="intake-actions">
        <div className="action-choice">
          <Button disabled={state !== 'done' || current} onClick={() => onOpen(id)} aria-describedby={base + '-open'}>
            {current ? 'Open for review (already open)' : 'Open for review'}</Button>
          <p className="hint" id={base + '-open'}>{current ? 'Continue on the Documents tab.'
            : state === 'done' ? 'Opens this draft on the Documents page.' : state === undefined ? 'Waiting for the Prepare status.'
            : 'Available once Prepare is done.'}</p></div>
        {current && <div className="action-choice"><Button variant="outline" asChild><a href="/review">Go to Documents</a></Button></div>}
        <div className="action-choice">
          <Button variant="outline" disabled={state !== 'done'} aria-pressed={comparing} onClick={onCompare} aria-describedby={base + '-compare'}>
            {comparing ? 'Comparison open below' : 'Compare extraction'}</Button>
          <p className="hint" id={base + '-compare'}>{state === 'done' ? 'Shows each source page beside the text extracted from it.' : 'Available once Prepare is done.'}</p></div>
      </div>
    </section>

    <section className="step-block" aria-labelledby={base + '-build'}>
      <h3 id={base + '-build'}>Build</h3>
      <div aria-live="polite" className="upload-status">
        {build?.state === 'running' && <p className="notice"><span className="spinner" aria-hidden="true" /><span>Building the knowledge package. This page checks every 3 seconds. Seen running for {formatElapsed(buildElapsed)} on this page.</span></p>}
        {build?.state === 'done' && <p className="notice success"><span><strong>{buildSummary(build) || 'Built'}.</strong>{' '}
          {build.package ? <a href={knowledgeUrl({ source: packageSourceId(id), q: '', chunk: '', document: '', offset: 0 })}>View these chunks in Knowledge</a> : 'The server returned no package details.'}</span></p>}
        {control.kind === 'none' && <p className="hint">{build?.state === 'interrupted' ? INTERRUPTED_NOTE : REBUILD_NOTE}</p>}
        {control.kind === 'start' && <>
          <p className="hint">Building turns the prepared draft into chunks you can browse in Knowledge. It approves and activates nothing, and it runs once per upload.</p>
          <ul className="checklist" aria-label="Before the first build">{buildChecklist(state === 'done', formSaved).map(row =>
            <li key={row.key}><StatusTag status={row.status}>{row.text}</StatusTag></li>)}</ul></>}
      </div>
      {buildStopped && <p className="notice error" role="alert"><span>
        <strong>{build?.state === 'failed' ? 'Build failed.' : 'Build was interrupted.'}</strong>{' '}
        {build?.state === 'interrupted' ? 'The review server restarted while it ran. ' : ''}
        {build?.exit_code !== undefined && `Exit code ${build.exit_code}. `}{build?.error ?? ''}</span></p>}
      {buildRefused && <p className="notice error" role="alert"><span><strong>The server did not start Build.</strong> {buildRefused}
        {opensMetadataForm(buildCode) && !current && ' Open this upload for review, then save its passages and claims form.'}</span></p>}
      {entry?.buildError && <p className="notice error" role="alert"><span><strong>The Build status could not be checked.</strong> {entry.buildError}</span>
        <Button variant="outline" size="sm" onClick={() => void onChanged(id)}>Check again</Button></p>}
      {(control.kind === 'start' || control.kind === 'retry') && <div className="intake-actions"><div className="action-choice">
        <Button disabled={busy || !!blocker} onClick={() => void startBuild()} aria-describedby={base + '-build-hint'}>{control.label}</Button>
        <p className="hint" id={base + '-build-hint'}>{blocker ? blocker
          : control.kind === 'retry' ? 'A retry is allowed only while no package was produced.' : 'Starts one build for this upload on the review server.'}</p></div></div>}
      {!!buildLog.length && <div className="log-viewer"><details open={buildStopped}>
        <summary>Log ({buildLog.length} {buildLog.length === 1 ? 'line' : 'lines'})</summary>
        <pre className="intake-log" tabIndex={0} role="region" aria-label={`Build log for ${upload.title}`}>{buildLog.join('\n')}</pre></details></div>}
    </section>

    {current && <details className="metadata-form" open={formOpen} onToggle={event => setFormOpen(event.currentTarget.open)}>
      <summary ref={formSummary}>Passages and claims form (needed before the first build)</summary>
      <IntakeBuild uploadId={id} onFormState={setPlanSaved} />
    </details>}
  </article>;
});
