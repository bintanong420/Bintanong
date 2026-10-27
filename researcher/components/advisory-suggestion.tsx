'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { proposalState, readableValue, type Document, type Field, type ReviewItem } from '@/lib/review-state';

export function AdvisorySuggestion({ field, item, document, onUse }: {
  field: Field; item: ReviewItem; document?: Document; onUse: (value: unknown) => void;
}) {
  const [ignored, setIgnored] = useState(false);
  const state = proposalState(field, item, document);
  if (!state || ignored) return null;
  return <section className="companion ai-suggestion" aria-label="AI suggestion">
    <h4>AI suggestion · needs your review</h4>
    <p className="muted">{field.assistance?.provider} · {field.assistance?.model}</p>
    {state === 'stale' ? <p role="alert">This suggestion belongs to different source content. Reopen the current packet before using assistance.</p>
      : <><p>{field.assistance?.rationale || 'Compare this with the original before deciding.'}</p>
        {state === 'proposal' && <><p className="original-text">{readableValue(field.proposed_value)}</p>
          <Button type="button" variant="outline" onClick={() => onUse(field.proposed_value)}>Use suggestion</Button>
          <p className="muted">Copies into your correction. Edit it if needed, then save your review.</p></>}
        {state === 'no_change' && <p>The model suggested no change. The field still needs your review.</p>}
      </>}
    <Button type="button" variant="ghost" onClick={() => setIgnored(true)}>Ignore suggestion</Button>
  </section>;
}
