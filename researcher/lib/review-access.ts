import { timingSafeEqual } from 'node:crypto';

// Server-side gate for the same-origin review API proxy. Returns null when allowed, otherwise the refusal reason.
// The launch link puts the per-session token in an HttpOnly cookie; the browser never sends the token itself.
export const REVIEW_COOKIE = 'bintanong-review';

export function sameToken(given: string | undefined, token: string) {
  const a = Buffer.from(given ?? ''), b = Buffer.from(token);
  return a.length === b.length && timingSafeEqual(a, b);
}

export function authorizeReview({ token, cookie, method, origin, fetchSite, uiOrigin }: {
  token?: string; cookie?: string; method: string; origin?: string | null; fetchSite?: string | null; uiOrigin?: string;
}) {
  if (!token || token.length < 16 || !uiOrigin) return 'The review session is not configured. Start it with the local review command.';
  if (!sameToken(cookie, token)) return 'Open the launch link printed by the local review command first.';
  if (fetchSite && fetchSite !== 'same-origin') return 'Review requests must come from the review page.';
  if (method !== 'GET' && method !== 'HEAD' && origin !== uiOrigin) return 'Review changes must come from the review page.';
  return null;
}
