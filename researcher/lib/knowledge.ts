// Pure logic for the Knowledge tab: URL state, query building, source grouping and paging.

export const CHUNK_LIMIT = 20;
export type KnowledgeSource = { id: string; kind: string; label: string; chunk_count?: number; status?: string; active?: boolean };
export type SourcesReply = { sources: KnowledgeSource[]; unavailable?: { local?: string; hosted?: string } };
export type Chunk = { chunk_id: string; text: string; document_title?: string; section?: string; pages?: number[];
  source_sha256?: string; reading_id?: string; token_count?: number };
export type ChunksReply = { chunks: Chunk[]; total: number; offset: number; limit: number };
export type KnowledgeUrlState = { source: string; q: string; chunk: string; offset: number };

export const packageSourceId = (uploadId: string) => 'package:' + uploadId;

export function parseKnowledgeUrl(search: string): KnowledgeUrlState {
  const params = new URLSearchParams(search);
  const offset = Number.parseInt(params.get('offset') ?? '', 10);
  return { source: params.get('source') ?? '', q: params.get('q') ?? '', chunk: params.get('chunk') ?? '',
    offset: Number.isFinite(offset) && offset > 0 ? offset : 0 };
}

export function knowledgeUrl(state: KnowledgeUrlState) {
  const params = new URLSearchParams();
  if (state.source) params.set('source', state.source);
  if (state.q) params.set('q', state.q);
  if (state.chunk) params.set('chunk', state.chunk);
  if (state.offset > 0) params.set('offset', String(state.offset));
  const text = params.toString();
  return '/review/knowledge' + (text ? '?' + text : '');
}

export function chunksQuery({ source, q, offset, limit }: { source: string; q: string; offset: number; limit: number }) {
  const params = new URLSearchParams({ source });
  if (q.trim()) params.set('q', q.trim());
  params.set('offset', String(offset)); params.set('limit', String(limit));
  return params.toString();
}

const GROUPS: [string, string][] = [['package', 'Built packages'], ['local', 'Local Supabase'], ['hosted', 'Online (read-only)']];

export function groupSources(sources: KnowledgeSource[]) {
  const known = GROUPS.map(([kind, heading]) => ({ kind, heading, sources: sources.filter(s => s.kind === kind) }));
  const other = sources.filter(s => !GROUPS.some(([kind]) => kind === s.kind));
  return [...known, ...(other.length ? [{ kind: 'other', heading: 'Other sources', sources: other }] : [])]
    .filter(group => group.sources.length);
}

export function pageWindow(total: number, offset: number, limit: number) {
  const pages = Math.max(1, Math.ceil(total / limit));
  return { from: total ? offset + 1 : 0, to: Math.min(total, offset + limit), total,
    page: Math.min(pages, Math.floor(offset / limit) + 1), pages,
    prev: offset > 0 ? Math.max(0, offset - limit) : null, next: offset + limit < total ? offset + limit : null };
}

export function pageImagePath(sha256: string, page: number, scale?: number) {
  const params = new URLSearchParams({ sha256, page: String(page) });
  if (scale) params.set('scale', String(scale));
  return '/api/knowledge/page?' + params.toString();
}
