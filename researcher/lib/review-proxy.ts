// Which upstream response headers the same-origin review proxy passes on. Everything else is dropped,
// and a cache lifetime is honoured only in the exact private form the review API sets for page images.
const PRIVATE_CACHE = /^private, max-age=\d{1,4}$/;

export function proxyResponseHeaders(upstream: Headers): Record<string, string> {
  const cache = upstream.get('cache-control') ?? '';
  const count = upstream.get('x-page-count') ?? '';
  return {
    'content-type': upstream.get('content-type') ?? 'application/octet-stream',
    'cache-control': PRIVATE_CACHE.test(cache) ? cache : 'no-store',
    ...(/^\d{1,6}$/.test(count) ? { 'x-page-count': count } : {}),
  };
}