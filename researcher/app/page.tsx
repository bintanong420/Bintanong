'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { SourceViewer } from '@/components/source-viewer';
import { ProspectusReview } from '@/components/prospectus-review';
import { appearanceKey, appearanceValue, type Appearance } from '@/lib/appearance';
import { download, request, ReviewError } from '@/lib/api';
import { filterItems, parseConnection, type Connection, type Gap, type ReviewItem, type ReviewState } from '@/lib/review-state';

type Draft = { audience: string; reason: string; companions: string[]; gaps: string;
  fields: Record<string, { decision: string; text: string }> };

function text(value: unknown) { return typeof value === 'string' ? value : JSON.stringify(value, null, 2); }
function draftFor(row: ReviewItem): Draft {
  return { audience: row.audience, reason: row.reason ?? '', companions: row.companions,
    gaps: JSON.stringify(row.gaps ?? [], null, 2), fields: Object.fromEntries(row.fields.map(field =>
      [field.name, { decision: field.decision, text: text(field.reviewed_value) }])) };
}

export default function ReviewWorkspace() {
  const [connection, setConnection] = useState<Connection | null>(null);
  const [state, setState] = useState<ReviewState | null>(null), [selected, setSelected] = useState('');
  const [query, setQuery] = useState(''), [documentFilter, setDocumentFilter] = useState(''), [mode, setMode] = useState('all');
  const [draft, setDraft] = useState<Draft | null>(null), [busy, setBusy] = useState(false);
  const [error, setError] = useState(''), [message, setMessage] = useState('');
  const [history, setHistory] = useState<unknown[] | null>(null), [appearance, setAppearance] = useState<Appearance>('system');
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
    setSelected(id); setMessage(''); setError('');
  }

  async function save() {
    if (!connection || !state || !item || !draft || busy) return;
    setError(''); setMessage('');
    try {
      if (!pending.current) {
        const gaps: Gap[] = JSON.parse(draft.gaps);
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

  return <main className="review-workspace">
    <header className="app-header"><div><p className="wordmark">Bintanong <span>Knowledge review</span></p>
      <p className="muted">Local researcher workspace · Inactive candidates</p></div>
      <div className="header-actions"><span className="muted">{state?.researcher}</span>
        <label>Appearance<select value={appearance} onChange={event => setAppearance(appearanceValue(event.target.value))}>
          <option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option>
        </select></label>
        <Button variant="outline" disabled={!state} onClick={() => void showHistory()}>History</Button>
        <Button variant="outline" disabled={!state} onClick={() => void exportDecisions()}>Export decisions</Button>
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
    {!state || !connection ? <section className="empty"><h1>Open a local review packet</h1>
      <p>Use the launch link printed by the review command. The packet and access token stay on this computer.</p></section>
      : <div className="work-area">
        <aside className="queue" aria-label="Review queue"><div className="queue-heading"><h1>Review queue</h1>
          <span>{filtered.length} of {state.items.length}</span></div>
          <label>Search<Textarea rows={1} value={query} onChange={event => setQuery(event.target.value)} placeholder="Section or source wording" /></label>
          <label>Document<select value={documentFilter} onChange={event => setDocumentFilter(event.target.value)}>
            <option value="">All documents</option>{state.documents.map(doc => <option key={doc.id} value={doc.id}>{doc.title} · {doc.edition}</option>)}
          </select></label>
          <label>Review state<select value={mode} onChange={event => setMode(event.target.value)}>
            <option value="all">All items</option><option value="attention">Needs attention</option>
          </select></label>
          <nav aria-label="Source items">{filtered.map(row => <button key={row.id} className="queue-item" aria-current={selected === row.id ? 'true' : undefined}
            onClick={() => choose(row.id)}><strong>{row.title}</strong><span>{row.document_id} · {row.id.split(':').slice(1).join(':')}</span>
            <span className={row.findings.length ? 'status hold' : 'status'}>{row.audience === 'excluded' ? 'Excluded'
              : row.findings.length ? 'Source hold' : row.fields.every(f => ['accepted', 'corrected'].includes(f.decision)) && row.fields.length ? 'Transcription reviewed' : 'Pending review'}</span>
          </button>)}</nav>
          {!filtered.length && <p className="muted">No items match these filters.</p>}
        </aside>
        {!item || !draft ? <section className="empty">Choose an item from the queue.</section>
          : item.prospectus_candidate ? <ProspectusReview connection={connection} documentId={item.document_id}/>
          : <div className="evidence-area"><SourceViewer connection={connection} item={item} />
            <section className="decision-pane" aria-label="Extraction and review"><div className="pane-heading"><h2>{item.title}</h2>
              <span>{dirty ? 'Unsaved edits' : 'Saved state'}</span></div>
              {item.findings.map((finding, i) => <p key={i} className="notice hold">Source finding: {finding}. This finding remains attached to the evidence.</p>)}
              {!item.fields.length ? <p className="notice hold">This prospectus uses the course review workflow. Its questions require the prospectus review controls.</p>
              : <form onSubmit={event => { event.preventDefault(); void save(); }}>
                <fieldset disabled={busy || !!pending.current}><legend>Audience applicability</legend>
                  <label>Applies to<select aria-label="Audience applicability" value={draft.audience} onChange={event => setDraft({ ...draft, audience: event.target.value })}>
                    <option value="unresolved">Unresolved / mixed applicability</option><option value="undergraduate">Undergraduate-applicable</option><option value="excluded">Excluded audience or procedure</option>
                  </select></label>
                  {item.fields.map(field => <section className="field-review" key={field.name}>
                    <h3>{field.name}</h3><p className="muted">Original extracted value · pages {field.locator.physical_pages.join(', ') || 'unlocated'}</p>
                    <pre className="original-text">{text(field.original_value) || '(literal empty extraction)'}</pre>
                    {field.source_blank && <p className="notice hold">Recorded literal source blank. It must stay blank.</p>}
                    <label>Content decision<select aria-label={`${field.name} content decision`} value={draft.fields[field.name].decision}
                      onChange={event => setDraft({ ...draft, fields: { ...draft.fields, [field.name]: { ...draft.fields[field.name], decision: event.target.value } } })}>
                      <option value="pending">Not reviewed</option><option value="accepted">Accept original reading</option><option value="corrected">Correct extraction</option><option value="unresolved">Hold unresolved</option>
                    </select></label>
                    <label>Reviewed value<Textarea aria-label={`${field.name} reviewed value`} rows={4} value={draft.fields[field.name].text}
                      readOnly={field.source_blank} onChange={event => setDraft({ ...draft, fields: { ...draft.fields,
                        [field.name]: { decision: 'corrected', text: event.target.value } } })}/></label>
                  </section>)}
                  <label>Reason / source observation<Textarea aria-label="Review reason" required rows={3} value={draft.reason}
                    onChange={event => setDraft({ ...draft, reason: event.target.value })}/></label>
                  <label>Related blocks / required companions<select aria-label="Required companions" multiple size={4} value={draft.companions}
                    onChange={event => setDraft({ ...draft, companions: Array.from(event.target.selectedOptions, option => option.value) })}>
                    {state.items.filter(r => r.id !== item.id).map(row => <option key={row.id} value={row.id}>{row.document_id} · {row.title} · {row.id}</option>)}
                  </select></label>
                  {draft.companions.map(id => state.items.find(r => r.id === id)).filter(r => !!r).map(row => <section className="companion" key={row.id}>
                    <h3>{row.title}</h3><p className="muted">{row.document_id} · pages {row.fields.flatMap(f => f.locator.physical_pages).join(', ')}</p>
                    {row.fields.map(field => <pre key={field.name}>{text(field.original_value)}</pre>)}
                  </section>)}
                  <details><summary>Source gaps and affected claims</summary><p className="muted">Record issue, field_names, visible_text and affected_claims. Preserve original cutoffs and contradictions.</p>
                    <Textarea aria-label="Source gap records" rows={6} value={draft.gaps} onChange={event => setDraft({ ...draft, gaps: event.target.value })}/>
                  </details>
                  <Button type="submit" disabled={!draft.reason.trim()}>{busy ? 'Saving…' : 'Save review decision'}</Button>
                </fieldset>
              </form>}
              <details><summary>Recorded source geometry and extraction</summary><pre>{JSON.stringify(item, null, 2)}</pre></details>
            </section>
          </div>}
      </div>}
    {history && <aside className="history-panel" aria-label="Decision history"><div className="pane-heading"><h2>Decision history</h2>
      <Button variant="outline" onClick={() => setHistory(null)}>Close history</Button></div>
      {!history.length ? <p>No decisions have been saved.</p> : history.map((entry, i) => <pre key={i}>{JSON.stringify(entry, null, 2)}</pre>)}
    </aside>}
  </main>;
}
