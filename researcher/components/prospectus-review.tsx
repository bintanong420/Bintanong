'use client';

import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { SourceViewer, type HighlightPages } from '@/components/source-viewer';
import { download, request, ReviewError } from '@/lib/api';
import { answerPayload, filterQuestions, groupBySection, nextAfter, progressLine, prospectusFieldLabel, statusLines, step,
  warningCount, type ProspectusState } from '@/lib/prospectus-review';
import type { Connection, ReviewItem } from '@/lib/review-state';

type Question = { qid: string; kind: string; prompt: string; pages: number[]; decided: boolean;
  section: { sid: string; title: string; health: string }; reference: Record<string, unknown>; editable_fields: string[];
  other_allowed: boolean; flags: { severity: string; message: string }[];
  proposals: { letter: string; field: string; old: string; new: string; note: string }[] };
type View = { question: Question; course: unknown; cells: unknown[]; boxes: HighlightPages };

const CHOICES = [
  { value: 'yes', label: 'Yes, the displayed reading matches the original' },
  { value: 'no', label: 'No, hold this reading' },
  { value: 'other', label: 'Other: record an explicit correction' },
];

export function ProspectusReview({ connection, documentId }: { connection: Connection; documentId: string }) {
  const [questions, setQuestions] = useState<Question[]>([]), [view, setView] = useState<View | null>(null);
  const [mode, setMode] = useState('attention'), [choice, setChoice] = useState(''), [filter, setFilter] = useState('');
  const [edits, setEdits] = useState<Record<string, string>>({}), [reason, setReason] = useState('');
  const [error, setError] = useState(''), [message, setMessage] = useState(''), [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<ProspectusState>();
  const pending = useRef<Record<string, unknown> | null>(null);
  const base = '/api/prospectus/' + encodeURIComponent(documentId);
  const q = view?.question, locked = busy || !!pending.current;
  const visible = filterQuestions(questions, filter), index = visible.findIndex(item => item.qid === q?.qid);

  async function openQuestion(qid: string) {
    const data: View = await (await request(connection, base + '/question?qid=' + encodeURIComponent(qid))).json();
    setView(data); setChoice(''); setEdits({}); setReason('');
  }
  // reload the queue, then open `pick(queue)`; by default stay on the current question when it is still queued
  async function reload(pick?: (queue: Question[]) => string | null) {
    const data = await (await request(connection, base + '/queue?mode=' + mode)).json();
    const queue: Question[] = data.questions;
    setQuestions(queue); setStatus(data.state);
    const target = pick ? pick(queue) : (queue.find(item => item.qid === q?.qid) ?? queue[0])?.qid;
    if (target) await openQuestion(target); else setView(null);
  }
  useEffect(() => { void reload().catch(e => setError(e.message)); }, [connection, documentId, mode]);

  function go(qid: string | null) {
    if (!qid || qid === q?.qid || locked) return;
    if ((choice || reason || Object.keys(edits).length) && !window.confirm('Discard this unsaved answer?')) return;
    void openQuestion(qid).catch(e => setError(e.message));
  }

  async function save() {
    if (!view || !choice || busy) return;
    setError(''); setMessage(''); setBusy(true);
    try {
      pending.current ??= answerPayload(view.question, choice, edits, reason);
      const saved = view.question.qid;
      const result = await (await request(connection, base + '/answer', { method: 'POST', body: JSON.stringify(pending.current) })).json();
      pending.current = null;
      // like the original reviewer: move on after every save, staying inside the current filter when possible
      await reload(queue => nextAfter(filterQuestions(queue, filter), saved) ?? nextAfter(queue, saved));
      setMessage(`Saved ${saved}: ${result.written} new decision records; ${result.skipped} unchanged records.`);
    } catch (error) {
      if (error instanceof ReviewError && error.status < 500) pending.current = null;
      setError(pending.current ? 'The save outcome is uncertain. Retry the same answer; your input is retained.' : (error as Error).message);
    } finally { setBusy(false); }
  }
  async function exportCandidate() {
    try { download(await (await request(connection, base + '/export', { method: 'POST' })).json(), 'reviewed-prospectus-candidate.json'); }
    catch (error) { setError((error as Error).message); }
  }
  function applyProposal(field: string, value: string) {
    setChoice('other'); setEdits({ ...edits, [field]: value });
    setMessage(`Proposal copied into ${prospectusFieldLabel(field)}. Save to record it.`);
  }

  const warnings = warningCount(status);
  const sourceItem: ReviewItem | null = q ? { id: documentId + ':' + q.qid, document_id: documentId,
    title: q.prompt, audience: 'unresolved', companions: [], findings: [], fields: [{ name: 'course',
      original_value: q.reference, reviewed_value: q.reference, source_blank: false, decision: 'pending',
      locator: { physical_pages: q.pages, field: 'course' }, spans: [] }] } : null;

  return <section className="prospectus-workspace" aria-label="Prospectus course review">
    <div className="prospectus-toolbar"><h2>Prospectus review</h2>
      <label>Question order<select value={mode} disabled={locked} onChange={event => setMode(event.target.value)}>
        <option value="attention">Needs attention first</option><option value="print">Printed order</option></select></label>
      <Button variant="outline" onClick={() => void exportCandidate()}>Export corrected candidate</Button>
      <span className="muted" role="status">{progressLine(status)}</span>
    </div>
    {status && <details className="prospectus-status" open={warnings > 0}>
      <summary className={warnings ? 'hold' : undefined}>Review status{warnings ? ` · ${warnings} warning${warnings > 1 ? 's' : ''}` : ' · no warnings'}</summary>
      <ul>{statusLines(status).map(line => <li key={line}>{line}</li>)}</ul>
    </details>}
    {error && <p className="notice error" role="alert">{error}{pending.current && <Button onClick={() => void save()}>Retry answer</Button>}</p>}
    {message && <p className="notice success" role="status">{message}</p>}

    <div className="prospectus-layout">
      <aside className="queue prospectus-queue" aria-label="Prospectus questions">
        <label>Filter questions<input type="search" value={filter} placeholder="Code, title or question id"
          onChange={event => setFilter(event.target.value)}/></label>
        <nav>{!status ? <p className="muted">Loading questions…</p> : visible.length === 0
          ? <p className="muted">{questions.length ? 'No question matches the filter.' : 'Every question in this queue has an answer.'}</p>
          : groupBySection(visible).map(({ section, items }) => <details key={section.sid} open>
            <summary>{section.title} <span className={`health health-${section.health}`}>{section.health}</span>
              <span className="muted"> · {items.filter(item => item.decided).length}/{items.length}</span></summary>
            {items.map(item => <button type="button" className="queue-item" key={item.qid} disabled={locked}
              aria-current={item.qid === q?.qid ? 'true' : undefined} onClick={() => go(item.qid)}>
              {item.prompt}<span>{item.qid}{item.decided ? ' · Reviewed' : ''}</span></button>)}
          </details>)}</nav>
      </aside>

      {!q || !view || !sourceItem
        ? <p className="empty">{status ? 'No questions remain in this queue. Choose Printed order to inspect every recorded question.' : 'Loading questions…'}</p>
        : <div className="prospectus-main">
          <div className="review-actions">
            <Button variant="outline" disabled={locked || index <= 0} onClick={() => go(step(visible, q.qid, -1))}>Previous</Button>
            <p>{index >= 0 ? `Question ${index + 1} of ${visible.length}` : 'Outside the current filter'} · {q.section.title}</p>
            <Button variant="outline" disabled={locked || index < 0 || index >= visible.length - 1} onClick={() => go(step(visible, q.qid, 1))}>Next</Button>
          </div>
          <div className="evidence-area"><SourceViewer connection={connection} item={sourceItem} legacyBoxes={view.boxes}/>
            <section className="decision-pane"><h2>{q.prompt}</h2>
              <p className="muted">{q.section.title} · {q.kind.replaceAll('_', ' ')} · section {q.section.health}{q.decided ? ' · already reviewed' : ''}</p>
              {q.flags.map((flag, i) => <p className="notice hold" key={i}>{flag.severity}: {flag.message}</p>)}
              <dl className="related-fields original-text">{Object.entries(q.reference).filter(([name]) => name !== 'courses').map(([name, value]) =>
                <div key={name}><dt>{prospectusFieldLabel(name)}</dt><dd>{value === null || value === '' ? '(blank)' : String(value)}</dd></div>)}</dl>
              {q.proposals.map(proposal => <div className="companion" key={proposal.letter}>
                <p>Proposal {proposal.letter}: {prospectusFieldLabel(proposal.field)} “{proposal.old}” → “{proposal.new}”. {proposal.note}</p>
                <Button variant="outline" disabled={!q.other_allowed || locked} onClick={() => applyProposal(proposal.field, proposal.new)}>
                  Use proposal {proposal.letter}</Button></div>)}
              <form onSubmit={event => { event.preventDefault(); void save(); }}><fieldset disabled={locked}>
                <legend>Record your reading of the original</legend>
                {CHOICES.filter(option => option.value !== 'other' || q.other_allowed).map(option =>
                  <label className="checkbox-label" key={option.value}>
                    <input type="radio" name="prospectus-answer" value={option.value} checked={choice === option.value}
                      onChange={() => setChoice(option.value)}/>{option.label}</label>)}
                {!q.other_allowed && <p className="muted">Other is not available here: there is nothing to type for this question.</p>}
                {choice === 'other' && q.editable_fields.map(name => <label key={name}>{prospectusFieldLabel(name)}
                  <Textarea value={edits[name] ?? ''} rows={name === 'prerequisites_raw' ? 2 : 1}
                    onChange={event => setEdits({ ...edits, [name]: event.target.value })}/>
                </label>)}
                {choice === 'other' && q.kind === 'prerequisite' && <p className="muted">Leave the prerequisites blank to record that none are printed.</p>}
                <label>{q.kind === 'section_confirm' ? 'Note (optional)' : 'Reason'}
                  <Textarea value={reason} onChange={event => setReason(event.target.value)} rows={3}/></label>
                <Button type="submit" disabled={!choice}>{busy ? 'Saving…' : 'Save and go to next'}</Button>
              </fieldset></form>
              <details><summary>Extracted course and source cells</summary><pre>{JSON.stringify({ course: view.course, cells: view.cells }, null, 2)}</pre></details>
              <p className="muted">Corrections remain candidate data. Source review does not establish curriculum approval or activation.</p>
            </section>
          </div>
        </div>}
    </div>
  </section>;
}
