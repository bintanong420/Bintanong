// Which upstream response headers the same-origin review proxy passes on. Everything else is dropped,
// and a cache lifetime is honoured only in the exact private form the review API sets for page images.
const PRIVATE_CACHE = /^private, max-age=\d{1,4}$/;
// page geometry the source viewer needs to place highlight boxes; numbers only
const PAGE_HEADERS: Record<string, RegExp> = {
  'x-page-count': /^\d{1,6}$/, 'x-page-width': /^\d{1,6}(\.\d{1,20})?$/,
  'x-page-height': /^\d{1,6}(\.\d{1,20})?$/, 'x-page-rotation': /^\d{1,3}$/,
};

export function proxyResponseHeaders(upstream: Headers): Record<string, string> {
  const cache = upstream.get('cache-control') ?? '';
  const result: Record<string, string> = {
    'content-type': upstream.get('content-type') ?? 'application/octet-stream',
    'cache-control': PRIVATE_CACHE.test(cache) ? cache : 'no-store',
  };
  // a source PDF is shown in place; any other disposition (a download or a filename) is dropped
  if (upstream.get('content-disposition') === 'inline') result['content-disposition'] = 'inline';
  for (const [name, pattern] of Object.entries(PAGE_HEADERS)) {
    const value = upstream.get(name) ?? '';
    if (pattern.test(value)) result[name] = value;
  }
  return result;
}