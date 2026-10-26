'use client';

import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { request } from '@/lib/api';
import { sourceRectangle, type Connection, type Document, type ReviewItem } from '@/lib/review-state';

export type HighlightPages = Record<string, { warning?: string | null;
  boxes: { fractions: { left: number; top: number; width: number; height: number } }[] }>;

export function SourceViewer({ connection, item, legacyBoxes, document }: {
  connection: Connection; item: ReviewItem; legacyBoxes?: HighlightPages; document?: Document;
}) {
  const [page, setPage] = useState(1), [scale, setScale] = useState('1.5');
  const [image, setImage] = useState<string | null>(null), [error, setError] = useState('');
  const [geometry, setGeometry] = useState({ width: 600, height: 800, count: 0, rotation: 0 });
  const pageScroll = useRef<HTMLDivElement>(null);
  useEffect(() => { setPage(item.fields.flatMap(f => f.locator.physical_pages)[0] ?? 1); }, [item.id]);
  useEffect(() => {
    let current = true, objectUrl = '';
    setImage(null); setError('');
    request(connection, `/api/page/${encodeURIComponent(item.document_id)}/${page}?scale=${scale}`)
      .then(async response => {
        const blob = await response.blob();
        if (!current) return;
        objectUrl = URL.createObjectURL(blob); setImage(objectUrl);
        setGeometry({ width: Number(response.headers.get('x-page-width')), height: Number(response.headers.get('x-page-height')),
          count: Number(response.headers.get('x-page-count')), rotation: Number(response.headers.get('x-page-rotation')) });
      }).catch(error => { if (current) setError(error.message); });
    return () => { current = false; if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [connection, item.document_id, page, scale]);
  const spans = item.fields.flatMap(f => f.spans).filter(span => span.page === page);
  const legacy = legacyBoxes?.[String(page)];
  const highlights = legacyBoxes ? (legacy?.warning ? [] : (legacy?.boxes ?? []).map(({ fractions: f }) => ({
    x: f.left * geometry.width, y: f.top * geometry.height,
    width: f.width * geometry.width, height: f.height * geometry.height,
  }))) : geometry.rotation === 0 ? spans.map(sourceRectangle).filter(r => r !== null) : [];
  useEffect(() => {
    const scroll = pageScroll.current, region = scroll?.querySelector('rect');
    if (scroll && region) scroll.scrollTop += region.getBoundingClientRect().top - scroll.getBoundingClientRect().top - scroll.clientHeight * .25;
  }, [image, item.id]);
  return <section className="source-pane" aria-label="Original source">
    {document && <div className="source-heading"><h2>{document.title}</h2><p className="muted">{document.edition}</p></div>}
    <div className="pane-heading"><h2>Original PDF</h2><span>Page {page} of {geometry.count || '?'}</span></div>
    <div className="page-controls">
      <Button variant="outline" size="sm" disabled={!image || page <= 1} onClick={() => setPage(p => p - 1)}>Previous page</Button>
      <label>Page<input aria-label="PDF page" type="number" min="1" max={geometry.count || 1000} value={page}
        onChange={event => { const n = Number(event.target.value); if (Number.isInteger(n) && n > 0 && n <= (geometry.count || 1000)) setPage(n); }}/></label>
      <Button variant="outline" size="sm" disabled={!image || page >= geometry.count} onClick={() => setPage(p => p + 1)}>Next page</Button>
      <label>Quality<select value={scale} onChange={event => setScale(event.target.value)}>
        <option value="1">100%</option><option value="1.5">150%</option><option value="2">200%</option><option value="3">300%</option>
      </select></label>
    </div>
    {error ? <p role="alert" className="notice error">The original page could not be displayed. {error} Keep affected content on hold.</p>
      : !image ? <p role="status" className="empty">Loading original page…</p>
      : <div className="page-scroll" ref={pageScroll}><div className="pdf-page" style={{ aspectRatio: `${geometry.width}/${geometry.height}` }}>
        <img src={image} alt={`Original PDF page ${page}`} />
        <svg viewBox={`0 0 ${geometry.width} ${geometry.height}`} aria-hidden="true">
          {highlights.map((r, i) => <rect key={i} {...r} />)}
        </svg>
      </div></div>}
    <p className="muted source-note">{!image ? 'Source regions appear when the page has loaded.' : legacy?.warning ?? (geometry.rotation !== 0 ? 'Highlights are withheld for this rotated page.'
      : highlights.length ? 'Highlighted regions belong to this item’s recorded source spans.'
      : 'No verified highlight is available for this page. Inspect the original; geometry remains unresolved.')}</p>
  </section>;
}
