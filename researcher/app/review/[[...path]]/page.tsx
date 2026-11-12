'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { SourceViewer } from '@/components/source-viewer';
import { KnowledgeLibrary } from '@/components/knowledge-library';
import { ProspectusReview } from '@/components/prospectus-review';
import { ReviewHistory, type HistoryEntry } from '@/components/review-history';
import { RecordList } from '@/components/record-list';
import { DecisionPane } from '@/components/decision-pane';
import { download, request, ReviewError } from '@/lib/api';
import { buildPayload, draftFor, isDirty, leaveWarning, switchGate, type Draft } from '@/lib/review-form';
import { REVIEW_CONNECTION, type Connection, type FeedbackReceipt, type ReviewState } from '@/lib/review-state';
import { isNoPacketError } from '@/lib/intake';
import { itemForTarget, parseReviewPath, reviewPath, targetForItem } from '@/lib/review-path';

const NOTHING_TO_SAVE = 'Write a short note on what you checked, then save.';

export default function ReviewWorkspace() {
  const [connection, setConnection] = useState<Connection | null>(null);
  const [state, setState] = useState<ReviewState | null>(null), [selected, setSelected] = useState('');
  const [draft, setDraft] = useState<Draft | null>(null), [busy, setBusy] = useState(false);
  const [error, setError] = useState(''), [message, setMessage] = useState(''), [noPacket, setNoPacket] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[] | null>(null), [panel, setPanel] = useState<'help' | 'library' | null>(null);
  const [libraryOpened, setLibraryOpened] = useState(false);
  const [sourceFocus, setSourceFocus] = useState<{ itemId: string; page: number } | null>(null);
  const [linkedQuestion, setLinkedQuestion] = useState<string>();
  const pending = useRef<Record<string, unknown> | null>(null), menu = useRef<HTMLDetailsElement>(null);
  const item = useMemo(() => state?.items.find(row => row.id === selected) ?? null, [state, selected]);
  const dirty = useMemo(() => !!item && !!draft && isDirty(item, draft), [item, draft]);
  const sourceDoc = state?.documents.find(doc => doc.id === item?.document_id);
  const relatedItems = useMemo(() => state && draft ? state.items.filter(row => draft.companions.includes(row.id)) : [], [state, draft?.companions]);

  const reload = useCallback(async (c: Connection) => {
    const value: ReviewState = await (await request(c, '/api/state')).json();
    setState(value); return value;
  }, []);

  useEffect(() => {
    try {
      sessionStorage.removeItem('bintanong-review-connection');  // tokens from older launch links are no longer kept
    } catch { /* storage can be unavailable; defaults apply */ }
    setConnection(REVIEW_CONNECTION);
    // the intake tool starts with nothing open; ask first so the empty state is not a failed request
    const nothingOpen = request(REVIEW_CONNECTION, '/api/intake/current').then(async r => (await r.json()).upload_id === null, () => false);
    void nothingOpen.then(empty => { if (empty) { setNoPacket(true); return null; } return reload(REVIEW_CONNECTION); }).then(value => {
      if (!value) return;
      // open the record named by the address, e.g. /review/prospectus/<document>/<question>
      const target = parseReviewPath(window.location.pathname);
      const linked = itemForTarget(value.items, target);
      if (target.kind === 'prospectus' && linked) setLinkedQuestion(target.question);
      if (target.kind !== 'home' && !linked) setMessage('That link does not match a record in this packet, so the first record is open.');
      const first = linked ?? value.items[0];
      setSelected(first?.id ?? '');
      if (first && !linked) window.history.replaceState(null, '', reviewPath(targetForItem(first)));
    }).catch(error => {
      // the intake tool starts with nothing open: point to Intake instead of the generic launch-link error
      if (error instanceof ReviewError && isNoPacketError(error.message, error.status)) setNoPacket(true);
      else setError(error.message);
    });
  }, [reload]);

  // back and forward move between records
  useEffect(() => {
    function follow() {
      const linked = state && itemForTarget(state.items, parseReviewPath(window.location.pathname));
      if (linked && linked.id !== selected) choose(linked.id, false);
    }
    window.addEventListener('popstate', follow);
    return () => window.removeEventListener('popstate', follow);
  });

  useEffect(() => { if (item) setDraft(draftFor(item)); }, [item]);
  useEffect(() => {
    function protect(event: BeforeUnloadEvent) { if (leaveWarning(dirty, !!pending.current)) { event.preventDefault(); event.returnValue = ''; } }
    window.addEventListener('beforeunload', protect);
    return () => window.removeEventListener('beforeunload', protect);
  }, [dirty]);

  function choose(id: string, record = true) {
    const gate = switchGate(dirty, !!pending.current);
    if (gate === 'blocked') { setError('Resolve the previous save before changing items.'); return; }
    if (gate === 'confirm' && !window.confirm('Discard the unsaved edits for this item?')) return;
    const next = state?.items.find(row => row.id === id);
    setDraft(next ? draftFor(next) : null);
    setSourceFocus(null); setLinkedQuestion(undefined);
    setSelected(id); setMessage(''); setError('');
    if (next && record) window.history.pushState(null, '', reviewPath(targetForItem(next)));
  }
  // the record list is memoized: hand it one stable callback that always runs the latest choose()
  const chooseRef = useRef(choose);
  chooseRef.current = choose;
  const onChoose = useCallback((id: string) => chooseRef.current(id), []);

  async function save() {
    if (!connection || !state || !item || !draft || busy) return;
    setError(''); setMessage('');
    try {
      if (!pending.current) {
        if (!draft.reason.trim()) {
          setError(NOTHING_TO_SAVE);
          focusByLabel('Review reason');
          return;
        }
        pending.current = buildPayload(item, draft, state.revision, crypto.randomUUID());
      }
      setBusy(true);
      await request(connection, '/api/decision', { method: 'POST', body: JSON.stringify(pending.current) });
      pending.current = null;
      await reload(connection); setMessage('Saved with its source identity and history.');
    } catch (error) {
      if (error instanceof ReviewError && error.status < 500) {
        pending.current = null;
        setError(error.status === 409 ? `${error.message} Your draft is retained; reopen the item after reloading.` : error.message);
      } else {
        setError(pending.current ? 'The save response was lost. Your draft is retained. Retry the same save to check its outcome.' : (error as Error).message);
      }
    } finally { setBusy(false); }
  }

  async function exportDecisions() {
    if (!connection) return;
    const route = item?.prospectus_candidate ? '/api/prospectus/' + encodeURIComponent(item.document_id) + '/export' : '/api/export';
    try { download(await (await request(connection, route, { method: 'POST' })).json(), 'review-decisions.json'); }
    catch (error) { setError((error as Error).message); }
  }
  async function showHistory() {
    if (!connection) return;
    try { setHistory(await (await request(connection, '/api/history')).json()); }
    catch (error) { setError((error as Error).message); }
  }
  function feedbackSaved(receipt: FeedbackReceipt) {
    setState(current => current ? { ...current, revision: Math.max(current.revision, receipt.revision),
      feedback: [...(current.feedback ?? []).filter(row => row.operation_id !== receipt.feedback.operation_id), receipt.feedback] } : current);
    setMessage('Missing-content note saved as pending feedback. Your field review is unchanged.');
  }
  function closeMenu(refocus = false) {
    if (!menu.current) return;
    menu.current.open = false;
    if (refocus) menu.current.querySelector('summary')?.focus();
  }
  useEffect(() => {
    function outside(event: PointerEvent) { if (menu.current?.open && !menu.current.contains(event.target as Node)) menu.current.open = false; }
    document.addEventListener('pointerdown', outside);
    return () => document.removeEventListener('pointerdown', outside);
  }, []);
  function togglePanel(next: 'help' | 'library') {
    setPanel(current => current === next ? null : next);
    if (next === 'library') setLibraryOpened(true);
  }

  // a fresh decision answers the 'nothing to save' hint, so clear it as soon as the reviewer edits
  const editDraft: typeof setDraft = useCallback(value => { setError(current => current === NOTHING_TO_SAVE ? '' : current); setDraft(value); }, []);
  const fit = !!state && !!connection && !noPacket;
  const hasAssistance = !!state?.items.some(row => row.fields.some(field => field.assistance));
  const notices = <>
    {error && <div className="notice error" role="alert">{error}
      {pending.current && <Button variant="outline" disabled={busy} onClick={() => void save()}>Retry save</Button>}
      {connection && !pending.current && error !== NOTHING_TO_SAVE && <Button variant="outline" onClick={() => {
        if (dirty && !window.confirm('Discard your unsaved draft and load the saved decisions?')) return;
        void reload(connection).catch(e => setError(e.message));
      }}>Reload packet</Button>}
    </div>}
    {message && <p className="notice success" role="status">{message}</p>}
  </>;
  const showPaneNotices = fit && !!item && !item.prospectus_candidate && !!draft;

  return <main className={fit ? 'review-workspace rw-fit' : 'review-workspace'} id="review-main">
    {state && !noPacket && <a className="skip-link" href="#source-review">Skip to the source record</a>}
    <div className="rw-bar"><h1 className="page-title">{item?.prospectus_candidate ? 'Prospectus' : 'Documents'}</h1>
      {state && <span className="muted" title={`Reviewer: ${state.researcher}`}>{state.items.length} records</span>}
      {state?.items.some(row => row.fields.length > 0) && <span className="muted" role="status" aria-label="AI assistance">{hasAssistance
        ? 'AI notes appear beside fields. You decide what to save.' : 'AI suggestions are not included in this packet.'}</span>}
      {state && !noPacket && <details className="rw-menu" ref={menu} onKeyDown={event => { if (event.key === 'Escape') closeMenu(true); }}>
        <summary>Tools</summary>
        <div className="rw-menu-list">
          <button type="button" aria-pressed={panel === 'help'} onClick={() => { closeMenu(); togglePanel('help'); }}>How to review</button>
          <button type="button" aria-pressed={panel === 'library'} onClick={() => { closeMenu(); togglePanel('library'); }}>Browse knowledge</button>
          <button type="button" onClick={() => { closeMenu(); void showHistory(); }}>Saved reviews</button>
          <button type="button" onClick={() => { closeMenu(); void exportDecisions(); }}>Download my reviews</button>
        </div>
      </details>}
    </div>
    {panel === 'help' && state && <section className="rw-panel" id="rw-help" aria-label="How to review">
      <ul>
        <li>Pick a record. Its source regions are outlined on the PDF page.</li>
        <li>For each field choose Matches, Fix text or Unclear, then Save.</li>
        <li>{state.source_basis?.candidate_review
          ? 'These are local copies of selected undergraduate records, saved apart from the frozen baseline. They cover selected material, not every page.'
          : 'This older packet is read-only reference. Prepare a new packet to review candidates.'}</li>
        <li>Opening, saving or downloading a review does not change the chatbot.</li>
      </ul></section>}
    {state && !noPacket && <section className="rw-panel" id="rw-library" aria-label="Existing knowledge" hidden={panel !== 'library'}>
      {libraryOpened && <KnowledgeLibrary />}</section>}
    {!showPaneNotices && notices}
    {noPacket ? <>
      <section className="library-intro" aria-label="Review status"><p role="status"><strong>No upload is open for review.</strong>{' '}
        <a href="/review/intake">Open one on Intake</a> to compare it with its PDF.</p></section>
      <section className="library-section" aria-labelledby="library-heading"><h2 id="library-heading">Existing knowledge</h2>
        <p className="muted">Documents stored in each knowledge source. Pick one to read its chunks beside the source page.</p>
        <KnowledgeLibrary headingId="library-heading" /></section></>
      : !state || !connection ? <section className="empty"><h2>Open a local review packet</h2>
      <p role="status">{error ? 'The review records could not be loaded. If this is a new review session, open the launch link printed by the local review command.' : 'Loading the source documents and review records…'}</p></section>
      : <div className="work-area rw-grid">
        <RecordList items={state.items} documents={state.documents} selected={selected} onChoose={onChoose}/>
        {!item || !draft ? <section className="empty">Choose a record from the list.</section>
          : item.prospectus_candidate ? <div className="rw-prospectus"><ProspectusReview key={item.document_id} connection={connection} documentId={item.document_id}
            initialQuestion={linkedQuestion}
            onQuestion={qid => window.history.replaceState(null, '', reviewPath(targetForItem(item, qid)))}/></div>
          : <div className="evidence-area"><SourceViewer key={item.document_id} connection={connection} item={item} document={sourceDoc}
            relatedItems={relatedItems} focus={sourceFocus}
            revision={state.revision} feedback={state.feedback} onFeedbackSaved={feedbackSaved} reviewBusy={busy || !!pending.current}/>
            <DecisionPane key={item.id} item={item} items={state.items} documents={state.documents} draft={draft} setDraft={editDraft}
              packetId={state.packet_id} revision={state.revision}
              dirty={dirty} busy={busy || !!pending.current} notices={notices} onSave={() => void save()}
              onShowSource={(itemId, page) => setSourceFocus({ itemId, page })} onOpenRecord={onChoose}/>
          </div>}
      </div>}
    {history && <ReviewHistory entries={history} items={state?.items ?? []} documents={state?.documents ?? []} onClose={() => setHistory(null)}/>}
  </main>;
}

function focusByLabel(label: string) {
  document.querySelector<HTMLInputElement>(`[aria-label="${label}"]`)?.focus();
}
