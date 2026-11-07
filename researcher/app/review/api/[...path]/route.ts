import { NextResponse, type NextRequest } from 'next/server';
import { authorizeReview, REVIEW_COOKIE } from '@/lib/review-access';

export const dynamic = 'force-dynamic';
const MAX_BODY = 1024 * 1024;  // the review API's own limit

// Same-origin bridge to the local review API: the token stays on this server and is added here.
async function forward(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const token = process.env.BINTANONG_REVIEW_TOKEN, api = process.env.BINTANONG_REVIEW_API_ORIGIN;
  const uiOrigin = process.env.BINTANONG_REVIEW_UI_ORIGIN;
  const refusal = authorizeReview({ token, cookie: request.cookies.get(REVIEW_COOKIE)?.value, method: request.method,
    origin: request.headers.get('origin'), fetchSite: request.headers.get('sec-fetch-site'), uiOrigin });
  if (refusal || !api || !token || !uiOrigin) {
    return NextResponse.json({ error: refusal ?? 'The review session is not configured.' }, { status: 403 });
  }
  const { path } = await params;
  if (path.some(segment => segment === '.' || segment === '..')) {
    return NextResponse.json({ error: 'Invalid review path.' }, { status: 404 });
  }
  const body = request.method === 'GET' ? undefined : await request.arrayBuffer();
  if (body && body.byteLength > MAX_BODY) return NextResponse.json({ error: 'Request too large.' }, { status: 413 });
  const headers: Record<string, string> = { 'x-review-token': token, origin: uiOrigin };
  const type = request.headers.get('content-type');
  if (type) headers['content-type'] = type;
  const target = new URL('/api/' + path.map(encodeURIComponent).join('/') + request.nextUrl.search, api);
  let upstream: Response;
  try {
    upstream = await fetch(target, { method: request.method, headers, body, cache: 'no-store', redirect: 'manual' });
  } catch {
    return NextResponse.json({ error: 'The local review API is not responding. Check the review command terminal.' }, { status: 502 });
  }
  return new NextResponse(upstream.body, { status: upstream.status, headers: {
    'content-type': upstream.headers.get('content-type') ?? 'application/octet-stream', 'cache-control': 'no-store' } });
}

export { forward as GET, forward as POST };
