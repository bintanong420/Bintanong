// Pure logic for the Knowledge tab: URL state, query building, source grouping and paging.

export const CHUNK_LIMIT = 20;
export type KnowledgeSource = { id: string; kind: string; label: string; chunk_count?: number; status?: string; active?: boolean };
export type SourcesReply = { sources: KnowledgeSource[]; unavailable?: { local?: string; hosted?: string } };
export type Chunk = { chunk_id: string; text: string; document_title?: string; section?: string; pages?: number[];
  source_sha256?: string; reading_id?: string; token_count?: number };
export type ChunksReply = { chunks: Chunk[]; total: number; offset: number; limit: number };
export type LibraryDocument = { document_key: string; title: string; source_sha256?: string; chunk_count: number;
  pages: number[]; pdf_available: boolean };
export type DocumentsReply = { documents: LibraryDocument[]; source: string; truncated?: boolean };
export type KnowledgeUrlState = { source: string; q: string; chunk: string; document: string; offset: number };

export const packageSourceId = (uploadId: string) => 'package:' + uploadId;

export function parseKnowledgeUrl(search: string): KnowledgeUrlState {
  const params = new URLSearchParams(search);
  const offset = Number.parseInt(params.get('offset') ?? '', 10);
  return { source: params.get('source') ?? '', q: params.get('q') ?? '', chunk: params.get('chunk') ?? '',
    document: params.get('document') ?? '', offset: Number.isFinite(offset) && offset > 0 ? offset : 0 };
}

export function knowledgeUrl(state: KnowledgeUrlState) {
  const params = new URLSearchParams();
  if (state.source) params.set('source', state.source);
  if (state.document) params.set('document', state.document);
  if (state.q) params.set('q', state.q);
  if (state.chunk) params.set('chunk', state.chunk);
  if (state.offset > 0) params.set('offset', String(state.offset));
  const text = params.toString();
  return '/review/knowledge' + (text ? '?' + text : '');
}

export function chunksQuery({ source, q, document, offset, limit }:
  { source: string; q: string; document: string; offset: number; limit: number }) {
  const params = new URLSearchParams({ source });
  if (q.trim()) params.set('q', q.trim());
  if (document) params.set('document', document);
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

// The library lists the online release first: it is what the public runtime reads.
const LIBRARY_ORDER = ['hosted', 'local', 'package'];

export function libraryGroups(sources: KnowledgeSource[]) {
  const byKind = new Map(groupSources(sources).map(group => [group.kind, group]));
  const ordered = [...LIBRARY_ORDER, 'other'].flatMap(kind => byKind.get(kind) ?? []);
  return ordered;
}

export const chunkCountText = (count: number) => `${count.toLocaleString('en-US')} chunk${count === 1 ? '' : 's'}`;

export function pageRangeText(pages: number[]) {
  if (!pages.length) return 'No page reference';
  return pages[0] === pages[pages.length - 1] ? `Page ${pages[0]}` : `Pages ${pages[0]} to ${pages[pages.length - 1]}`;
}

export function pdfText(doc: Pick<LibraryDocument, 'pdf_available' | 'source_sha256'>) {
  if (!doc.source_sha256) return 'No source PDF recorded';
  return doc.pdf_available ? 'PDF on this machine' : 'PDF not on this machine';
}

export const documentsPath = (source: string) => '/api/knowledge/documents?' + new URLSearchParams({ source }).toString();

export const documentLink = (source: string, doc: LibraryDocument) =>
  knowledgeUrl({ source, q: '', chunk: '', document: doc.document_key, offset: 0 });

// A hash key has no readable name of its own, so the chip borrows the title a loaded chunk carries.
export function documentChipLabel(key: string, chunks: { document_title?: string }[]) {
  if (!/^[0-9a-f]{64}$/.test(key)) return key;
  return chunks.find(chunk => chunk.document_title)?.document_title ?? 'Document ' + key.slice(0, 8);
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
