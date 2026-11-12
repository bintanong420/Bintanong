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
  return <details className="rw-disclosure ai-suggestion" aria-label="AI suggestion" open><summary>AI suggestion</summary>
    <p className="muted">{field.assistance?.provider} · {field.assistance?.model}. Check it against the source page.</p>
    {state === 'stale' ? <p role="alert">This suggestion belongs to different source content. Reopen the current packet first.</p>
      : <><p>{field.assistance?.rationale || 'Compare this with the original before deciding.'}</p>
        {state === 'proposal' && <><p className="original-text source-reading">{readableValue(field.proposed_value)}</p>
          <div className="feedback-actions"><Button type="button" variant="outline" onClick={() => onUse(field.proposed_value)}>Use as my correction</Button>
            <Button type="button" variant="ghost" onClick={() => setIgnored(true)}>Ignore</Button></div></>}
        {state === 'no_change' && <p>The model suggested no change. The field still needs your review.</p>}
      </>}
    {state !== 'proposal' && <Button type="button" variant="ghost" onClick={() => setIgnored(true)}>Ignore</Button>}
  </details>;
}
