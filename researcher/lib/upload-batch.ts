// Pure logic for uploading several documents from the Intake page. Each file stays its own upload with its own fields;
// the review server remains authoritative for every limit, so nothing here approves or accepts a file.
import { checkUploadFile, fieldErrors, type UploadField } from './intake.ts';

export const MAX_BATCH_FILES = 20;

export type FileLike = { name: string; type: string; size: number };
export type BatchRow<F extends FileLike = FileLike> = { id: string; file: F; title: string; edition: string; kind: string };
export type BatchDefaults = { kind: string; edition: string; office: string; audience: string };
export type SharedNotes = Pick<BatchDefaults, 'office' | 'audience'>;

export function titleFromFileName(name: string) {
  return name.trim().replace(/\.(pdf|png|jpe?g|webp)$/i, '').replace(/[_-]+/g, ' ').replace(/\s+/g, ' ').trim();
}

// A year is 19xx or 20xx not glued to other digits; two years joined by a dash or underscore stay together as one edition.
export function editionFromFileName(name: string) {
  const text = name.replace(/\.(pdf|png|jpe?g|webp)$/i, '');
  const range = text.match(/(?<!\d)((?:19|20)\d{2})\s*[-_]\s*((?:19|20)\d{2})(?!\d)/);
  if (range) return `${range[1]}-${range[2]}`;
  return text.match(/(?<!\d)(?:19|20)\d{2}(?!\d)/)?.[0] ?? '';
}

export function addFiles<F extends FileLike>(rows: BatchRow<F>[], files: F[], defaults: Pick<BatchDefaults, 'kind' | 'edition'>, nextSeq: number) {
  const next = [...rows];
  let seq = nextSeq, duplicates = 0, overLimit = 0;
  for (const file of files) {
    if (next.some(row => row.file === file)) { duplicates++; continue; }
    if (next.length >= MAX_BATCH_FILES) { overLimit++; continue; }
    next.push({ id: `r${seq++}`, file, kind: defaults.kind, title: titleFromFileName(file.name),
      edition: editionFromFileName(file.name) || defaults.edition.trim() });
  }
  return { rows: next, nextSeq: seq, duplicates, overLimit };
}

// Kind goes on every row; a blank edition leaves the rows' own editions alone.
export function applyToAll<F extends FileLike>(rows: BatchRow<F>[], values: { kind: string; edition: string }) {
  const edition = values.edition.trim();
  return rows.map(row => ({ ...row, kind: values.kind, edition: edition || row.edition }));
}

export type RowProblems = { file?: string; fields: Partial<Record<UploadField, string>> };
export function rowProblems(row: BatchRow, notes: SharedNotes): RowProblems {
  const file = checkUploadFile(row.file) ?? undefined;
  const fields = fieldErrors({ kind: row.kind, title: row.title, edition: row.edition, office: notes.office, audience: notes.audience });
  return file ? { file, fields } : { fields };
}
export const hasProblems = (problems: RowProblems) => Boolean(problems.file) || Object.keys(problems.fields).length > 0;

export type RowStatus = 'waiting' | 'uploading' | 'uploaded' | 'failed' | 'skipped';
export type RowResult = { status: RowStatus; error?: string; uncertain?: boolean; uploadId?: string; title?: string };
export type BatchState = { phase: 'idle' | 'running' | 'stopping' | 'finished'; results: Record<string, RowResult> };
export const initialBatch: BatchState = { phase: 'idle', results: {} };

export type BatchAction =
  | { type: 'start'; ids: string[] }
  | { type: 'begin'; id: string }
  | { type: 'success'; id: string; uploadId: string; title: string }
  | { type: 'failure'; id: string; error: string; uncertain?: boolean }
  | { type: 'stop' }
  | { type: 'settle' }
  | { type: 'retry'; id: string }
  | { type: 'remove'; id: string }
  | { type: 'reset' };

export function batchReducer(state: BatchState, action: BatchAction): BatchState {
  const set = (id: string, result: RowResult): BatchState => ({ ...state, results: { ...state.results, [id]: result } });
  switch (action.type) {
    case 'start': {
      const results = { ...state.results };
      for (const id of action.ids) if (results[id]?.status !== 'uploaded') results[id] = { status: 'waiting' };
      return { phase: 'running', results };
    }
    case 'begin': return set(action.id, { status: 'uploading' });
    case 'success': return set(action.id, { status: 'uploaded', uploadId: action.uploadId, title: action.title });
    case 'failure': return set(action.id, { status: 'failed', error: action.error, uncertain: action.uncertain });
    case 'stop': return state.phase === 'running' ? { ...state, phase: 'stopping' } : state;
    case 'settle': {
      // a stop leaves the unsent rows visible as "not sent"; a normal run has none waiting
      const results: Record<string, RowResult> = {};
      for (const [id, result] of Object.entries(state.results)) results[id] = result.status === 'waiting' ? { status: 'skipped' } : result;
      return { phase: 'finished', results };
    }
    case 'retry': {
      if (state.phase === 'running' || state.phase === 'stopping') return state;
      const status = state.results[action.id]?.status;
      if (status !== 'failed' && status !== 'skipped') return state;
      return { phase: 'running', results: { ...state.results, [action.id]: { status: 'waiting' } } };
    }
    case 'remove': {
      const { [action.id]: _removed, ...results } = state.results;
      return { ...state, results };
    }
    case 'reset': return initialBatch;
  }
}

export function retryNotice(ids: string[], state: BatchState) {
  return ids.some(id => state.results[id]?.uncertain)
    ? 'An upload response was lost or incomplete. The document may already be saved. Check the uploads list first. Uploading it again can create a duplicate. Send it again?'
    : '';
}

// Rows are sent strictly one after another: nothing new starts once a stop is requested.
export function nextWaiting(order: string[], state: BatchState) {
  if (state.phase !== 'running') return null;
  return order.find(id => state.results[id]?.status === 'waiting') ?? null;
}

export function startableIds(order: string[], state: BatchState) {
  return order.filter(id => state.results[id]?.status !== 'uploaded');
}

export function summaryText(order: string[], state: BatchState) {
  const count = (status: RowStatus) => order.filter(id => state.results[id]?.status === status).length;
  const parts = [[count('uploaded'), 'uploaded'], [count('failed'), 'failed'], [count('skipped'), 'not sent']] as const;
  return parts.filter(([n]) => n > 0).map(([n, word]) => `${n} ${word}`).join(', ');
}

export function progressText(order: string[], names: Record<string, string>, state: BatchState) {
  const members = order.filter(id => state.results[id]);
  const current = members.find(id => state.results[id].status === 'uploading');
  if (!current) return '';
  if (state.phase === 'stopping') return `Stopping after ${names[current]}. The files not yet sent stay in the list.`;
  return `Uploading ${members.indexOf(current) + 1} of ${members.length}: ${names[current]}`;
}
