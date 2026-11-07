export type SourceSpan = {
  page?: number; bbox?: number[] | null; bbox_origin?: string | null;
  page_size?: number[] | null; text?: string;
};
export type Field = {
  name: string; original_value: unknown; reviewed_value: unknown; decision: string;
  source_blank: boolean; locator: { physical_pages: number[]; field: string }; spans: SourceSpan[];
  field_kind?: string; node_reading_ids?: Record<string, string>;
  proposed_value?: unknown;
  assistance?: { outcome: 'proposal' | 'no_change' | 'uncertain' | 'failed'; rationale?: string;
    provider: string; model: string; binding: { source_sha256: string; item_id: string;
      field: string; pages: number[]; original_value: unknown } };
};

export function proposalState(field: Field, item: Pick<ReviewItem, 'id'>, document?: Pick<Document, 'sha256'>) {
  const advice = field.assistance;
  if (!advice) return null;
  const b = advice.binding;
  if (!b || b.source_sha256 !== document?.sha256 || b.item_id !== item.id || b.field !== field.name
    || JSON.stringify(b.pages) !== JSON.stringify(field.locator.physical_pages)
    || JSON.stringify(b.original_value) !== JSON.stringify(field.original_value)) return 'stale';
  return advice.outcome;
}
export type ReviewItem = {
  id: string; document_id: string; title: string; audience: string; findings: string[];
  fields: Field[]; companions: string[]; reason?: string; gaps?: Gap[];
  prospectus_candidate?: unknown;
  reference_only?: boolean; source_gaps?: SourceGap[];
};
export type Gap = { issue: string; field_names: string[]; visible_text: string; affected_claims: string[] };
export type SourceGap = Omit<Gap, 'visible_text'> & { visible_text: string | string[]; message?: string };
export type Document = { id: string; kind: string; title: string; edition: string; sha256: string };
export type ReviewState = {
  packet_id: string; revision: number; documents: Document[]; items: ReviewItem[]; researcher: string;
  source_basis?: { kind: string; selected_records: number; whole_document_review: boolean; candidate_review?: boolean } | null;
  feedback?: OmissionFeedback[];
};
export type Region = [number, number, number, number];
export type OmissionCommand = { kind: 'omission'; revision: number; operation_id: string; document_id: string;
  page: number; region: Region | null; stage: string; visible_text: string; note: string };
export type OmissionFeedback = OmissionCommand & { status: 'pending'; reviewer: string; recorded_at: string;
  source_sha256: string; event_sha256: string };
export type FeedbackReceipt = { revision: number; event_sha256: string; feedback: OmissionFeedback };
// base path of the same-origin review API bridge (app/review/api)
export type Connection = { api: string };
export const REVIEW_CONNECTION: Connection = { api: '/review' };

export function selectionRegion(start: [number, number], end: [number, number]): Region | null {
  if (![...start, ...end].every(Number.isFinite)) return null;
  const [x1, y1, x2, y2] = [...start, ...end].map(n => Math.max(0, Math.min(1, n)));
  const box: Region = [Math.min(x1, x2), Math.min(y1, y2), Math.max(x1, x2), Math.max(y1, y2)];
  return box[0] < box[2] && box[1] < box[3] ? box : null;
}

export function readableValue(value: unknown): string {
  if (value === null) return 'Not recorded in the reviewed source.';
  if (Array.isArray(value)) return value.map(row => row && typeof row === 'object' && 'from' in row && 'to' in row
    ? `${String(row.from).replace('row-', 'Step ')} to ${String(row.to).replace('row-', 'Step ')}${row.label ? ': ' + row.label : ''}`
    : String(row)).join('\n');
  return String(value);
}

export function fieldLabel(name: string): string {
  const value = name.replaceAll('_', ' ');
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export function recordStatus(item: { audience: string; findings: string[]; reference_only?: boolean;
  source_gaps?: { issue: string }[]; fields: { decision: string }[] }) {
  if (item.audience === 'excluded') return 'Outside this study';
  if (item.findings.length || item.source_gaps?.length) return 'Known source problem';
  if (item.reference_only) return 'Reviewed reference';
  if (item.fields.some(f => f.decision === 'unresolved')) return 'Needs clarification';
  if (item.audience === 'unresolved' && item.fields.some(f => f.decision !== 'pending')) return 'Audience not checked';
  return item.fields.length && item.fields.every(f => ['accepted', 'corrected'].includes(f.decision))
    ? 'Review saved' : 'Not checked yet';
}

export function filterItems<T extends {
  document_id: string; title: string; audience: string; findings: string[];
  source_gaps?: { issue: string; message?: string }[];
  reference_only?: boolean;
  fields: { decision: string; original_value: unknown }[];
}>(items: T[], document: string, query: string, mode: string): T[] {
  const text = query.trim().toLocaleLowerCase();
  return items.filter(item => (!document || item.document_id === document)
    && (!text || [item.title, ...item.findings.map(fieldLabel), ...(item.source_gaps ?? []).map(g => fieldLabel(g.issue) + ' ' + (g.message ?? '')),
      ...item.fields.map(f => typeof f.original_value === 'string'
      ? f.original_value : JSON.stringify(f.original_value))].join(' ').toLocaleLowerCase().includes(text))
    && (mode === 'all'
      || mode === 'attention' && (item.findings.length > 0 || !!item.source_gaps?.length
        || !item.reference_only && item.audience !== 'excluded' && (item.audience === 'unresolved'
          || item.fields.some(f => !['accepted', 'corrected'].includes(f.decision))))
      || mode === 'pending' && !item.reference_only && item.audience !== 'excluded'
        && !item.fields.some(f => f.decision === 'unresolved')
        && (item.audience === 'unresolved' || item.fields.some(f => f.decision === 'pending'))
      || mode === 'held' && item.fields.some(f => f.decision === 'unresolved')
      || mode === 'reviewed' && !item.reference_only && item.audience === 'undergraduate'
        && item.fields.length > 0 && item.fields.every(f => ['accepted', 'corrected'].includes(f.decision))
      || mode === 'excluded' && item.audience === 'excluded'
      || mode === 'source-problems' && (item.findings.length > 0 || !!item.source_gaps?.length)));
}

export function sourceRectangle(span: SourceSpan) {
  const box = span.bbox, size = span.page_size;
  if (!box || box.length !== 4 || !size || size.length !== 2
      || ![...box, ...size].every(Number.isFinite) || size.some(n => n <= 0)
      || !['TOPLEFT', 'BOTTOMLEFT'].includes(span.bbox_origin ?? '')) return null;
  const [left, bottom, right, top] = box;
  const x = Math.min(left, right), low = Math.min(bottom, top), high = Math.max(bottom, top);
  if (x < 0 || low < 0 || Math.max(left, right) > size[0] || high > size[1]) return null;
  return { x, y: span.bbox_origin === 'BOTTOMLEFT' ? size[1] - high : low,
    width: Math.abs(right - left), height: high - low };
}
