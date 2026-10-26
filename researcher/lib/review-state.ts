export type SourceSpan = {
  page?: number; bbox?: number[] | null; bbox_origin?: string | null;
  page_size?: number[] | null; text?: string;
};
export type Field = {
  name: string; original_value: unknown; reviewed_value: unknown; decision: string;
  source_blank: boolean; locator: { physical_pages: number[]; field: string }; spans: SourceSpan[];
};
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
  source_basis?: { kind: string; selected_records: number; whole_document_review: boolean } | null;
};
export type Connection = { api: string; token: string };

export function fieldLabel(name: string): string {
  const value = name.replaceAll('_', ' ');
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export function recordStatus(item: { audience: string; findings: string[]; reference_only?: boolean;
  source_gaps?: { issue: string }[]; fields: { decision: string }[] }) {
  if (item.audience === 'excluded') return 'Outside this study';
  if (item.findings.length || item.source_gaps?.length) return 'Known source problem';
  if (item.reference_only) return 'Reviewed reference';
  return item.fields.length && item.fields.every(f => ['accepted', 'corrected'].includes(f.decision))
    ? 'Review saved' : 'Not checked yet';
}

export function parseConnection(fragment: string): Connection {
  const params = new URLSearchParams(fragment.replace(/^#/, ''));
  const api = new URL(params.get('api') ?? '');
  const token = params.get('token') ?? '';
  if (api.protocol !== 'http:' || !['127.0.0.1', 'localhost'].includes(api.hostname)
      || !api.port || api.pathname !== '/' || api.search || api.hash || api.username || api.password
      || !/^[A-Za-z0-9_-]{16,128}$/.test(token)) {
    throw new Error('Open the launch link from the local review command.');
  }
  return { api: api.origin, token };
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
    && (mode === 'all' || item.findings.length > 0 || !!item.source_gaps?.length
      || !item.reference_only && (item.audience === 'unresolved'
        || item.fields.some(f => !['accepted', 'corrected'].includes(f.decision)))));
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
