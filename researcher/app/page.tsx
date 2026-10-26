'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { SourceViewer } from '@/components/source-viewer';
import { ProspectusReview } from '@/components/prospectus-review';
import { SourceGaps } from '@/components/source-gaps';
import { ReviewHistory, type HistoryEntry } from '@/components/review-history';
import { ReviewedValue } from '@/components/reviewed-value';
import { RelatedRecords } from '@/components/related-records';
import { appearanceKey, appearanceValue, type Appearance } from '@/lib/appearance';
import { download, request, ReviewError } from '@/lib/api';
import { fieldLabel, filterItems, parseConnection, readableValue, recordStatus, type Connection, type FeedbackReceipt, type Gap, type ReviewItem, type ReviewState } from '@/lib/review-state';

type Draft = { audience: string; reason: string; companions: string[]; gaps: Gap[];
  fields: Record<string, { decision: string; text: string }> };

function text(value: unknown) { return typeof value === 'string' ? value : JSON.stringify(value, null, 2); }
function draftFor(row: ReviewItem): Draft {
  return { audience: row.audience, reason: row.reason ?? '', companions: row.companions,
    gaps: row.gaps ?? [], fields: Object.fromEntries(row.fields.map(field =>
      [field.name, { decision: field.decision, text: text(field.reviewed_value) }])) };
}

export default function ReviewWorkspace() {
  const [connection, setConnection] = useState<Connection | null>(null);
  const [state, setState] = useState<ReviewState | null>(null), [selected, setSelected] = useState('');
  const [query, setQuery] = useState(''), [documentFilter, setDocumentFilter] = useState(''), [mode, setMode] = useState('all');
  const [draft, setDraft] = useState<Draft | null>(null), [busy, setBusy] = useState(false);
  const [error, setError] = useState(''), [message, setMessage] = useState('');
  const [history, setHistory] = useState<HistoryEntry[] | null>(null), [appearance, setAppearance] = useState<Appearance>('system');
  const [sourceFocus, setSourceFocus] = useState<{ itemId: string; page: number } | null>(null);
  const pending = useRef<Record<string, unknown> | null>(null);
  const item = state?.items.find(row => row.id === selected) ?? null;
  const dirty = !!item && !!draft && JSON.stringify(draftFor(item)) !== JSON.stringify(draft);
  const filtered = state ? filterItems(state.items, documentFilter, query, mode) : [];

  const reload = useCallback(async (c: Connection) => {
    const value: ReviewState = await (await request(c, '/api/state')).json();
    setState(value); return value;
  }, []);

  useEffect(() => {
    try {
      const fragment = window.location.hash || sessionStorage.getItem('bintanong-review-connection') || '';
      const c = parseConnection(fragment); setConnection(c);
      sessionStorage.setItem('bintanong-review-connection', fragment);
      window.history.replaceState(null, '', window.location.pathname);
      setAppearance(appearanceValue(localStorage.getItem(appearanceKey)));
      void reload(c).then(value => setSelected(value.items[0]?.id ?? '')).catch(error => setError(error.message));
    } catch (error) { setError((error as Error).message); }
  }, [reload]);

  useEffect(() => {
    document.documentElement.dataset.appearance = appearance;
    localStorage.setItem(appearanceKey, appearance);
  }, [appearance]);
  useEffect(() => { if (item) setDraft(draftFor(item)); }, [item]);
  useEffect(() => {
    function protect(event: BeforeUnloadEvent) { if (dirty || pending.current) { event.preventDefault(); event.returnValue = ''; } }
    window.addEventListener('beforeunload', protect);
    return () => window.removeEventListener('beforeunload', protect);
  }, [dirty]);

  function choose(id: string) {
    if (pending.current) { setError('Resolve the previous save before changing items.'); return; }
    if (dirty && !window.confirm('Discard the unsaved edits for this item?')) return;
    const next = state?.items.find(row => row.id === id);
    setDraft(next ? draftFor(next) : null);
    setSourceFocus(null);
    setSelected(id); setMessage(''); setError('');
  }

  async function save() {
    if (!connection || !state || !item || !draft || busy) return;
    setError(''); setMessage('');
    try {
      if (!pending.current) {
        const gaps = draft.gaps;
        const fields = Object.fromEntries(item.fields.map(field => [field.name, {
          decision: draft.fields[field.name].decision,
          value: typeof field.original_value === 'string' ? draft.fields[field.name].text : JSON.parse(draft.fields[field.name].text),
        }]));
        pending.current = { item_id: item.id, revision: state.revision, operation_id: crypto.randomUUID(),
          audience: draft.audience, reason: draft.reason, companions: draft.companions, gaps, fields };
      }
      setBusy(true);
      await request(connection, '/api/decision', { method: 'POST', body: JSON.stringify(pending.current) });
      pending.current = null;
      await reload(connection); setMessage('Decision saved with its source identity and history.');
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

  return <main className="review-workspace">
    <a className="skip-link" href="#source-review">Skip to the source record</a>
    <header className="app-header"><div><p className="wordmark">Bintanong <span>Knowledge review</span></p>
      <p className="muted">Read the source. Check the extracted text.</p></div>
      <div className="header-actions"><span className="muted">{state?.researcher}</span>
        <label>Appearance<select value={appearance} onChange={event => setAppearance(appearanceValue(event.target.value))}>
          <option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option>
        </select></label>
        <Button variant="outline" disabled={!state} onClick={() => void showHistory()}>Saved reviews</Button>
        <Button variant="outline" disabled={!state} onClick={() => void exportDecisions()}>Download my reviews</Button>
      </div>
    </header>
    {error && <div className="notice error" role="alert">{error}
      {pending.current && <Button variant="outline" disabled={busy} onClick={() => void save()}>Retry save</Button>}
      {connection && !pending.current && <Button variant="outline" onClick={() => {
        if (dirty && !window.confirm('Discard your unsaved draft and load the saved decisions?')) return;
        void reload(connection).catch(e => setError(e.message));
      }}>Reload packet</Button>}
    </div>}
    {message && <p className="notice success" role="status">{message}</p>}
    {state?.source_basis?.kind === 'reviewed_snapshot' && <section className="scope-note" aria-label="Source coverage">
      <h1>Handbook and Citizens’ Charter</h1><p>{state.items.length} source records. Compare the PDF, check each field, then save your review.</p>
      <details><summary>What am I reviewing?</summary><p>{state.source_basis.candidate_review
        ? 'These are local candidate copies of selected undergraduate records. Your changes are saved separately from the frozen baseline. Previous review evidence and known source problems stay attached.'
        : 'This older packet contains read-only references. Prepare a new packet to review local candidate copies.'}
        {' '}This covers selected material, not every page. Opening, saving or downloading a review does not change the chatbot.</p></details>
    </section>}
    {!state || !connection ? <section className="empty"><h1>Open a local review packet</h1>
      <p role="status">{connection ? 'Loading the source documents and review records…' : 'Open the launch link from your local review terminal to load the documents.'}</p></section>
      : <div className="work-area">
        <aside className="queue" aria-label="Review queue"><div className="queue-heading"><h2>Source records</h2>
          <span>{filtered.length} of {state.items.length}</span></div>
          <label>Find a topic or phrase<Textarea rows={1} value={query} onChange={event => setQuery(event.target.value)} placeholder="e.g. grade, enrollment, deadline" /></label>
          <label>Document<select value={documentFilter} onChange={event => setDocumentFilter(event.target.value)}>
            <option value="">All documents</option>{state.documents.map(doc => <option key={doc.id} value={doc.id}>{doc.title} · {doc.edition}</option>)}
          </select></label>
          <label>Show<select value={mode} onChange={event => setMode(event.target.value)}>
            <option value="all">All items</option><option value="attention">Needs attention</option>
            <option value="pending">Not fully checked</option><option value="held">Needs clarification</option>
            <option value="reviewed">Fields and audience checked</option><option value="excluded">Outside this study</option>
            <option value="source-problems">Known source problems</option>
          </select></label>
          <nav aria-label="Source items">{filtered.map(row => <button key={row.id} className="queue-item" aria-current={selected === row.id ? 'true' : undefined}
            onClick={() => choose(row.id)}><strong>{row.title}</strong><span>{state.documents.find(d => d.id === row.document_id)?.title} · PDF pages {Array.from(new Set(row.fields.flatMap(f => f.locator.physical_pages))).join(', ')}</span>
            <span className={row.findings.length || row.source_gaps?.length ? 'status hold' : 'status'}>{recordStatus(row)}</span>
          </button>)}</nav>
          {!filtered.length && <p className="muted">No items match these filters.</p>}
        </aside>
        {!item || !draft ? <section className="empty">Choose an item from the queue.</section>
          : item.prospectus_candidate ? <ProspectusReview connection={connection} documentId={item.document_id}/>
          : <div className="evidence-area"><SourceViewer key={item.document_id} connection={connection} item={item} document={state.documents.find(d => d.id === item.document_id)}
            relatedItems={state.items.filter(row => draft.companions.includes(row.id))} focus={sourceFocus}
            revision={state.revision} feedback={state.feedback} onFeedbackSaved={feedbackSaved} reviewBusy={busy || !!pending.current}/>
            <section id="source-review" tabIndex={-1} className="decision-pane" aria-label="Extraction and review"><div className="pane-heading"><h2>{item.title}</h2>
              <span>{dirty ? 'Unsaved edits' : item.reference_only ? 'Previously reviewed' : 'No unsaved changes'}</span></div>
              {item.reference_only && <p className="reference-note">This reading comes from the existing reviewed package. It is shown here for reference, with the original page beside it. Opening it does not record a new approval.</p>}
              {item.findings.map((finding, i) => <p key={i} className="notice hold">Needs checking: {fieldLabel(finding)}.</p>)}
              {!!item.source_gaps?.length && <section className="known-gaps" aria-label="Known source problems"><h3>Known source problems</h3>
                {item.source_gaps.map((gap, i) => <div key={i}><p><strong>{fieldLabel(gap.issue)}</strong></p>
                  <p>This affects: {gap.affected_claims.join('; ')}.</p>
                  <p className="source-reading">{Array.isArray(gap.visible_text) ? gap.visible_text.join('\n') : gap.visible_text}</p>
                  <p className="muted">The issue stays unresolved. Missing wording has not been filled in.</p></div>)}
              </section>}
              {item.reference_only ? <div className="reference-fields">{item.fields.map(field => <section className="field-review" key={field.name}>
                <h3>{fieldLabel(field.name)}</h3><p className="muted">PDF pages {field.locator.physical_pages.join(', ')}</p>
                <p className="source-reading">{field.source_blank ? 'Blank in the original document.' : readableValue(field.original_value)}</p>
              </section>)}</div> :
              !item.fields.length ? <p className="notice hold">This prospectus uses the course review workflow. Its questions require the prospectus review controls.</p>
              : <form onSubmit={event => { event.preventDefault(); void save(); }}>
                <fieldset disabled={busy || !!pending.current}><legend>Your review</legend>
                  <label>Who is this for?<select aria-label="Audience applicability" value={draft.audience} onChange={event => setDraft({ ...draft, audience: event.target.value })}>
                    <option value="unresolved">Not sure yet / mixed audience</option><option value="undergraduate">Undergraduate students</option><option value="excluded">Outside this study</option>
                  </select></label>
                  {item.fields.map(field => <section className="field-review" key={field.name}>
                    <h3>{fieldLabel(field.name)}</h3><p className="muted">Extracted text · PDF pages {field.locator.physical_pages.join(', ') || 'not yet located'}</p>
                    <p className="original-text source-reading">{readableValue(field.original_value) || '(literal empty extraction)'}</p>
                    {field.source_blank && <p className="notice hold">Recorded literal source blank. It must stay blank.</p>}
                    <label>Does this match the document?<select aria-label={`${field.name} content decision`} value={draft.fields[field.name].decision}
                      onChange={event => setDraft({ ...draft, fields: { ...draft.fields, [field.name]: { ...draft.fields[field.name], decision: event.target.value } } })}>
                      <option value="pending">Not checked yet</option><option value="accepted">Matches the document</option><option value="corrected">Fix the extracted text</option><option value="unresolved">Needs clarification</option>
                    </select></label>
                    <ReviewedValue field={field} value={draft.fields[field.name].text}
                      onChange={value => setDraft({ ...draft, fields: { ...draft.fields,
                        [field.name]: { decision: 'corrected', text: value } } })}/>
                  </section>)}
                  <label>What did you check or change?<Textarea aria-label="Review reason" required rows={3} value={draft.reason}
                    onChange={event => setDraft({ ...draft, reason: event.target.value })}/></label>
                  <RelatedRecords key={item.id} item={item} items={state.items} documents={state.documents} selected={draft.companions}
                    onChange={companions => setDraft({ ...draft, companions })} onShowSource={(itemId, page) => setSourceFocus({ itemId, page })}/>
                  <SourceGaps gaps={draft.gaps} fields={item.fields} onChange={gaps => setDraft({ ...draft, gaps })}/>
                  <Button type="submit" disabled={!draft.reason.trim()}>{busy ? 'Saving…' : 'Save my review'}</Button>
                </fieldset>
              </form>}
              {!!draft.companions.length && item.reference_only && <section aria-label="Related source records"><h3>Read together</h3>
                {draft.companions.map(id => state.items.find(r => r.id === id)).filter(r => !!r).map(row => <button
                  type="button" className="related-record" key={row.id} onClick={() => choose(row.id)}>{row.title}</button>)}
              </section>}
              <details><summary>Technical details</summary><pre>{JSON.stringify(item, null, 2)}</pre></details>
            </section>
          </div>}
      </div>}
    {history && <ReviewHistory entries={history} items={state?.items ?? []} documents={state?.documents ?? []} onClose={() => setHistory(null)}/>}
  </main>;
}
