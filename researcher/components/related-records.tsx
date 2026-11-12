'use client';

import { useMemo, useState } from 'react';
import { Button } from '@/components/ui/button';
import { fieldLabel, filterItems, readableValue, recordHeading, type Document, type ReviewItem } from '@/lib/review-state';

const SHOWN = 50;  // the picker lists matches only after it is opened, and never more than this many at once

export function RelatedRecords({ item, items, documents, selected, onChange, onShowSource }: {
  item: ReviewItem; items: ReviewItem[]; documents: Document[]; selected: string[];
  onChange: (ids: string[]) => void; onShowSource: (itemId: string, page: number) => void;
}) {
  const [query, setQuery] = useState(''), [picking, setPicking] = useState(false);
  const matches = useMemo(() => picking ? filterItems(items.filter(row => row.id !== item.id), '', query, 'all') : [], [picking, items, item.id, query]);
  const chosen = selected.map(id => items.find(row => row.id === id)).filter(row => !!row);
  function pages(row: ReviewItem) { return [...new Set(row.fields.flatMap(field => field.locator.physical_pages))].sort((a, b) => a - b); }
  return <details className="rw-disclosure" aria-label="Related records"><summary>Related records ({selected.length})</summary>
    <p className="muted">Steps or tables needed to read this record. They are outlined with dashes on the PDF.</p>
    {chosen.map(row => <article className="companion" key={row.id}>
      <div className="companion-heading"><h4 title={row.title}>{recordHeading(row.title).heading}</h4><Button type="button" variant="outline" size="sm"
        aria-label={`Remove related record: ${row.title}`} onClick={() => onChange(selected.filter(id => id !== row.id))}>Remove</Button></div>
      <p className="muted">{documents.find(doc => doc.id === row.document_id)?.title} · p. {pages(row).join(', ')}</p>
      {row.document_id === item.document_id && <div className="context-pages">{pages(row).map(page => <Button key={page} type="button" variant="outline" size="sm"
        onClick={() => onShowSource(row.id, page)}>Show page {page}</Button>)}</div>}
      <details><summary>Read the related fields</summary><dl className="related-fields">{row.fields.map(field => <div key={field.name}>
        <dt>{fieldLabel(field.name)}</dt><dd>{readableValue(field.reviewed_value)}</dd>
      </div>)}</dl></details>
    </article>)}
    <details className="record-picker" onToggle={event => setPicking(event.currentTarget.open)}><summary>Add or remove records</summary>
      <label>Find a record<input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Topic or phrase"/></label>
      <div className="record-choices" role="group" aria-label="Available related records">{matches.slice(0, SHOWN).map(row => <label className="record-choice" key={row.id}>
        <input type="checkbox" checked={selected.includes(row.id)} onChange={e => onChange(e.target.checked ? [...selected, row.id] : selected.filter(id => id !== row.id))}/>
        <span><strong title={row.title}>{recordHeading(row.title).heading}</strong><span className="muted">{documents.find(doc => doc.id === row.document_id)?.title} · p. {pages(row).join(', ')}</span></span>
      </label>)}</div>
      {matches.length > SHOWN && <p className="muted">Showing {SHOWN} of {matches.length}. Search to narrow.</p>}
      {picking && !matches.length && <p className="muted">No records match.</p>}
    </details>
  </details>;
}
