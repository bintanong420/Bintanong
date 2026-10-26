'use client';

import { Textarea } from '@/components/ui/textarea';
import type { Field } from '@/lib/review-state';

export function ReviewedValue({ field, value, onChange }: { field: Field; value: string; onChange: (value: string) => void }) {
  if (field.field_kind !== 'arrows' || !field.node_reading_ids) return <label>Text after your review
    <Textarea aria-label={`${field.name} reviewed value`} rows={4} value={value} readOnly={field.source_blank}
      onChange={event => onChange(event.target.value)}/>
  </label>;
  const edges: { from: string; label: string; to: string }[] = JSON.parse(value);
  const nodes = Object.keys(field.node_reading_ids);
  function update(index: number, key: 'from' | 'label' | 'to', text: string) {
    onChange(JSON.stringify(edges.map((edge, i) => i === index ? { ...edge, [key]: text } : edge)));
  }
  return <div><p>Connections after your review</p>{edges.map((edge, index) => <fieldset className="field-review" key={index}>
    <legend>Connection {index + 1}</legend>
    <label>From<select aria-label={`Connection ${index + 1} from`} value={edge.from} onChange={e => update(index, 'from', e.target.value)}>
      {nodes.map(node => <option key={node} value={node}>{node.replace('row-', 'Step ')}</option>)}
    </select></label>
    <label>Branch label<input aria-label={`Connection ${index + 1} label`} value={edge.label} onChange={e => update(index, 'label', e.target.value)}/></label>
    <label>To<select aria-label={`Connection ${index + 1} to`} value={edge.to} onChange={e => update(index, 'to', e.target.value)}>
      {[...nodes, 'END'].map(node => <option key={node} value={node}>{node === 'END' ? 'End' : node.replace('row-', 'Step ')}</option>)}
    </select></label>
  </fieldset>)}</div>;
}
