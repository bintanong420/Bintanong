'use client';

import { forwardRef, useCallback, useEffect, useRef, useState } from 'react';
import { PageImage } from '@/components/page-image';
import { PdfFrame, SourceModeSwitch, useSourceMode } from '@/components/pdf-frame';
import { Button } from '@/components/ui/button';
import { request } from '@/lib/api';
import { knowledgePdfPath } from '@/lib/pdf-view';
import { CHUNK_LIMIT, chunkMeta, chunksQuery, chunkText, documentChipLabel, groupSources, snippet, knowledgeUrl, pageWindow, parseKnowledgeUrl,
  type Chunk, type ChunksReply, type KnowledgeUrlState, type SourcesReply } from '@/lib/knowledge';
import { REVIEW_CONNECTION } from '@/lib/review-state';

const message = (error: unknown, fallback: string) => error instanceof Error ? error.message : fallback;
type Load<T> = { kind: 'loading' } | { kind: 'error'; message: string } | { kind: 'ready'; value: T };

export default function KnowledgePage() {
  const [url, setUrl] = useState<KnowledgeUrlState | null>(null), [input, setInput] = useState('');
  const [sources, setSources] = useState<Load<SourcesReply>>({ kind: 'loading' });
  const [chunks, setChunks] = useState<Load<ChunksReply>>({ kind: 'loading' });
  const [reload, setReload] = useState(0);
  const detailHeading = useRef<HTMLHeadingElement>(null);

  // the address is the state: read it once, then keep it in step with every choice
  const latest = useRef<KnowledgeUrlState | null>(null);
  useEffect(() => { const first = parseKnowledgeUrl(window.location.search); latest.current = first; setUrl(first); setInput(first.q); }, []);
  function change(next: Partial<KnowledgeUrlState>) {
    if (!latest.current) return;
    // the address is rewritten here, not inside a state updater: the router must not be updated while React renders
    const merged = { ...latest.current, ...next };
    latest.current = merged;
    window.history.replaceState(null, '', knowledgeUrl(merged));
    setUrl(merged);
  }

  const loadSources = useCallback(async () => {
    setSources({ kind: 'loading' });
    try { setSources({ kind: 'ready', value: await (await request(REVIEW_CONNECTION, '/api/knowledge/sources')).json() }); }
    catch (failure) { setSources({ kind: 'error', message: message(failure, 'The knowledge sources could not be loaded.') }); }
  }, []);
  useEffect(() => { void loadSources(); }, [loadSources]);

  const all = sources.kind === 'ready' ? sources.value.sources : [];
  const source = all.find(s => s.id === url?.source);
  // with no source in the address, open the first one that exists
  useEffect(() => {
    if (url && !url.source && all.length) change({ source: all[0].id });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [all.length, !!url]);

  // debounce the search box into the address
  useEffect(() => {
    if (!url || input === url.q) return;
    const timer = setTimeout(() => change({ q: input, offset: 0, chunk: '' }), 300);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [input]);

  const sourceId = url?.source ?? '', query = url?.q ?? '', offset = url?.offset ?? 0, documentKey = url?.document ?? '';
  useEffect(() => {
    if (!sourceId) return;
    let current = true;
    setChunks({ kind: 'loading' });
    request(REVIEW_CONNECTION, '/api/knowledge/chunks?' + chunksQuery({ source: sourceId, q: query, document: documentKey, offset, limit: CHUNK_LIMIT }))
      .then(async response => { const value: ChunksReply = await response.json(); if (current) setChunks({ kind: 'ready', value }); })
      .catch(failure => { if (current) setChunks({ kind: 'error', message: message(failure, 'The chunks could not be loaded.') }); });
    return () => { current = false; };
  }, [sourceId, query, offset, documentKey, reload]);
  // the chip keeps the name it first learned: a filtered list only ever holds this document's chunks
  const [documentName, setDocumentName] = useState('');
  useEffect(() => {
    if (!documentKey) { setDocumentName(''); return; }
    if (chunks.kind === 'ready') setDocumentName(documentChipLabel(documentKey, chunks.value.chunks));
  }, [documentKey, chunks]);

  const list = chunks.kind === 'ready' ? chunks.value.chunks : [];
  const selected = list.find(chunk => chunk.chunk_id === url?.chunk) ?? null;
  const window_ = chunks.kind === 'ready' ? pageWindow(chunks.value.total, chunks.value.offset, chunks.value.limit || CHUNK_LIMIT) : null;
  const unavailable = sources.kind === 'ready' ? sources.value.unavailable : undefined;
  const groups = groupSources(all);

  // on a phone the detail sits below the list: once it has rendered, bring it into view and read its heading out
  const reveal = useRef(false);
  function pick(chunk: Chunk) {
    reveal.current = window.matchMedia('(max-width: 900px)').matches;
    change({ chunk: chunk.chunk_id });
  }
  const selectedId = selected?.chunk_id;
  useEffect(() => {
    if (!reveal.current || !selectedId) return;
    reveal.current = false;
    detailHeading.current?.focus();
    detailHeading.current?.scrollIntoView({ block: 'start' });
  }, [selectedId]);

  return <main className="page-main" id="review-main">
    <div className="page-toolbar"><div><h1 className="page-title">Knowledge</h1>
      <p className="muted">Read stored chunks beside their source pages. Nothing here changes the data.</p></div></div>

    <div className="page-body knowledge-notes" aria-live="polite">
      {sources.kind === 'loading' && <p className="muted" role="status"><span className="spinner" aria-hidden="true" /> Loading sources…</p>}
      {sources.kind === 'error' && <div className="notice error" role="alert"><span><strong>The knowledge sources could not be loaded.</strong> {sources.message}</span>
        <Button variant="outline" size="sm" onClick={() => void loadSources()}>Try again</Button></div>}
      {unavailable?.local && <p className="notice hold"><span><strong>The local copy is not available.</strong> {unavailable.local}</span></p>}
      {unavailable?.hosted && <p className="notice hold"><span><strong>Online knowledge is not available.</strong> {unavailable.hosted}</span></p>}
      {sources.kind === 'ready' && !all.length && <div className="empty-state"><h2>No knowledge sources yet</h2>
        <p className="muted">Build chunks for a prepared upload on the Intake tab, or start the local database, and they appear here.</p>
        <Button asChild><a href="/review/intake">Go to Intake</a></Button></div>}
    </div>

    {!!all.length && url && <div className="knowledge-grid">
      <div className="knowledge-side">
        <div className="field"><label htmlFor="source">Source</label>
          <select id="source" value={url.source} onChange={event => { setInput(url.q); change({ source: event.target.value, document: '', offset: 0, chunk: '' }); }}>
            {!source && url.source && <option value={url.source}>{url.source} (not in the list)</option>}
            {groups.map(group => <optgroup key={group.kind} label={group.heading}>{group.sources.map(item =>
              <option key={item.id} value={item.id}>{item.label}{item.chunk_count !== undefined ? ` (${item.chunk_count})` : ''}{item.active ? ' · active' : ''}</option>)}</optgroup>)}
          </select>
          {source?.kind === 'hosted' && <p className="hint">Online knowledge, read-only. Nothing here changes the hosted database.</p>}
          {source?.status && <p className="hint">Status: {source.status}</p>}
        </div>
        {url.document && <div className="filter-chip" role="group" aria-label="Document filter">
          <span className="filter-chip-text"><span className="row-meta">Showing one document</span><strong>{documentName || 'Loading…'}</strong></span>
          <button type="button" className="chip filter-clear" aria-label={`Clear the document filter${documentName ? ': ' + documentName : ''}`}
            onClick={() => change({ document: '', offset: 0, chunk: '' })}><span aria-hidden="true">×</span></button></div>}
        <div className="field"><label htmlFor="chunk-search">Search chunk text</label>
          <input id="chunk-search" type="search" value={input} autoComplete="off" onChange={event => setInput(event.target.value)} placeholder="e.g. grade, enrollment" /></div>

        <div aria-live="polite" className="knowledge-status">
          {chunks.kind === 'loading' && <p className="muted" role="status"><span className="spinner" aria-hidden="true" /> Loading chunks…</p>}
          {chunks.kind === 'error' && <div className="notice error" role="alert"><span><strong>The chunks could not be loaded.</strong> {chunks.message}</span>
            <Button variant="outline" size="sm" onClick={() => setReload(n => n + 1)}>Try again</Button></div>}
          {window_ && <p className="muted">{window_.total ? `Showing ${window_.from} to ${window_.to} of ${window_.total}` : 'No chunks'}{query ? ` matching “${query}”` : ''}</p>}
        </div>
        {window_ && !window_.total && <div className="empty-state"><h2>{query ? 'No chunks match' : 'This source has no chunks'}</h2>
          <p className="muted">{query ? 'Try a different word, or clear the search.' : url.document ? 'No chunks of this document are stored in this source.' : 'Nothing has been built or stored here yet.'}</p>
          {query && <Button variant="outline" onClick={() => { setInput(''); change({ q: '', offset: 0, chunk: '' }); }}>Clear search</Button>}</div>}

        <ul className="chunk-rows">{list.map(chunk => <li key={chunk.chunk_id}>
          <button type="button" className="chunk-row" aria-current={selected?.chunk_id === chunk.chunk_id ? 'true' : undefined} onClick={() => pick(chunk)}>
            <span className="row-meta">{[chunk.document_title, chunk.section].filter(Boolean).join(' · ') || chunk.chunk_id}</span>
            <span className="chunk-snippet">{snippet(chunk)}</span>
            <span className="row-meta">{chunk.pages?.length ? `Page${chunk.pages.length === 1 ? '' : 's'} ${chunk.pages.join(', ')}` : 'No page reference'}</span>
          </button></li>)}</ul>

        {window_ && window_.pages > 1 && <nav className="pager" aria-label="Chunk pages">
          <Button variant="outline" disabled={window_.prev === null} onClick={() => change({ offset: window_.prev ?? 0, chunk: '' })}>Previous</Button>
          <span className="muted">Page {window_.page} of {window_.pages}</span>
          <Button variant="outline" disabled={window_.next === null} onClick={() => change({ offset: window_.next ?? 0, chunk: '' })}>Next</Button>
        </nav>}
      </div>

      <div className="knowledge-main">
        {selected ? <ChunkDetail key={selected.chunk_id} chunk={selected} ref={detailHeading} />
          : <div className="empty-state"><h2>{url.chunk ? 'That chunk is not on this page of results' : 'Select a chunk'}</h2>
            <p className="muted">{url.chunk ? 'The link names a chunk that this page of the list does not contain. Change the page or clear the search.' : 'Its text appears here beside the source page it came from.'}</p></div>}
      </div>
    </div>}
  </main>;
}

const ChunkDetail = forwardRef<HTMLHeadingElement, { chunk: Chunk }>(function ChunkDetail({ chunk }, headingRef) {
  const pages = chunk.pages ?? [];
  const [page, setPage] = useState(pages[0] ?? 0), [count, setCount] = useState(0);
  const [mode, setMode] = useSourceMode();
  const showPdf = mode === 'pdf' && !!chunk.source_sha256;
  return <article className="chunk-detail" aria-labelledby="chunk-title">
    <h2 id="chunk-title" tabIndex={-1} ref={headingRef}>{chunk.section?.trim() || chunk.document_title || 'Chunk'}</h2>
    <dl className="upload-meta chunk-meta">{chunkMeta(chunk).map(([name, value]) =>
      <div key={name} data-field={name.toLowerCase()}><dt>{name}</dt><dd>{value}</dd></div>)}</dl>
    <div className="compare-grid">
      <section className="compare-pane" role="region" aria-label="Chunk text" tabIndex={0}><p className="pane-label">Chunk text</p>
        <p className="chunk-text">{chunkText(chunk)}</p>
        <details className="tech-details"><summary>Technical details</summary>
          <dl className="upload-meta"><div><dt>Tokens</dt><dd>{chunk.token_count ?? 'unknown'}</dd></div><div><dt>Passage id</dt><dd><code>{chunk.reading_id ?? 'none'}</code></dd></div>
            <div><dt>Chunk id</dt><dd><code>{chunk.chunk_id}</code></dd></div></dl>
          {chunk.display_text && <pre className="chunk-text">{chunk.text}</pre>}</details></section>
      <section className={showPdf ? 'compare-pane has-pdf' : 'compare-pane'} role="region" aria-label="Source page" tabIndex={showPdf ? undefined : 0}>
        <div className="pane-label-row"><p className="pane-label">Source page</p>
          {pages.length > 1 && <div className="page-chips" role="group" aria-label="Pages this chunk cites">{pages.map(p =>
            <button key={p} type="button" className="chip" aria-pressed={p === page} onClick={() => setPage(p)}>{p}</button>)}</div>}
          {count > 0 && <span className="muted">of {count}</span>}
          {chunk.source_sha256 && <SourceModeSwitch mode={mode} onChange={setMode}/>}</div>
        {showPdf ? <PdfFrame url={REVIEW_CONNECTION.api + knowledgePdfPath(chunk.source_sha256!)} page={page || 1}
            title={chunk.document_title || 'Source document'}/>
          : chunk.source_sha256 && page > 0 ? <PageImage sha256={chunk.source_sha256} page={page} onCount={setCount} />
          : <div className="page-placeholder"><p><strong>No source page to show.</strong></p>
            <p className="muted">{chunk.source_sha256 ? 'This chunk cites no page.' : 'This chunk has no source PDF hash.'}</p></div>}
      </section>
    </div>
  </article>;
});
