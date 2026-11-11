import type { Connection } from './review-state';

export class ReviewError extends Error {
  status: number;
  code?: string;  // machine-readable reason from the server, e.g. package_exists
  constructor(message: string, status: number, code?: string) { super(message); this.status = status; this.code = code; }
}

export async function request(connection: Connection, path: string, init: RequestInit = {}) {
  // same-origin: the review server adds the session token from its launch cookie
  const response = await fetch(connection.api + path, { ...init, cache: 'no-store', credentials: 'same-origin',
    headers: { ...(init.body ? { 'Content-Type': 'application/json' } : {}), ...init.headers } });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ReviewError(body.error ?? `Review request failed (${response.status}).`, response.status,
      typeof body.code === 'string' ? body.code : undefined);
  }
  return response;
}

export function download(value: unknown, filename: string) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }));
  const link = document.createElement('a');
  link.href = url; link.download = filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
