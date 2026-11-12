'use client';

import { memo, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, type KeyboardEvent } from 'react';
import { revealScrollTop, stepIndex, windowRange } from '@/lib/review-form';
import { filterItems, itemSnippet, recordStatus, type Document, type ReviewItem } from '@/lib/review-state';

const ROW = 76;  // px; rows have a fixed height so only the visible ones need to exist

function pagesOf(row: ReviewItem) { return [...new Set(row.fields.flatMap(f => f.locator.physical_pages))].join(', '); }

const Row = memo(function Row({ row, index, doc, current, tabStop, onChoose }: {
  row: ReviewItem; index: number; doc: string; current: boolean; tabStop: boolean; onChoose: (id: string) => void;
}) {
  const snippet = itemSnippet(row);
  const problem = row.findings.length > 0 || !!row.source_gaps?.length;
  return <button type="button" className="queue-item rl-row" data-index={index} style={{ top: index * ROW }}
    title={`${row.title} · ${doc}`} aria-current={current ? 'true' : undefined} tabIndex={tabStop ? 0 : -1} onClick={() => onChoose(row.id)}>
    <strong>{row.title}</strong>
    {snippet && <span className="queue-snippet">{snippet}</span>}
    <span className={problem ? 'status hold' : 'status'}>p. {pagesOf(row)} · {recordStatus(row)}</span>
  </button>;
});

// Left column: search, filters and the record list. Owns its own filter state so typing never re-renders the review form.
export const RecordList = memo(function RecordList({ items, documents, selected, onChoose }: {
  items: ReviewItem[]; documents: Document[]; selected: string; onChoose: (id: string) => void;
}) {
  const [input, setInput] = useState(''), [query, setQuery] = useState('');
  const [documentFilter, setDocumentFilter] = useState(''), [mode, setMode] = useState('all');
  const [open, setOpen] = useState(false);
  const [scrollTop, setScrollTop] = useState(0), [viewport, setViewport] = useState(600);
  const scroller = useRef<HTMLDivElement>(null), frame = useRef(0), focusIndex = useRef<number | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => setQuery(input), 150);
    return () => clearTimeout(timer);
  }, [input]);
  const filtered = useMemo(() => filterItems(items, documentFilter, query, mode), [items, documentFilter, query, mode]);
  const docTitle = useMemo(() => new Map(documents.map(doc => [doc.id, doc.title])), [documents]);
  const selectedRow = items.find(row => row.id === selected);
  const { start, end } = windowRange(scrollTop, viewport, ROW, filtered.length);
  const selectedIndex = filtered.findIndex(row => row.id === selected);
  const tabStopIndex = selectedIndex >= start && selectedIndex < end ? selectedIndex : start;

  useLayoutEffect(() => {
    const el = scroller.current;
    if (!el) return;
    const measure = () => setViewport(el.clientHeight || 600);
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, [open]);
  const scrollTo = useCallback((value: number) => {
    const el = scroller.current;
    if (!el) return;
    el.scrollTop = value; setScrollTop(el.scrollTop);
  }, []);
  // keep the open record in view when it changes (link, back/forward) or the filter reorders the list
  useLayoutEffect(() => {
    const el = scroller.current;
    if (el && selectedIndex >= 0) scrollTo(revealScrollTop(el.scrollTop, el.clientHeight, selectedIndex, ROW));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected, filtered, scrollTo]);
  useEffect(() => {
    if (focusIndex.current === null) return;
    scroller.current?.querySelector<HTMLElement>(`[data-index="${focusIndex.current}"]`)?.focus();
    focusIndex.current = null;
  });
  useEffect(() => () => cancelAnimationFrame(frame.current), []);

  function onScroll() {
    cancelAnimationFrame(frame.current);
    frame.current = requestAnimationFrame(() => { if (scroller.current) setScrollTop(scroller.current.scrollTop); });
  }
  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const current = Number((event.target as HTMLElement).closest<HTMLElement>('[data-index]')?.dataset.index ?? -1);
    let next = -2;
    if (event.key === 'ArrowDown') next = stepIndex(current, 1, filtered.length);
    else if (event.key === 'ArrowUp') next = stepIndex(current, -1, filtered.length);
    else if (event.key === 'Home') next = filtered.length ? 0 : -1;
    else if (event.key === 'End') next = filtered.length - 1;
    if (next === -2 || next < 0) return;
    event.preventDefault();
    const el = scroller.current!;
    focusIndex.current = next;
    scrollTo(revealScrollTop(el.scrollTop, el.clientHeight, next, ROW));
  }
  const choose = useCallback((id: string) => { onChoose(id); setOpen(false); }, [onChoose]);

  return <aside className={open ? 'rw-list is-open' : 'rw-list'} aria-label="Review queue">
    <button type="button" className="rl-toggle" aria-expanded={open} aria-controls="rl-body" onClick={() => setOpen(!open)}>
      <span><strong>Records</strong> <span className="muted">{filtered.length} of {items.length}</span></span>
      <span className="rl-current">{selectedRow?.title ?? 'Choose a record'}</span><i className="chevron" aria-hidden="true"/>
    </button>
    <div className="rl-body" id="rl-body">
      <div className="rl-filters">
        <input type="search" aria-label="Find a record by topic or phrase" placeholder="Search topic or phrase" value={input}
          onChange={event => setInput(event.target.value)} autoComplete="off" spellCheck={false}/>
        <select aria-label="Document" value={documentFilter} onChange={event => setDocumentFilter(event.target.value)}>
          <option value="">All documents</option>{documents.map(doc => <option key={doc.id} value={doc.id}>{doc.title} · {doc.edition}</option>)}
        </select>
        <select aria-label="Show" value={mode} onChange={event => setMode(event.target.value)}>
          <option value="all">All items</option><option value="attention">Needs attention</option>
          <option value="pending">Not fully checked</option><option value="held">Needs clarification</option>
          <option value="reviewed">Fields and audience checked</option><option value="excluded">Outside this study</option>
          <option value="source-problems">Known source problems</option>
        </select>
      </div>
      <div className="rl-scroll" ref={scroller} onScroll={onScroll} onKeyDown={onKeyDown} role="group" aria-label="Source items">
        <div className="rl-space" style={{ height: filtered.length * ROW }}>
          {filtered.slice(start, end).map((row, i) => <Row key={row.id} row={row} index={start + i} doc={docTitle.get(row.document_id) ?? ''}
            current={row.id === selected} tabStop={start + i === tabStopIndex} onChoose={choose}/>)}
        </div>
      </div>
      {!filtered.length && <p className="muted rl-empty">No records match. <button type="button" className="rl-clear"
        onClick={() => { setInput(''); setQuery(''); setDocumentFilter(''); setMode('all'); }}>Clear filters</button></p>}
    </div>
  </aside>;
});
