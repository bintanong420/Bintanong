'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { request, ReviewError } from '@/lib/api';
import { shouldPoll, shouldPollBuild, type BuildStatus } from '@/lib/intake';
import { REVIEW_CONNECTION } from '@/lib/review-state';

export type PrepareStatus = { state: string; exit_code?: number; error?: string; log_tail?: string[];
  gemma_unavailable_fields?: number; assist?: boolean };
export type UploadState = { prepare?: PrepareStatus; build?: BuildStatus; error?: string; buildError?: string };

function message(error: unknown) { return error instanceof Error ? error.message : 'The request failed.'; }

// One place that knows every upload's Prepare and Build status, so the list rows and the detail pane never disagree.
// It polls only while some job is running: a finished, failed or interrupted job never changes by itself.
export function useUploadStates(ids: string[]) {
  const [states, setStates] = useState<Record<string, UploadState>>({});
  const asked = useRef(new Set<string>());

  const refresh = useCallback(async (id: string) => {
    const [prepare, build] = await Promise.allSettled([
      request(REVIEW_CONNECTION, '/api/intake/prepare/' + encodeURIComponent(id)).then(r => r.json() as Promise<PrepareStatus>),
      request(REVIEW_CONNECTION, '/api/intake/build/' + encodeURIComponent(id)).then(r => r.json() as Promise<BuildStatus>)]);
    setStates(all => {
      const old = all[id] ?? {};
      const next: UploadState = { ...old };
      if (prepare.status === 'fulfilled') { next.prepare = prepare.value; next.error = undefined; } else next.error = message(prepare.reason);
      if (build.status === 'fulfilled') { next.build = build.value; next.buildError = undefined; }
      // no build has been started for this upload: that is not a failure
      else if (build.reason instanceof ReviewError && build.reason.status === 404) { next.build = undefined; next.buildError = undefined; }
      else next.buildError = message(build.reason);
      return { ...all, [id]: next };
    });
  }, []);

  const key = ids.join('\n');
  useEffect(() => {
    for (const id of ids) if (!asked.current.has(id)) { asked.current.add(id); void refresh(id); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, refresh]);

  useEffect(() => {
    const running = ids.filter(id => shouldPoll(states[id]?.prepare?.state) || shouldPollBuild(states[id]?.build?.state));
    if (!running.length) return;
    const timer = setTimeout(() => running.forEach(id => void refresh(id)), 3000);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [states, key, refresh]);

  const patch = useCallback((id: string, change: Partial<UploadState>) =>
    setStates(all => ({ ...all, [id]: { ...all[id], ...change } })), []);
  return { states, refresh, patch };
}
