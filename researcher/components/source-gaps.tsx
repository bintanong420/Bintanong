'use client';

import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { fieldLabel, type Field, type Gap } from '@/lib/review-state';

export function SourceGaps({ gaps, fields, onChange }: { gaps: Gap[]; fields: Field[]; onChange: (gaps: Gap[]) => void }) {
  function update(index: number, patch: Partial<Gap>) {
    onChange(gaps.map((gap, i) => i === index ? { ...gap, ...patch } : gap));
  }
  return <details><summary>Report a problem in the document</summary>
    <p className="muted">Use this when the original is cut off, unclear or contradictory. Keep the visible wording unchanged.</p>
    {gaps.map((gap, i) => <section className="gap-editor" key={i}>
      <label>What is the problem?<Textarea required value={gap.issue} onChange={e => update(i, { issue: e.target.value })}/></label>
      <fieldset><legend>Which fields does it affect?</legend>{fields.map(field => <label className="checkbox-label" key={field.name}>
        <input type="checkbox" checked={gap.field_names.includes(field.name)} onChange={e => update(i, {
          field_names: e.target.checked ? [...gap.field_names, field.name] : gap.field_names.filter(n => n !== field.name),
        })}/>{fieldLabel(field.name)}</label>)}</fieldset>
      <label>What can you read in the original?<Textarea value={gap.visible_text} onChange={e => update(i, { visible_text: e.target.value })}/></label>
      <label>What can we no longer answer? (one point per line)<Textarea required value={gap.affected_claims.join('\n')}
        onChange={e => update(i, { affected_claims: e.target.value.split('\n') })}/></label>
      <Button type="button" variant="outline" onClick={() => onChange(gaps.filter((_, index) => index !== i))}>Remove this problem</Button>
    </section>)}
    <Button type="button" variant="outline" onClick={() => onChange([...gaps, { issue: '', field_names: [], visible_text: '', affected_claims: [] }])}>
      Add a source problem</Button>
  </details>;
}
