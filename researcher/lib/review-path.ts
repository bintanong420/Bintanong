// Readable review URLs: /review, /review/policy/<item>, /review/prospectus/<document>[/<question>].

export type ReviewTarget = { kind: 'home' } | { kind: 'policy'; item: string }
  | { kind: 'prospectus'; document: string; question?: string };

export function reviewPath(target: ReviewTarget) {
  if (target.kind === 'policy') return '/review/policy/' + encodeURIComponent(target.item);
  if (target.kind === 'prospectus') return '/review/prospectus/' + encodeURIComponent(target.document)
    + (target.question ? '/' + encodeURIComponent(target.question) : '');
  return '/review';
}

type Routable = { id: string; document_id: string; prospectus_candidate?: unknown };

export function targetForItem(item: Routable, question?: string): ReviewTarget {
  return item.prospectus_candidate ? { kind: 'prospectus', document: item.document_id, ...(question ? { question } : {}) }
    : { kind: 'policy', item: item.id };
}

export function itemForTarget<T extends Routable>(items: T[], target: ReviewTarget) {
  if (target.kind === 'policy') return items.find(item => item.id === target.item && !item.prospectus_candidate);
  if (target.kind === 'prospectus') return items.find(item => item.document_id === target.document && !!item.prospectus_candidate);
  return undefined;
}

export function parseReviewPath(pathname: string): ReviewTarget {
  const [root, kind, ...rest] = pathname.split('/').filter(Boolean);
  try {
    const ids = rest.map(decodeURIComponent);
    if (root === 'review' && kind === 'policy' && ids.length === 1) return { kind: 'policy', item: ids[0] };
    if (root === 'review' && kind === 'prospectus' && (ids.length === 1 || ids.length === 2)) {
      return ids[1] ? { kind: 'prospectus', document: ids[0], question: ids[1] } : { kind: 'prospectus', document: ids[0] };
    }
  } catch { /* a malformed escape opens the review home */ }
  return { kind: 'home' };
}
