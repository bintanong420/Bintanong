'use client';

import { useCallback, useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { ReviewError, request } from '@/lib/api';
import { isNoPacketError } from '@/lib/intake';
import { prospectusDocuments } from '@/lib/review-nav';
import { reviewPath } from '@/lib/review-path';
import { REVIEW_CONNECTION, type ReviewState } from '@/lib/review-state';

type Loaded = { kind: 'loading' } | { kind: 'none' } | { kind: 'error'; message: string }
  | { kind: 'ready'; documents: ReturnType<typeof prospectusDocuments> };

export default function ProspectusList() {
  const [view, setView] = useState<Loaded>({ kind: 'loading' });
  const load = useCallback(async () => {
    setView({ kind: 'loading' });
    try {
      const state: ReviewState = await (await request(REVIEW_CONNECTION, '/api/state')).json();
      setView({ kind: 'ready', documents: prospectusDocuments(state) });
    } catch (failure) {
      if (failure instanceof ReviewError && isNoPacketError(failure.message, failure.status)) setView({ kind: 'none' });
      else setView({ kind: 'error', message: failure instanceof Error ? failure.message : 'The prospectus documents could not be loaded.' });
    }
  }, []);
  useEffect(() => { void load(); }, [load]);

  return <main className="page-main" id="review-main">
    <div className="page-toolbar"><div><h1 className="page-title">Prospectus</h1>
      <p className="muted">Course-by-course review of the prospectus documents in the open packet.</p></div></div>
    <div className="page-body" aria-live="polite">
      {view.kind === 'loading' && <div role="status" aria-busy="true"><p className="muted"><span className="spinner" aria-hidden="true" /> Loading documents…</p>
        <ul className="doc-list" aria-hidden="true">{[0, 1].map(n => <li key={n} className="doc-card"><span className="skeleton skeleton-title" /><span className="skeleton skeleton-short" /></li>)}</ul></div>}
      {view.kind === 'none' && <div className="empty-state"><h2>Nothing is open for review</h2>
        <p className="muted">Prospectus documents appear here once an upload is open. Prepare an upload on the Intake tab, then choose Open for review.</p>
        <Button asChild><a href="/review/intake">Go to Intake</a></Button></div>}
      {view.kind === 'error' && <div className="notice error" role="alert"><span><strong>The prospectus documents could not be loaded.</strong> {view.message}</span>
        <Button variant="outline" size="sm" onClick={() => void load()}>Try again</Button></div>}
      {view.kind === 'ready' && !view.documents.length && <div className="empty-state"><h2>No prospectus in this packet</h2>
        <p className="muted">The open packet has no prospectus documents. Handbook and Charter records are on the Documents tab.</p>
        <Button variant="outline" asChild><a href="/review">Go to Documents</a></Button></div>}
      {view.kind === 'ready' && !!view.documents.length && <>
        <p className="muted">{view.documents.length} {view.documents.length === 1 ? 'document' : 'documents'}</p>
        <ul className="doc-list">{view.documents.map(doc => <li key={doc.id} className="doc-card">
          <div><h2 className="doc-title">{doc.title}</h2><p className="muted">{doc.edition} · {doc.records} {doc.records === 1 ? 'record' : 'records'}</p></div>
          <Button asChild><a href={reviewPath({ kind: 'prospectus', document: doc.id })} aria-label={`Review ${doc.title}`}>Review</a></Button>
        </li>)}</ul></>}
    </div>
  </main>;
}
