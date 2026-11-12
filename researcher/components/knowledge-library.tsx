'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { request } from '@/lib/api';
import { chunkCountText, documentLink, documentsPath, documentTitle, groupLabel, libraryGroups, pageRangeText, pdfText,
  type DocumentsReply, type KnowledgeSource, type SourcesReply } from '@/lib/knowledge';
import { REVIEW_CONNECTION } from '@/lib/review-state';

type Load<T> = { kind: 'loading' } | { kind: 'error'; message: string } | { kind: 'ready'; value: T };
const message = (error: unknown, fallback: string) => error instanceof Error ? error.message : fallback;

// Read-only library of the documents already stored in each knowledge source. Nothing here changes any database.
export function KnowledgeLibrary({ headingId }: { headingId?: string }) {
  const [sources, setSources] = useState<Load<SourcesReply>>({ kind: 'loading' });
  const [docs, setDocs] = useState<Record<string, Load<DocumentsReply>>>({});
  const [open, setOpen] = useState<Record<string, boolean>>({});
  const asked = useRef(new Set<string>());

  const loadSources = useCallback(async () => {
    setSources({ kind: 'loading' });
    try {
      const value: SourcesReply = await (await request(REVIEW_CONNECTION, '/api/knowledge/sources')).json();
      setSources({ kind: 'ready', value });
      const first = libraryGroups(value.sources)[0]?.sources[0];
      if (first) { setOpen(current => ({ ...current, [first.id]: true })); void loadDocuments(first.id); }
    } catch (failure) { setSources({ kind: 'error', message: message(failure, 'The knowledge sources could not be loaded.') }); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadDocuments(id: string, retry = false) {
    if (asked.current.has(id) && !retry) return;
    asked.current.add(id);
    setDocs(current => ({ ...current, [id]: { kind: 'loading' } }));
    try {
      const value: DocumentsReply = await (await request(REVIEW_CONNECTION, documentsPath(id))).json();
      setDocs(current => ({ ...current, [id]: { kind: 'ready', value } }));
    } catch (failure) {
      setDocs(current => ({ ...current, [id]: { kind: 'error', message: message(failure, 'The documents could not be loaded.') } }));
    }
  }

  useEffect(() => { void loadSources(); }, [loadSources]);

  function toggle(id: string) {
    const next = !open[id];
    setOpen(current => ({ ...current, [id]: next }));
    if (next) void loadDocuments(id);
  }

  const all = sources.kind === 'ready' ? sources.value.sources : [];
  const unavailable = sources.kind === 'ready' ? sources.value.unavailable : undefined;

  return <div className="library" aria-labelledby={headingId}>
    {sources.kind === 'loading' && <p className="muted" role="status"><span className="spinner" aria-hidden="true" /> Loading the knowledge sources…</p>}
    {sources.kind === 'error' && <div className="notice error" role="alert"><span><strong>The knowledge sources could not be loaded.</strong> {sources.message}</span>
      <Button variant="outline" size="sm" onClick={() => void loadSources()}>Try again</Button></div>}
    {unavailable?.hosted && <p className="notice hold"><span><strong>Online knowledge is not available.</strong> {unavailable.hosted}</span></p>}
    {unavailable?.local && <p className="notice hold"><span><strong>The local copy is not available.</strong> {unavailable.local}</span></p>}
    {sources.kind === 'ready' && !all.length && <div className="empty-state"><h3>No knowledge stored yet</h3>
      <p className="muted">Build chunks for a prepared upload on the Intake page, or start the local database, and the documents appear here.</p>
      <Button asChild variant="outline"><a href="/review/intake">Go to Intake</a></Button></div>}

    {libraryGroups(all).map(group => <section key={group.kind} className="library-group" aria-label={group.heading}>
      <h3 className="library-heading">{group.heading}{groupLabel(group.kind).note && <span className="library-note"> · {groupLabel(group.kind).note}</span>}</h3>
      <ul className="entry-list">{group.sources.map(source => <li key={source.id}>
        <SourceRow source={source} expanded={!!open[source.id]} onToggle={() => toggle(source.id)}
          docs={docs[source.id]} onRetry={() => void loadDocuments(source.id, true)} />
      </li>)}</ul>
    </section>)}
  </div>;
}

function SourceRow({ source, expanded, onToggle, docs, onRetry }:
  { source: KnowledgeSource; expanded: boolean; onToggle: () => void; docs?: Load<DocumentsReply>; onRetry: () => void }) {
  const panel = 'library-panel-' + source.id.replace(/[^A-Za-z0-9_-]/g, '-');
  const meta = [source.active ? 'Active release' : '', source.status && !source.active ? 'Status: ' + source.status : '',
    source.chunk_count !== undefined ? chunkCountText(source.chunk_count) : ''].filter(Boolean).join(' · ');
  return <div className="library-source">
    <h4><button type="button" className="entry library-toggle" aria-expanded={expanded} aria-controls={panel} onClick={onToggle}>
      <span className="entry-head"><strong>{source.label}</strong>{meta && <span className="row-meta">{meta}</span>}</span>
      <span className="chevron" aria-hidden="true" />
    </button></h4>
    {expanded && <div id={panel} className="library-docs">
      {(!docs || docs.kind === 'loading') && <p className="muted" role="status"><span className="spinner" aria-hidden="true" /> Loading documents…</p>}
      {docs?.kind === 'error' && <div className="notice error" role="alert"><span><strong>The documents could not be loaded.</strong> {docs.message}</span>
        <Button variant="outline" size="sm" onClick={onRetry}>Try again</Button></div>}
      {docs?.kind === 'ready' && <>
        {docs.value.truncated && <p className="notice hold"><span>This source holds more chunks than were read here, so counts and page ranges may be low.</span></p>}
        {!docs.value.documents.length ? <div className="empty-state"><h3>This source has no documents</h3>
          <p className="muted">Nothing has been stored in it yet.</p></div>
          : <ul className="entry-list">{docs.value.documents.map(doc => <li key={doc.document_key}>
            <a className="entry doc-row" href={documentLink(source.id, doc)}>
              <strong className="entry-title">{documentTitle(doc)}</strong>
              <span className="row-meta">{chunkCountText(doc.chunk_count)} · {pageRangeText(doc.pages)}</span>
              <span className="row-meta">{pdfText(doc)}</span>
            </a></li>)}</ul>}
      </>}
    </div>}
  </div>;
}
