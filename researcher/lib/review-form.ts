// Pure helpers for the Documents review panel: list windowing, keyboard stepping and the decision form's defaults.
import type { Gap, ReviewItem } from './review-state';

export const DEFAULT_REASON = 'Checked against the page';

export type Draft = { audience: string; reason: string; companions: string[]; gaps: Gap[];
  fields: Record<string, { decision: string; text: string }> };

export function draftFor(row: ReviewItem): Draft {
  return { audience: row.audience, reason: row.reason ?? '', companions: row.companions,
    gaps: row.gaps ?? [], fields: Object.fromEntries(row.fields.map(field =>
      [field.name, { decision: field.decision, text: textOf(field.reviewed_value) }])) };
}

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

// Smallest scroll change that brings row `index` fully into view.
export function revealScrollTop(scrollTop: number, viewport: number, index: number, rowHeight: number) {
  const top = index * rowHeight, bottom = top + rowHeight;
  if (top < scrollTop) return top;
  if (bottom > scrollTop + viewport) return bottom - viewport;
  return scrollTop;
}

export function textOf(value: unknown) { return typeof value === 'string' ? value : JSON.stringify(value, null, 2); }

// "Matches" puts the extracted text back, so a decision never pairs with an edit the reviewer abandoned.
export function fieldAfterChoice(original: unknown, current: { decision: string; text: string }, choice: string) {
  return { decision: choice, text: choice === 'accepted' ? textOf(original) : current.text };
}

type DraftSummary = { audience: string; gaps: unknown[]; fields: Record<string, { decision: string }> };

// The server always needs a reason. Use the reviewer's own words; fall back to a short default only when
// something was actually decided, so an untouched record can never be saved as "checked".
export function reasonFor(reason: string, draft: DraftSummary) {
  const own = reason.trim();
  if (own) return own;
  const decided = draft.audience !== 'unresolved' || draft.gaps.length > 0
    || Object.values(draft.fields).some(field => field.decision !== 'pending');
  return decided ? DEFAULT_REASON : '';
}
