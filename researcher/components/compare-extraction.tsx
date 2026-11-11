'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { PageImage } from '@/components/page-image';
import { Button } from '@/components/ui/button';
import { request } from '@/lib/api';
import { clampPage, entriesOf, pagesOf, type CompareItem } from '@/lib/compare';
import { REVIEW_CONNECTION } from '@/lib/review-state';

type Loaded = { kind: 'loading' } | { kind: 'error'; message: string } | { kind: 'ready'; items: CompareItem[] };

// Left: the source page. Right: what was extracted from it. Choosing an extracted field jumps to its page.
export function CompareExtraction({ uploadId, sha256, title, onClose }: { uploadId: string; sha256?: string; title: string; onClose: () => void }) {
  const [data, setData] = useState<Loaded>({ kind: 'loading' });
  const [page, setPage] = useState(1), [count, setCount] = useState(0), [scope, setScope] = useState<'page' | 'all'>('page');
  const [picked, setPicked] = useState(''), [pageDraft, setPageDraft] = useState('1');
  const heading = useRef<HTMLHeadingElement>(null);

  const load = useCallback(async () => {
    setData({ kind: 'loading' });
    try {
      const body = await (await request(REVIEW_CONNECTION, `/api/intake/packet/${encodeURIComponent(uploadId)}/items`)).json();
      const items: CompareItem[] = Array.isArray(body) ? body : body.items ?? [];
      setData({ kind: 'ready', items });
      setPage(pagesOf(items)[0] ?? 1);
    } catch (failure) { setData({ kind: 'error', message: failure instanceof Error ? failure.message : 'The extracted items could not be loaded.' }); }
  }, [uploadId]);
  useEffect(() => { void load(); }, [load]);
  useEffect(() => { heading.current?.focus(); }, [uploadId]);
  useEffect(() => { setPageDraft(String(page)); }, [page]);

  const items = data.kind === 'ready' ? data.items : [];
  const entries = useMemo(() => entriesOf(items), [items]);
  const pages = useMemo(() => pagesOf(items), [items]);
  const shown = scope === 'all' ? entries : entries.filter(entry => entry.pages.includes(page));
  const go = (next: number) => setPage(clampPage(next, count));
  const keyOf = (entry: (typeof entries)[number], index: number) => `${entry.itemId}:${entry.fieldName}:${index}`;

  return <section className="compare" aria-labelledby="compare-heading">
    <div className="compare-head">
      <div><h2 id="compare-heading" tabIndex={-1} ref={heading}>Compare extraction</h2>
        <p className="muted">{title}. Source page on the left, extracted text on the right.</p></div>
      <Button variant="outline" onClick={onClose}>Close comparison</Button>
    </div>

    {!sha256 && <p className="notice hold" role="status"><span>The upload list did not include this file’s hash, so the source page cannot be fetched.
      The extracted text is still shown.</span></p>}
    {data.kind === 'loading' && <div role="status" aria-busy="true"><p className="muted"><span className="spinner" aria-hidden="true" /> Loading extracted text…</p></div>}
    {data.kind === 'error' && <div className="notice error" role="alert"><span><strong>The extracted items could not be loaded.</strong> {data.message}</span>
      <Button variant="outline" size="sm" onClick={() => void load()}>Try again</Button></div>}
    {data.kind === 'ready' && !entries.length && <div className="empty-state"><h3>Nothing to compare yet</h3>
      <p className="muted">This packet has no extracted fields that cite a source page.</p></div>}

    {data.kind === 'ready' && !!entries.length && <>
      <div className="compare-controls">
        <Button variant="outline" onClick={() => go(page - 1)} disabled={page <= 1}>Previous page</Button>
        <form className="page-jump" onSubmit={event => { event.preventDefault(); go(Number(pageDraft)); }}>
          <label>Page<input inputMode="numeric" value={pageDraft} onChange={event => setPageDraft(event.target.value)} aria-describedby="compare-count" /></label>
          <span id="compare-count" className="muted">{count ? `of ${count}` : ''}</span>
          <Button type="submit" variant="outline">Go</Button>
        </form>
        <Button variant="outline" onClick={() => go(page + 1)} disabled={count > 0 && page >= count}>Next page</Button>
        <fieldset className="scope-toggle"><legend className="sr-only">Which extracted text to list</legend>
          <label className="inline"><input type="radio" name="compare-scope" checked={scope === 'page'} onChange={() => setScope('page')} />This page</label>
          <label className="inline"><input type="radio" name="compare-scope" checked={scope === 'all'} onChange={() => setScope('all')} />All pages</label>
        </fieldset>
      </div>
      <p className="muted" aria-live="polite">Page {page}: {entries.filter(entry => entry.pages.includes(page)).length} extracted
        {' '}{entries.filter(entry => entry.pages.includes(page)).length === 1 ? 'field' : 'fields'}. Pages with extracted text: {pages.join(', ')}.</p>

      <div className="compare-grid">
        <div className="compare-pane" aria-label={`Source page ${page}`} role="region" tabIndex={0}>
          {sha256 ? <PageImage sha256={sha256} page={page} onCount={setCount} />
            : <div className="page-placeholder"><p className="muted">Source page unavailable.</p></div>}
        </div>
        <div className="compare-pane" aria-label="Extracted text" role="region" tabIndex={0}>
          {!shown.length && <p className="muted">No extracted text cites page {page}. Choose another page{scope === 'page' ? ' or switch to All pages' : ''}.</p>}
          <ul className="entry-list">{shown.map((entry, index) => {
            const key = keyOf(entry, index), active = picked === key;
            return <li key={key}><button type="button" className="entry" aria-pressed={active}
              onClick={() => { setPicked(key); if (!entry.pages.includes(page)) go(entry.pages[0]); }}>
              <span className="entry-head"><strong>{entry.itemTitle}</strong><span className="muted">{entry.fieldName.replaceAll('_', ' ')} · page{entry.pages.length === 1 ? '' : 's'} {entry.pages.join(', ')}</span></span>
              <span className="entry-text">{entry.text || '(empty extraction)'}</span></button></li>;
          })}</ul>
        </div>
      </div>
    </>}
  </section>;
}
