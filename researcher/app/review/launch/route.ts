import { NextResponse, type NextRequest } from 'next/server';
import { REVIEW_COOKIE, sameToken } from '@/lib/review-access';

export const dynamic = 'force-dynamic';

// The printed launch link: trade the one-time token in the URL for an HttpOnly cookie, then show the clean /review address.
export function GET(request: NextRequest) {
  const token = process.env.BINTANONG_REVIEW_TOKEN ?? '';
  if (token.length < 16 || !sameToken(request.nextUrl.searchParams.get('token') ?? '', token)) {
    return new NextResponse('This launch link does not match the running review session. Use the newest link printed by the local review command.',
      { status: 403, headers: { 'content-type': 'text/plain; charset=utf-8' } });
  }
  // relative, so the browser stays on the host it opened (request.url may say localhost while the cookie is for 127.0.0.1)
  const response = new NextResponse(null, { status: 303, headers: { location: '/review' } });
  response.cookies.set(REVIEW_COOKIE, token, { httpOnly: true, sameSite: 'strict', path: '/review' });
  return response;
}
