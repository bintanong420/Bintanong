'use client';

import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { SourceViewer, type HighlightPages } from '@/components/source-viewer';
import { download, request, ReviewError } from '@/lib/api';
import type { Connection, ReviewItem } from '@/lib/review-state';

type Question = { qid: string; kind: string; prompt: string; pages: number[]; decided: boolean;
  section: { title: string; health: string }; reference: Record<string, unknown>; editable_fields: string[];
  other_allowed: boolean; flags: { severity: string; message: string }[];
  proposals: { letter: string; field: string; old: string; new: string; note: string }[] };
type View = { question: Question; course: unknown; cells: unknown[]; boxes: HighlightPages };

export function ProspectusReview({ connection, documentId }: { connection: Connection; documentId: string }) {
  const [questions, setQuestions] = useState<Question[]>([]), [view, setView] = useState<View | null>(null);
  const [mode, setMode] = useState('attention'), [choice, setChoice] = useState('');
  const [edits, setEdits] = useState<Record<string, string>>({}), [reason, setReason] = useState('');
  const [error, setError] = useState(''), [message, setMessage] = useState(''), [busy, setBusy] = useState(false);
  const pending = useRef<Record<string, unknown> | null>(null);
  const base = '/api/prospectus/' + encodeURIComponent(documentId);

  async function openQuestion(qid: string) {
    const data: View = await (await request(connection, base + '/question?qid=' + encodeURIComponent(qid))).json();
    setView(data); setChoice(''); setEdits({}); setReason('');
  }
  async function reload() {
    const data = await (await request(connection, base + '/queue?mode=' + mode)).json();
    setQuestions(data.questions);
    const next = data.questions.find((q: Question) => q.qid === view?.question.qid) ?? data.questions[0];
    if (next) await openQuestion(next.qid); else setView(null);
  }
  useEffect(() => { void reload().catch(e => setError(e.message)); }, [connection, documentId, mode]);

  async function save() {
    if (!view || !choice || busy) return;
    setError(''); setMessage(''); setBusy(true);
    try {
      pending.current ??= { qid: view.question.qid, choice, edits: choice === 'other' ? edits : {}, proposals: [],
        reason: view.question.kind === 'section_confirm' ? '' : reason,
        note: view.question.kind === 'section_confirm' ? reason : '' };
      const result = await (await request(connection, base + '/answer', { method: 'POST', body: JSON.stringify(pending.current) })).json();
      pending.current = null; await reload();
      setMessage(`Saved ${result.written} new decision records; ${result.skipped} unchanged records.`);
    } catch (error) {
      if (error instanceof ReviewError && error.status < 500) pending.current = null;
      setError(pending.current ? 'The save outcome is uncertain. Retry the same answer; your input is retained.' : (error as Error).message);
    } finally { setBusy(false); }
  }
  async function exportCandidate() {
    try { download(await (await request(connection, base + '/export', { method: 'POST' })).json(), 'reviewed-prospectus-candidate.json'); }
    catch (error) { setError((error as Error).message); }
  }
  const q = view?.question;
  const sourceItem: ReviewItem | null = q ? { id: documentId + ':' + q.qid, document_id: documentId,
    title: q.prompt, audience: 'unresolved', companions: [], findings: [], fields: [{ name: 'course',
      original_value: q.reference, reviewed_value: q.reference, source_blank: false, decision: 'pending',
      locator: { physical_pages: q.pages, field: 'course' }, spans: [] }] } : null;
  return <section className="prospectus-workspace" aria-label="Prospectus course review">
    <div className="prospectus-toolbar"><h2>Prospectus review</h2>
      <label>Question order<select value={mode} disabled={busy || !!pending.current} onChange={event => setMode(event.target.value)}>
        <option value="attention">Needs attention</option><option value="print">Printed order</option></select></label>
      <Button variant="outline" onClick={() => void exportCandidate()}>Export corrected candidate</Button>
      <span className="muted">{questions.length} questions · Existing source-bound prospectus ledger</span>
    </div>
    {error && <p className="notice error" role="alert">{error}{pending.current && <Button onClick={() => void save()}>Retry answer</Button>}</p>}
    {message && <p className="notice success" role="status">{message}</p>}
    <nav className="question-navigation" aria-label="Prospectus questions">{questions.map(question => <Button variant={q?.qid === question.qid ? 'secondary' : 'outline'}
      size="sm" key={question.qid} disabled={busy || !!pending.current} onClick={() => {
        if ((choice || reason || Object.keys(edits).length) && !window.confirm('Discard this unsaved answer?')) return;
        void openQuestion(question.qid).catch(e => setError(e.message));
      }}>{question.qid}{question.decided ? ' · Reviewed' : ''}</Button>)}</nav>
    {!q || !view || !sourceItem ? <p className="empty">No questions remain in this queue. Use Printed order to inspect all recorded questions.</p>
    : <div className="evidence-area"><SourceViewer connection={connection} item={sourceItem} legacyBoxes={view.boxes}/>
      <section className="decision-pane"><h2>{q.prompt}</h2><p className="muted">{q.section.title} · {q.kind} · {q.section.health}</p>
        {q.flags.map((flag, i) => <p className="notice hold" key={i}>{flag.severity}: {flag.message}</p>)}
        <pre className="original-text">{JSON.stringify(q.reference, null, 2)}</pre>
        {q.proposals.map(proposal => <div className="companion" key={proposal.letter}>
          <p>{proposal.field}: “{proposal.old}” → “{proposal.new}”. {proposal.note}</p>
          <Button variant="outline" disabled={!q.other_allowed || busy || !!pending.current} onClick={() => {
            setChoice('other'); setEdits({ ...edits, [proposal.field]: proposal.new });
          }}>Use proposal {proposal.letter}</Button></div>)}
        <form onSubmit={event => { event.preventDefault(); void save(); }}><fieldset disabled={busy || !!pending.current}>
          <legend>Record your reading of the original</legend>
          <label>Answer<select required aria-label="Prospectus answer" value={choice} onChange={event => setChoice(event.target.value)}>
            <option value="">Choose an answer</option><option value="yes">Yes, the displayed reading matches</option>
            <option value="no">No, hold the reading</option>{q.other_allowed && <option value="other">Other: explicit correction</option>}
          </select></label>
          {choice === 'other' && q.editable_fields.map(name => <label key={name}>{name.replaceAll('_', ' ')}
            <Textarea value={edits[name] ?? ''} onChange={event => setEdits({ ...edits, [name]: event.target.value })}/>
          </label>)}
          <label>Reason / note<Textarea value={reason} onChange={event => setReason(event.target.value)} rows={3}/></label>
          <Button type="submit" disabled={!choice}>{busy ? 'Saving…' : 'Save prospectus answer'}</Button>
        </fieldset></form>
        <details><summary>Extracted course and source cells</summary><pre>{JSON.stringify({ course: view.course, cells: view.cells }, null, 2)}</pre></details>
        <p className="muted">Corrections remain candidate data. Source review does not establish curriculum approval or activation.</p>
      </section>
    </div>}
  </section>;
}
