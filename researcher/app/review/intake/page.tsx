'use client';

import { useCallback, useEffect, useState } from 'react';
import { IntakeBuild } from '@/components/intake-build';
import { IntakeUpload } from '@/components/intake-upload';
import { StatusTag } from '@/components/intake-status';
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
    <header className="app-header"><div><h1 className="wordmark">Bintanong <span>Knowledge intake</span></h1>
      <p className="muted">Upload a handbook-style PDF, prepare it, then review it. Nothing here approves content or activates it.</p></div>
      <div className="header-actions"><Button variant="outline" asChild><a href="/review">Back to review</a></Button></div>
    </header>
    <div className="intake-body">
      <nav aria-label="Intake steps" className="overview"><ol>
        <li><a href="#upload"><strong>1 Upload</strong><span>Send a PDF with its title and edition.</span></a></li>
        <li><a href="#prepare"><strong>2 Prepare</strong><span>Docling converts it; Gemma audit is optional.</span></a></li>
        <li><a href="#review"><strong>3 Review</strong><span>Open it and decide each item on the review page.</span></a></li>
        <li><a href="#build"><strong>4 Build form</strong><span>Record readings and claims for the review.</span></a></li>
      </ol></nav>
      <IntakeUpload onUploaded={() => void load()} />
      <IntakeUploads uploads={uploads} currentId={currentId} onOpen={id => void open(id)} error={error} onRetry={() => void load()} />
      <section className="intake-section" id="review" aria-labelledby="review-heading">
        <div className="section-head"><span className="section-number" aria-hidden="true">3</span>
          <div><h2 id="review-heading">Review the open upload</h2>
            <p className="muted">Review decisions are made on the review page, not here.</p></div></div>
        <div aria-live="polite">{currentId
          ? <div className="notice"><StatusTag status="active">Open for review</StatusTag><span><code>{currentId}</code></span><Button asChild><a href="/review">Go to review</a></Button></div>
          : <div className="empty-state"><h3>Nothing is open for review</h3><p className="muted">Prepare an upload in step 2, then choose Open for review.</p></div>}</div>
      </section>
      {currentId ? <IntakeBuild uploadId={currentId} />
        : <section className="intake-section" id="build" aria-labelledby="build-heading">
          <div className="section-head"><span className="section-number" aria-hidden="true">4</span>
            <div><h2 id="build-heading">Build form</h2><p className="muted">Available once an upload is open for review.</p></div></div></section>}
    </div>
  </main>;
}