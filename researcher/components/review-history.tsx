'use client';

import { useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { fieldLabel, type ReviewItem } from '@/lib/review-state';

export type HistoryEntry = { reviewer: string; recorded_at: string; item_id: string; reason: string;
  fields: Record<string, { decision: string; value: unknown }> };

export function ReviewHistory({ entries, items, onClose }: { entries: HistoryEntry[]; items: ReviewItem[]; onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => { dialog.current?.showModal(); }, []);
  return <dialog ref={dialog} className="history-panel" aria-labelledby="history-title" onClose={onClose}>
    <div className="pane-heading"><h2 id="history-title">Saved reviews</h2><Button variant="outline" onClick={() => dialog.current?.close()}>Close</Button></div>
    {!entries.length ? <p>No local reviews have been saved. Opening a reference does not create a review.</p>
      : entries.map((entry, i) => <section className="history-entry" key={i}>
        <h3>{items.find(item => item.id === entry.item_id)?.title ?? 'Source record'}</h3>
        <p className="muted">{entry.reviewer} · {new Date(entry.recorded_at).toLocaleString()}</p>
        <p>{entry.reason}</p><ul>{Object.entries(entry.fields).map(([name, field]) => <li key={name}>
          {fieldLabel(name)}: {field.decision === 'accepted' ? 'Matches the document' : field.decision === 'corrected' ? 'Text corrected'
            : field.decision === 'unresolved' ? 'Needs clarification' : 'Not checked'}
        </li>)}</ul>
        <details><summary>Technical details</summary><pre>{JSON.stringify(entry, null, 2)}</pre></details>
      </section>)}
  </dialog>;
}
