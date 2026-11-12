'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { request, ReviewError } from '@/lib/api';
import { pageImagePath } from '@/lib/knowledge';
import { REVIEW_CONNECTION } from '@/lib/review-state';

// One source page, fetched by PDF hash. A 404 means this machine does not hold that PDF; it is reported, not retried.
export function PageImage({ sha256, page, scale = 1.5, onCount }: { sha256: string; page: number; scale?: number; onCount?: (count: number) => void }) {
  const [state, setState] = useState<{ kind: 'loading' } | { kind: 'ready'; url: string } | { kind: 'missing' } | { kind: 'error'; message: string }>({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let current = true, objectUrl = '';
    setState({ kind: 'loading' });
    request(REVIEW_CONNECTION, pageImagePath(sha256, page, scale), { cache: 'default' }).then(async response => {
      const blob = await response.blob();
      if (!current) return;
      objectUrl = URL.createObjectURL(blob);
      const count = Number(response.headers.get('x-page-count'));
      if (count > 0) onCount?.(count);
      setState({ kind: 'ready', url: objectUrl });
    }).catch(failure => {
      if (!current) return;
      if (failure instanceof ReviewError && failure.status === 404) setState({ kind: 'missing' });
      else setState({ kind: 'error', message: failure instanceof Error ? failure.message : 'The page could not be loaded.' });
    });
    return () => { current = false; if (objectUrl) URL.revokeObjectURL(objectUrl); };
    // onCount is a stable setter in every caller; leaving it out avoids refetching on each render
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sha256, page, scale, attempt]);

  return <div className="page-frame" aria-live="polite">
    {state.kind === 'loading' && <div className="page-placeholder" role="status" aria-busy="true"><span className="spinner" aria-hidden="true" /> Loading page {page}…</div>}
    {state.kind === 'missing' && <div className="page-placeholder"><p><strong>Source PDF not available on this machine.</strong></p>
      <p className="muted">This review server has no PDF with this hash, so page {page} cannot be shown.</p><p><code>{sha256}</code></p></div>}
    {state.kind === 'error' && <div className="page-placeholder notice error" role="alert"><span><strong>Page {page} could not be loaded.</strong> {state.message}</span>
      <Button variant="outline" size="sm" onClick={() => setAttempt(n => n + 1)}>Try again</Button></div>}
    {/* eslint-disable-next-line @next/next/no-img-element */}
    {state.kind === 'ready' && <img className="page-img" src={state.url} alt={`Source page ${page}`} />}
  </div>;
}
