// Pure helpers for the Documents review panel: list windowing, keyboard stepping, the decision form and its save payload.
import type { Gap, ReviewItem } from './review-state';

// Offered as a one-click suggestion for the note. It is never filled in for the reviewer.
export const SUGGESTED_NOTE = 'Checked against the page';

// `edit` remembers the last typed correction so Matches -> Fix text does not lose it.
export type FieldDraft = { decision: string; text: string; edit?: string };
export type Draft = { audience: string; reason: string; companions: string[]; gaps: Gap[]; fields: Record<string, FieldDraft> };

export function textOf(value: unknown) { return typeof value === 'string' ? value : JSON.stringify(value, null, 2); }

export function draftFor(row: ReviewItem): Draft {
  return { audience: row.audience, reason: row.reason ?? '', companions: row.companions,
    gaps: row.gaps ?? [], fields: Object.fromEntries(row.fields.map(field =>
      [field.name, { decision: field.decision, text: textOf(field.reviewed_value) }])) };
}

export function isDirty(row: ReviewItem, draft: Draft) {
  const plain = { ...draft, fields: Object.fromEntries(Object.entries(draft.fields).map(([name, { decision, text }]) => [name, { decision, text }])) };
  return JSON.stringify(draftFor(row)) !== JSON.stringify(plain);
}

// The command the server receives. Untouched fields stay pending with their text; the reason is what the reviewer wrote.
export function buildPayload(row: ReviewItem, draft: Draft, revision: number, operationId: string) {
  const fields = Object.fromEntries(row.fields.map(field => [field.name, {
    decision: draft.fields[field.name].decision,
    value: typeof field.original_value === 'string' ? draft.fields[field.name].text : JSON.parse(draft.fields[field.name].text),
  }]));
  return { item_id: row.id, revision, operation_id: operationId, audience: draft.audience, reason: draft.reason,
    companions: draft.companions, gaps: draft.gaps, fields };
}

// Leaving a record with edits needs a confirmation; a save whose outcome is unknown blocks leaving altogether.
export function switchGate(dirty: boolean, saving: boolean): 'go' | 'confirm' | 'blocked' {
  return saving ? 'blocked' : dirty ? 'confirm' : 'go';
}
export function leaveWarning(dirty: boolean, saving: boolean) { return dirty || saving; }

// Rows to render for a fixed-height list: those in view plus `overscan` rows each side.
export function windowRange(scrollTop: number, viewport: number, rowHeight: number, count: number, overscan = 4) {
  const top = Math.max(0, scrollTop);
  const start = Math.max(0, Math.min(Math.floor(top / rowHeight), count) - overscan);
  const end = Math.min(count, Math.ceil((top + Math.max(0, viewport)) / rowHeight) + overscan);
  return { start: Math.min(start, end), end };
}

export function stepIndex(index: number, delta: 1 | -1, count: number) {
  if (count <= 0) return -1;
  if (index < 0) return delta > 0 ? 0 : count - 1;
  return Math.max(0, Math.min(count - 1, index + delta));
}

// Row to focus for a list key, or null when the key is not a list key.
export function nextIndexForKey(key: string, current: number, count: number, page = 8): number | null {
  if (count <= 0) return null;
  if (key === 'ArrowDown') return stepIndex(current, 1, count);
  if (key === 'ArrowUp') return stepIndex(current, -1, count);
  if (key === 'Home') return 0;
  if (key === 'End') return count - 1;
  if (key === 'PageDown') return Math.min(count - 1, Math.max(0, current) + page);
  if (key === 'PageUp') return Math.max(0, current - page);
  return null;
}
// Smallest scroll change that brings row `index` fully into view.
export function revealScrollTop(scrollTop: number, viewport: number, index: number, rowHeight: number) {
  const top = index * rowHeight, bottom = top + rowHeight;
  if (top < scrollTop) return top;
  if (bottom > scrollTop + viewport) return bottom - viewport;
  return scrollTop;
}

// "Matches" restores the extracted text, "Not checked" too; the last typed correction is kept in `edit` for Fix text.
export function fieldAfterChoice(original: unknown, current: FieldDraft, choice: string): FieldDraft {
  const edit = current.decision === 'corrected' ? current.text : current.edit;
  const keep = edit === undefined ? {} : { edit };
  if (choice === 'accepted' || choice === 'pending') return { decision: choice, text: textOf(original), ...keep };
  if (choice === 'corrected') return { decision: choice, text: edit ?? current.text, ...keep };
  return { decision: choice, text: current.text, ...keep };
}

const BADGES: Record<string, { label: string; tone: 'todo' | 'done' | 'hold' | 'muted' }> = {
  'Not checked yet': { label: 'Not checked', tone: 'todo' }, 'Review saved': { label: 'Saved', tone: 'done' },
  'Known source problem': { label: 'Source problem', tone: 'hold' }, 'Needs clarification': { label: 'Unclear', tone: 'hold' },
  'Outside this study': { label: 'Outside study', tone: 'muted' }, 'Reviewed reference': { label: 'Reference', tone: 'muted' },
  'Audience not checked': { label: 'Audience not set', tone: 'todo' },
};
export function statusBadge(status: string) { return BADGES[status] ?? { label: status, tone: 'todo' as const }; }