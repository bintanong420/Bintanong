'use client';

import { useCallback, useEffect, useState } from 'react';
import { IntakeBuild } from '@/components/intake-build';
import { IntakeUpload } from '@/components/intake-upload';
import { IntakeUploads, type Upload } from '@/components/intake-uploads';
import { Button } from '@/components/ui/button';
import { appearanceKey, appearanceValue } from '@/lib/appearance';
import { request } from '@/lib/api';
import { REVIEW_CONNECTION } from '@/lib/review-state';

export default function IntakePage() {
  const [uploads, setUploads] = useState<Upload[] | null>(null), [currentId, setCurrentId] = useState<string | null>(null);
  const [error, setError] = useState(''), [opening, setOpening] = useState(false);

  const load = useCallback(async () => {
    try {
      setUploads((await (await request(REVIEW_CONNECTION, '/api/intake/uploads')).json()).uploads);
      setCurrentId((await (await request(REVIEW_CONNECTION, '/api/intake/current')).json()).upload_id);
      setError('');
    } catch (failure) { setError(failure instanceof Error ? failure.message : 'The uploads could not be loaded.'); }
  }, []);

  useEffect(() => {
    try { document.documentElement.dataset.appearance = appearanceValue(localStorage.getItem(appearanceKey)); } catch { /* defaults apply */ }
    void load();
  }, [load]);

  async function open(uploadId: string) {
    if (opening) return;
    setOpening(true); setError('');
    try {
      await request(REVIEW_CONNECTION, '/api/intake/open', { method: 'POST', body: JSON.stringify({ upload_id: uploadId }) });
      window.location.assign('/review');  // the normal review UI loads the opened packet
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'The upload could not be opened.');
      setOpening(false);
    }
  }

  return <main className="intake-page">
    <header className="app-header"><div><p className="wordmark">Bintanong <span>Knowledge intake</span></p>
      <p className="muted">Upload a handbook-style PDF, prepare it, then review it. Nothing here approves content or activates it.</p></div>
      <div className="header-actions"><Button variant="outline" asChild><a href="/review">Back to review</a></Button></div>
    </header>
    <div className="intake-body">
      <IntakeUpload onUploaded={() => void load()} />
      <IntakeUploads uploads={uploads} currentId={currentId} onOpen={id => void open(id)} error={error} />
      <section className="intake-section" aria-label="Open upload">
        <p role="status">{currentId ? <>Open for review: <code>{currentId}</code>. <a href="/review">Go to review</a></> : 'No upload is open for review.'}</p>
      </section>
      {currentId && <IntakeBuild uploadId={currentId} />}
    </div>
  </main>;
}
