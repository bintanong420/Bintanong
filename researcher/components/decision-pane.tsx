'use client';

import { useId, useState, type Dispatch, type ReactNode, type SetStateAction } from 'react';
import { Button } from '@/components/ui/button';
import { ReviewAudit } from '@/components/review-audit';
import { RelatedRecords } from '@/components/related-records';
import { ReviewedValue } from '@/components/reviewed-value';
import { SourceGaps } from '@/components/source-gaps';
import { SUGGESTED_NOTE, fieldAfterChoice, textOf, type Draft, type FieldDraft } from '@/lib/review-form';
import { fieldLabel, readableValue, recordHeading, recordStatus, type Document, type Field, type ReviewItem } from '@/lib/review-state';

const CHOICES = [['accepted', 'Matches'], ['corrected', 'Fix text'], ['unresolved', 'Unclear']] as const;

function DecisionChoice({ field, value, onChoose }: { field: Field; value: string; onChoose: (value: string) => void }) {
  const name = useId();
  return <div className="rw-choice" role="radiogroup" aria-label={`${fieldLabel(field.name)} decision`}>
    {CHOICES.filter(([choice]) => !(field.source_blank && choice === 'corrected')).map(([choice, label]) => <label key={choice}>
      <input type="radio" name={name} value={choice} checked={value === choice} onChange={() => onChoose(choice)}/><span>{label}</span></label>)}
  </div>;
}

export function DecisionPane({ item, items, documents, draft, setDraft, dirty, busy, notices, onSave, onShowSource, onOpenRecord, packetId, revision }: {
  item: ReviewItem; items: ReviewItem[]; documents: Document[]; draft: Draft; setDraft: Dispatch<SetStateAction<Draft | null>>;
  dirty: boolean; busy: boolean; notices: ReactNode; onSave: () => void; onShowSource: (itemId: string, page: number) => void;
  onOpenRecord: (id: string) => void;
  packetId: string; revision: number;
}) {
  const [showRaw, setShowRaw] = useState(false);
  const document = documents.find(doc => doc.id === item.document_id);
  const editable = !item.reference_only && item.fields.length > 0;
  const ready = draft.reason.trim() !== '';
  const patch = (change: Partial<Draft>) => setDraft(current => current && { ...current, ...change });
  const setField = (name: string, value: FieldDraft) =>
    setDraft(current => current && { ...current, fields: { ...current.fields, [name]: value } });
  const problems = item.source_gaps ?? [];
  const heading = recordHeading(item.title);
  return <section id="source-review" tabIndex={-1} className="decision-pane rw-decision" aria-label="Extraction and review">
    <header className="rw-record-head">
      {heading.context && <p className="rw-record-context" title={item.title}>{heading.context}</p>}
      <h2 title={item.title}>{heading.heading}</h2>
      <div className="review-actions">
        {editable && <label className="rw-audience"><span>Audience</span>
          <select aria-label="Audience applicability" value={draft.audience} disabled={busy} onChange={event => patch({ audience: event.target.value })}>
            <option value="unresolved">Not sure yet</option><option value="undergraduate">Undergraduate</option><option value="excluded">Outside this study</option>
          </select></label>}
        {editable && <Button type="submit" form="review-form" disabled={busy}>{busy ? 'Saving…' : 'Save'}</Button>}
        <p id="review-save-help" role="status">{!editable ? (item.reference_only ? 'Reviewed reference' : recordStatus(item))
          : !ready ? 'Write a short note to save.' : dirty ? 'Unsaved changes' : recordStatus(item)}</p>
      </div>
      {notices}
    </header>
    <div className="rw-body">
      {item.reference_only && <p className="muted">Read-only. Opening it does not record a new approval.</p>}
      {!!item.findings.length && <p className="notice hold">Needs checking: {item.findings.map(fieldLabel).join(', ')}.</p>}
      {!!problems.length && <details className="rw-disclosure known-gaps"><summary>Known source problems ({problems.length})</summary>
        {problems.map((gap, i) => <div key={i}><p><strong>{fieldLabel(gap.issue)}</strong></p>
          <p>Affects: {gap.affected_claims.join('; ')}.</p>
          <p className="source-reading">{Array.isArray(gap.visible_text) ? gap.visible_text.join('\n') : gap.visible_text}</p>
          <p className="muted">Left unresolved. Nothing was filled in.</p></div>)}
      </details>}
      {item.reference_only ? <>{item.fields.map(field => <section className="field-review" key={field.name}>
          <div className="rw-field-head"><h3>{fieldLabel(field.name)}</h3><span className="muted">p. {field.locator.physical_pages.join(', ')}</span></div>
          <p className="source-reading">{field.source_blank ? 'Blank in the original document.' : readableValue(field.original_value)}</p>
        </section>)}
        {!!draft.companions.length && <section aria-label="Related source records"><h3>Read together</h3>
          {draft.companions.map(id => items.find(row => row.id === id)).filter(row => !!row).map(row => <button
            type="button" className="related-record" key={row.id} onClick={() => onOpenRecord(row.id)} title={row.title}>{recordHeading(row.title).heading}</button>)}
        </section>}</>
        : !item.fields.length ? <p className="notice hold">This prospectus uses the course review workflow. Its questions require the prospectus review controls.</p>
        : <form id="review-form" onSubmit={event => { event.preventDefault(); onSave(); }}>
          <fieldset disabled={busy}>
            <legend className="sr-only">Your review</legend>
            {item.fields.map(field => {
              const current = draft.fields[field.name];
              return <section className="field-review rw-field" key={field.name}>
                <div className="rw-field-head"><h3>{fieldLabel(field.name)}</h3>
                  <span className="muted">p. {field.locator.physical_pages.join(', ') || 'not located'}
                    {current.decision !== 'pending' && <button type="button" className="rw-clear"
                      onClick={() => setField(field.name, fieldAfterChoice(field.original_value, current, 'pending'))}>Mark as not checked</button>}</span></div>
                <p className="original-text source-reading rw-original">{readableValue(field.original_value) || '(literal empty extraction)'}</p>
                {field.source_blank && <p className="notice hold">Blank in the source. It stays blank.</p>}
                <DecisionChoice field={field} value={current.decision}
                  onChoose={choice => setField(field.name, fieldAfterChoice(field.original_value, current, choice))}/>
                {current.decision === 'corrected' && <ReviewedValue field={field} value={current.text}
                  onChange={text => setField(field.name, { decision: 'corrected', text })}/>}
                <ReviewAudit key={item.id + ':' + field.name} field={field} item={item} document={document}
                  packetId={packetId} revision={revision} disabled={busy}
                  onUse={value => setField(field.name, { decision: 'corrected', text: textOf(value) })}/>
              </section>;
            })}
            <div className="rw-note"><label>Note
              <input aria-label="Review reason" aria-describedby="review-save-help" type="text" maxLength={8000}
                value={draft.reason} placeholder="What did you check?" onChange={event => patch({ reason: event.target.value })}/></label>
              {!ready && <button type="button" className="rw-chip" onClick={() => patch({ reason: SUGGESTED_NOTE })}>Use: {SUGGESTED_NOTE}</button>}</div>
            <RelatedRecords key={item.id} item={item} items={items} documents={documents} selected={draft.companions}
              onChange={companions => patch({ companions })} onShowSource={onShowSource}/>
            <SourceGaps gaps={draft.gaps} fields={item.fields} onChange={gaps => patch({ gaps })}/>
          </fieldset>
        </form>}
      <details className="rw-disclosure" onToggle={event => setShowRaw(event.currentTarget.open)}><summary>Technical details</summary>
        {showRaw && <pre>{JSON.stringify(item, null, 2)}</pre>}</details>
    </div>
  </section>;
}
