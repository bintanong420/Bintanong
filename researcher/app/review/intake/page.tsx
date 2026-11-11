'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { CompareExtraction } from '@/components/compare-extraction';
import { IntakeUpload } from '@/components/intake-upload';
import { UploadDetail, UploadList, type Upload } from '@/components/intake-uploads';
import { useUploadStates } from '@/components/use-upload-states';
import { Button } from '@/components/ui/button';
import { request } from '@/lib/api';
import { REVIEW_CONNECTION } from '@/lib/review-state';

const ids = (uploads: Upload[] | null) => uploads?.map(u => u.upload_id) ?? [];

export default function IntakePage() {
  const [uploads, setUploads] = useState<Upload[] | null>(null), [currentId, setCurrentId] = useState<string | null>(null);
  const [error, setError] = useState(''), [opening, setOpening] = useState(false), [openError, setOpenError] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null), [comparing, setComparing] = useState(false);
  const { states, refresh, patch } = useUploadStates(ids(uploads));
  const heading = useRef<HTMLHeadingElement>(null), compare = useRef<HTMLDivElement>(null);
  const wanted = useRef<string | null>(null);  // an upload id asked for by the address or by a fresh upload

  const load = useCallback(async () => {
    try {
      const list: Upload[] = (await (await request(REVIEW_CONNECTION, '/api/intake/uploads')).json()).uploads;
      setCurrentId((await (await request(REVIEW_CONNECTION, '/api/intake/current')).json()).upload_id);
      setUploads(list); setError('');
      // keep the choice if it still exists; otherwise the requested upload; the open one or the first is the fallback below
      setSelectedId(previous => [previous, wanted.current].find(id => id && list.some(u => u.upload_id === id)) ?? null);
    } catch (failure) { setError(failure instanceof Error ? failure.message : 'The uploads could not be loaded.'); }
  }, []);

  useEffect(() => {
    wanted.current = new URLSearchParams(window.location.search).get('upload');
    void load();
  }, [load]);

  const fallback = uploads?.find(u => u.upload_id === currentId)?.upload_id ?? uploads?.[0]?.upload_id ?? null;
  const shownId = selectedId ?? fallback;
  const shown = uploads?.find(u => u.upload_id === shownId) ?? null;

  function select(id: string) {
    setSelectedId(id); setComparing(false); setOpenError('');
    window.history.replaceState(null, '', '/review/intake?upload=' + encodeURIComponent(id));
    // one column on a phone: bring the detail into view and announce it
    if (window.matchMedia('(max-width: 900px)').matches) setTimeout(() => heading.current?.focus(), 0);
  }
  function uploaded(id: string) { wanted.current = id; setSelectedId(id); setComparing(false); void load(); }

  async function open(uploadId: string) {
    if (opening) return;
    setOpening(true); setOpenError('');
    try {
      await request(REVIEW_CONNECTION, '/api/intake/open', { method: 'POST', body: JSON.stringify({ upload_id: uploadId }) });
      window.location.assign('/review');  // the Documents tab loads the opened packet
    } catch (failure) {
      setOpenError(failure instanceof Error ? failure.message : 'The upload could not be opened.');
      setOpening(false);
    }
  }
  function showCompare() {
    setComparing(true);
    setTimeout(() => compare.current?.scrollIntoView({ block: 'start' }), 0);
  }

  return <main className="page-main intake-page" id="review-main">
    <div className="page-toolbar"><div><h1 className="page-title">Intake</h1>
      <p className="muted">Upload a handbook-style PDF, prepare it, review it, then build chunks. Nothing here approves content or activates it.</p></div></div>
    <div className="intake-grid">
      <div className="intake-side">
        <details className="upload-panel" open={uploads?.length === 0 ? true : undefined}>
          <summary>Upload a PDF</summary>
          <IntakeUpload onUploaded={uploaded} />
        </details>
        <UploadList uploads={uploads} states={states} currentId={currentId} selectedId={shownId}
          onSelect={select} error={error} onRetry={() => void load()} />
      </div>
      <div className="intake-main">
        {openError && <div className="notice error" role="alert"><span><strong>The upload could not be opened.</strong> {openError}</span>
          <Button variant="outline" size="sm" onClick={() => setOpenError('')}>Dismiss</Button></div>}
        {shown ? <UploadDetail key={shown.upload_id} ref={heading} upload={shown} state={states[shown.upload_id]}
          current={currentId === shown.upload_id} onOpen={id => void open(id)} onChanged={refresh} onPatch={patch}
          onCompare={showCompare} comparing={comparing} />
          : <div className="empty-state"><h2>{uploads === null ? 'Loading…' : 'Select an upload'}</h2>
            <p className="muted">{uploads === null ? 'Fetching the upload list.' : 'Its Prepare, Review and Build steps appear here. Upload a PDF to start.'}</p></div>}
      </div>
      {comparing && shown && <div className="intake-compare" ref={compare}>
        <CompareExtraction key={shown.upload_id} uploadId={shown.upload_id} sha256={shown.sha256} title={shown.title} onClose={() => setComparing(false)} /></div>}
    </div>
  </main>;
}
