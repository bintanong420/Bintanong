'use client';

import { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { AdvisorySuggestion } from '@/components/advisory-suggestion';
import { request } from '@/lib/api';
import { REVIEW_CONNECTION, type Document, type Field, type ReviewItem } from '@/lib/review-state';

export function ReviewAudit({ field, item, document, packetId, revision, disabled, onUse }: {
  field: Field; item: ReviewItem; document?: Document; packetId: string; revision: number;
  disabled: boolean; onUse: (value: unknown) => void;
}) {
  const [busy, setBusy] = useState(false), [error, setError] = useState('');
  const [audited, setAudited] = useState<{ field: Field; revision: number } | null>(null);
  const active = useRef(false), currentRevision = useRef(revision);
  currentRevision.current = revision;
  async function audit() {
    if (active.current || disabled) return;
    active.current = true; setBusy(true); setError('');
    try {
      const response = await (await request(REVIEW_CONNECTION, '/api/audit', { method: 'POST', body: JSON.stringify({
        packet_id: packetId, revision, item_id: item.id, field: field.name,
      }) })).json();
      if (response.packet_id !== packetId || response.item_id !== item.id || response.revision !== currentRevision.current
          || response.field?.name !== field.name) throw Error('The review changed. Run the audit again on the current field.');
      setAudited({ field: response.field, revision: response.revision });
    } catch (failure) { setError(failure instanceof Error ? failure.message : 'Gemma audit unavailable. Review the source manually.'); }
    finally { active.current = false; setBusy(false); }
  }
  const selected = audited?.revision === revision ? audited.field : field;
  return <div className="rw-audit" aria-label="Gemma vision audit">
    <div className="rw-audit-row"><Button type="button" variant="outline" size="sm"
      disabled={busy || disabled || field.source_blank || !field.locator.physical_pages.length}
      onClick={() => void audit()}>{busy ? 'Auditing with Gemma…' : 'Audit with Gemma'}</Button>
    <p className="hint" role="status">{busy ? 'Comparing this extraction with its source page. You can continue editing.'
      : audited?.revision === revision ? 'Gemma audit ready. It has not changed your review.'
      : 'Optional local vision check. You decide whether to use its suggestion.'}</p></div>
    {error && <p className="field-error" role="alert">{error}</p>}
    <AdvisorySuggestion key={JSON.stringify(selected.assistance ?? null)} field={selected} item={item} document={document} onUse={onUse}/>
  </div>;
}
