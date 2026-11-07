'use client';

import { useEffect, useRef, useState, type PointerEvent } from 'react';
import { Button } from '@/components/ui/button';
import { request } from '@/lib/api';
import { selectionRegion, sourceRectangle, type Connection, type Document, type FeedbackReceipt, type OmissionFeedback, type Region, type ReviewItem } from '@/lib/review-state';
import { OmissionFeedback as OmissionForm } from '@/components/omission-feedback';

export type HighlightPages = Record<string, { warning?: string | null;
  boxes: { fractions: { left: number; top: number; width: number; height: number } }[] }>;

export function SourceViewer({ connection, item, legacyBoxes, document, relatedItems = [], focus, revision,
  feedback = [], onFeedbackSaved, reviewBusy = false }: {
  connection: Connection; item: ReviewItem; legacyBoxes?: HighlightPages; document?: Document;
  relatedItems?: ReviewItem[]; focus?: { itemId: string; page: number } | null; revision?: number;
  feedback?: OmissionFeedback[]; onFeedbackSaved?: (receipt: FeedbackReceipt) => void; reviewBusy?: boolean;
}) {
  const [page, setPage] = useState(item.fields.flatMap(f => f.locator.physical_pages)[0] ?? 1), [scale, setScale] = useState('1.5');
  const [image, setImage] = useState<string | null>(null), [error, setError] = useState('');
  const [geometry, setGeometry] = useState({ width: 600, height: 800, count: 0, rotation: 0 });
  const [marking, setMarking] = useState(false), [region, setRegion] = useState<Region | null>(null), [reporting, setReporting] = useState(false);
  const dragStart = useRef<[number, number] | null>(null);
  const pageScroll = useRef<HTMLDivElement>(null);
  useEffect(() => { setPage(item.fields.flatMap(f => f.locator.physical_pages)[0] ?? 1); }, [item.id]);
  useEffect(() => { if (focus) setPage(focus.page); }, [focus]);
  useEffect(() => { setRegion(null); setMarking(false); dragStart.current = null; }, [page, item.id]);
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
  const related = geometry.rotation === 0 ? relatedItems.filter(row => row.document_id === item.document_id).flatMap(row =>
    row.fields.flatMap(field => field.spans).filter(span => span.page === page).map(span => ({ readingId: row.id, box: sourceRectangle(span) }))
      .filter(value => value.box !== null)) : [];
  const reports = feedback.filter(row => row.document_id === item.document_id && row.page === page);
  useEffect(() => {
    const scroll = pageScroll.current;
    const target = focus ? [...(scroll?.querySelectorAll('rect[data-reading]') ?? [])].find(rect => rect.getAttribute('data-reading') === focus.itemId)
      : scroll?.querySelector('.current-highlight');
    if (scroll && target) scroll.scrollTop += target.getBoundingClientRect().top - scroll.getBoundingClientRect().top - scroll.clientHeight * .25;
  }, [image, item.id, focus]);
  function point(event: PointerEvent<HTMLDivElement>): [number, number] {
    const box = event.currentTarget.getBoundingClientRect();
    return [(event.clientX - box.left) / box.width, (event.clientY - box.top) / box.height];
  }
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
      : <div className="page-scroll" ref={pageScroll}><div className={marking ? 'pdf-page marking-region' : 'pdf-page'} style={{ aspectRatio: `${geometry.width}/${geometry.height}` }}
        onPointerDown={event => { if (marking && event.button === 0) { event.preventDefault(); event.currentTarget.setPointerCapture(event.pointerId); dragStart.current = point(event); setRegion(null); } }}
        onPointerMove={event => { if (dragStart.current) setRegion(selectionRegion(dragStart.current, point(event))); }}
        onPointerUp={event => { if (dragStart.current) { setRegion(selectionRegion(dragStart.current, point(event))); dragStart.current = null; setMarking(false); } }}
        onPointerCancel={() => { dragStart.current = null; setRegion(null); setMarking(false); }}>
        <img src={image} alt={`Original PDF page ${page}`} draggable={false}/>
        <svg viewBox={`0 0 ${geometry.width} ${geometry.height}`} aria-hidden="true">
          {related.map(({ box, readingId }, i) => <rect className="related-highlight" data-reading={readingId} key={i} {...box!}/>)}
          {highlights.map((r, i) => <rect className="current-highlight" key={i} {...r} />)}
          {region && <rect className="marked-region" x={region[0] * geometry.width} y={region[1] * geometry.height}
            width={(region[2] - region[0]) * geometry.width} height={(region[3] - region[1]) * geometry.height}/>}
        </svg>
      </div></div>}
    <p className="muted source-note">{!image ? 'Source regions appear when the page has loaded.' : legacy?.warning ?? (geometry.rotation !== 0 ? 'Highlights are withheld for this rotated page.'
      : highlights.length || related.length ? 'Regions use recorded source spans. Unmarked text on this page may still be present in the review data.'
      : 'No verified highlight is available for this page. Inspect the original; geometry remains unresolved.')}</p>
    {!!(highlights.length || related.length) && <div className="source-legend"><span><i className="legend-current"/>Current record</span>
      {!!related.length && <span><i className="legend-related"/>Related context</span>}</div>}
    {onFeedbackSaved && revision !== undefined && <section className="feedback-tools" aria-label="Missing content feedback">
      <p className="muted">Something missing from the extracted records or answer? Mark its area, or report the whole page.</p>
      <div className="feedback-actions"><Button type="button" variant="outline" disabled={!image || reviewBusy} aria-pressed={marking}
        onClick={() => setMarking(!marking)}>{marking ? 'Cancel marking' : 'Mark the missed area'}</Button>
        {region && <Button type="button" variant="outline" onClick={() => setRegion(null)}>Clear marked area</Button>}
        <Button type="button" disabled={!image || reviewBusy} onClick={() => setReporting(true)}>Report missing content</Button></div>
      {marking && <p role="status">Drag over the missing content. You can also cancel marking and report the whole page.</p>}
      {reporting && <OmissionForm connection={connection} documentId={item.document_id} documentTitle={document?.title ?? 'Original PDF'}
        page={page} region={region} revision={revision} onClose={() => setReporting(false)} onSaved={receipt => { onFeedbackSaved(receipt); setRegion(null); }}/>}
      {!!reports.length && <details><summary>Missing-content notes on this page ({reports.length})</summary>{reports.map(report => <article className="feedback-note" key={report.operation_id}>
        <p className="muted">Pending review · {report.reviewer}</p><blockquote>{report.visible_text}</blockquote><p>{report.note}</p>
      </article>)}</details>}
    </section>}
  </section>;
}
