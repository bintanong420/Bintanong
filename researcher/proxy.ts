import { NextResponse, type NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const host = request.headers.get('host') ?? '';
  if (!/^(127\.0\.0\.1|localhost):\d+$/.test(host)) {
    return new NextResponse('This researcher tool only accepts loopback requests.', { status: 403 });
  }
  return NextResponse.next();
}
