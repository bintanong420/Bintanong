'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { fieldLabel, filterItems, readableValue, type Document, type ReviewItem } from '@/lib/review-state';

export function RelatedRecords({ item, items, documents, selected, onChange, onShowSource }: {
  item: ReviewItem; items: ReviewItem[]; documents: Document[]; selected: string[];
  onChange: (ids: string[]) => void; onShowSource: (itemId: string, page: number) => void;
}) {
  const [query, setQuery] = useState('');
  const choices = filterItems(items.filter(row => row.id !== item.id), '', query, 'all');
  const chosen = selected.map(id => items.find(row => row.id === id)).filter(row => !!row);
  function pages(row: ReviewItem) { return [...new Set(row.fields.flatMap(field => field.locator.physical_pages))].sort((a, b) => a - b); }
  return <section className="related-records" aria-label="Related records">
    <div className="pane-heading"><h3>Related records</h3><span>{selected.length} selected</span></div>
    <p className="muted">Keep the steps, conditions or tables needed to understand this record together. Their source regions appear as dashed outlines on the PDF.</p>
    {!chosen.length && <p className="muted">No related records selected. Add one below when this record needs more context.</p>}
    {chosen.map(row => <article className="companion" key={row.id}>
      <div className="companion-heading"><h4>{row.title}</h4><Button type="button" variant="outline" size="sm"
        aria-label={`Remove related record: ${row.title}`} onClick={() => onChange(selected.filter(id => id !== row.id))}>Remove</Button></div>
      <p className="muted">{documents.find(doc => doc.id === row.document_id)?.title} · PDF pages {pages(row).join(', ')}</p>
      {row.document_id === item.document_id && <div className="context-pages">{pages(row).map(page => <Button key={page} type="button" variant="outline" size="sm"
        onClick={() => onShowSource(row.id, page)}>Show page {page}</Button>)}</div>}
      <details><summary>Read the related fields</summary><dl className="related-fields">{row.fields.map(field => <div key={field.name}>
        <dt>{fieldLabel(field.name)}</dt><dd>{readableValue(field.reviewed_value)}</dd>
      </div>)}</dl></details>
    </article>)}
    <details className="record-picker"><summary>Add or change related records</summary>
      <label>Find a related record<input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Search a topic or phrase"/></label>
      <div className="record-choices" role="group" aria-label="Available related records">{choices.map(row => <label className="record-choice" key={row.id}>
        <input type="checkbox" checked={selected.includes(row.id)} onChange={e => onChange(e.target.checked ? [...selected, row.id] : selected.filter(id => id !== row.id))}/>
        <span><strong>{row.title}</strong><span className="muted">{documents.find(doc => doc.id === row.document_id)?.title} · PDF pages {pages(row).join(', ')}</span></span>
      </label>)}</div>
      {!choices.length && <p className="muted">No related records match. Try another phrase; your selected records stay above.</p>}
    </details>
  </section>;
}
