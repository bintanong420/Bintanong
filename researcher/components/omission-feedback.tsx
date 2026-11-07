'use client';

import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { request, ReviewError } from '@/lib/api';
import type { Connection, FeedbackReceipt, OmissionCommand, Region } from '@/lib/review-state';

export function OmissionFeedback({ connection, documentId, documentTitle, page, region, revision, onSaved, onClose }: {
  connection: Connection; documentId: string; documentTitle: string; page: number; region: Region | null; revision: number;
  onSaved: (receipt: FeedbackReceipt) => void; onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [visibleText, setVisibleText] = useState(''), [note, setNote] = useState(''), [stage, setStage] = useState('not_sure');
  const [busy, setBusy] = useState(false), [error, setError] = useState('');
  const pending = useRef<OmissionCommand | null>(null);
  const dirty = !!visibleText || !!note || stage !== 'not_sure';
  useEffect(() => { dialog.current?.showModal(); }, []);
  useEffect(() => {
    function protect(event: BeforeUnloadEvent) { if (dirty || pending.current) { event.preventDefault(); event.returnValue = ''; } }
    window.addEventListener('beforeunload', protect);
    return () => window.removeEventListener('beforeunload', protect);
  }, [dirty]);
  function close() {
    if (busy) return;
    if ((dirty || pending.current) && !window.confirm(pending.current
      ? 'The save outcome is unknown. Close this draft and check Saved reviews before reporting again?'
      : 'Discard this unsaved missing-content note?')) return;
    dialog.current?.close();
  }
  async function save() {
    if (busy) return;
    setBusy(true); setError('');
    pending.current ??= { kind: 'omission', revision, operation_id: crypto.randomUUID(), document_id: documentId,
      page, region, stage, visible_text: visibleText, note };
    try {
      const receipt: FeedbackReceipt = await (await request(connection, '/api/decision', {
        method: 'POST', body: JSON.stringify(pending.current),
      })).json();
      pending.current = null; onSaved(receipt); onClose();
    } catch (error) {
      if (error instanceof ReviewError && error.status < 500) { pending.current = null; setError(error.message); }
      else setError('The save response was lost. Your note is retained. Retry the same save to check its outcome.');
    } finally { setBusy(false); }
  }
  return <dialog ref={dialog} className="feedback-dialog" aria-labelledby="feedback-title" onClose={onClose}
    onCancel={event => { event.preventDefault(); close(); }}>
    <div className="pane-heading"><h2 id="feedback-title">Report missing content</h2><Button type="button" variant="outline" disabled={busy} onClick={close}>Close</Button></div>
    <p>{documentTitle} · PDF page {page}</p><p className="muted">{region ? 'Your marked region is attached.' : 'This note refers to the whole page.'}
      {' '}This saves pending feedback. It does not approve content or add it to the chatbot.</p>
    {error && <p role="alert" className="notice error">{error}</p>}
    <form onSubmit={e => { e.preventDefault(); void save(); }}>
      <fieldset disabled={busy || !!pending.current}>
        <label>Where did you notice the omission?<select value={stage} onChange={e => setStage(e.target.value)}>
          <option value="not_sure">Not sure yet</option><option value="extraction">Text extraction (Docling)</option>
          <option value="context">Stored records or context links</option><option value="retrieval">Search results (RAG)</option>
        </select></label>
        <label>What wording is visible in the PDF?<Textarea aria-label="Missing source wording" required maxLength={20000} rows={5} value={visibleText}
          onChange={e => setVisibleText(e.target.value)}/></label>
        <label>What is missing or linked incorrectly?<Textarea aria-label="Missing content note" required maxLength={8000} rows={3} value={note}
          onChange={e => setNote(e.target.value)}/></label>
      </fieldset>
      <Button type="submit" disabled={busy || !visibleText.trim() || !note.trim()}>{busy ? 'Saving…' : pending.current ? 'Retry same save' : 'Save missing-content note'}</Button>
    </form>
  </dialog>;
}
