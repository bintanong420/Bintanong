'use client';

import { useCallback, useEffect, useId, useRef, useState } from 'react';
import { Field } from '@/components/intake-status';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { request } from '@/lib/api';
import { buildPayload, buildProblems, withheldReason, type BuildPlan, type BuildProblem, type ClaimDraft } from '@/lib/intake';
import { REVIEW_CONNECTION } from '@/lib/review-state';

type Row = { uid: number; draft: ClaimDraft };
type ClaimField = 'claim' | 'subject' | 'finding' | 'basis' | 'fields';
const blankClaim = (): ClaimDraft => ({ subject_id: '', claim: '', finding: 'visible_fields', field_refs: [], basis_reading_id: '' });
function message(error: unknown) { return error instanceof Error ? error.message : 'The request failed.'; }
function toggle(list: string[], value: string) { return list.includes(value) ? list.filter(v => v !== value) : [...list, value]; }

function claimError(problems: BuildProblem[], index: number, field: ClaimField) {
  const found = problems.find(p => p.scope === 'claim' && p.index === index && p.field === field);
  return found?.message.replace(/^Claim \d+: /, '').replace(/^./, c => c.toUpperCase());
}

export function IntakeBuild({ uploadId }: { uploadId: string }) {
  const [plan, setPlan] = useState<BuildPlan | null>(null), [error, setError] = useState(''), [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string[]>([]), [subjects, setSubjects] = useState<Record<string, string>>({});
  const nextUid = useRef(2);
  const [rows, setRows] = useState<Row[]>([{ uid: 1, draft: blankClaim() }]);
  const [removed, setRemoved] = useState<{ row: Row; index: number } | null>(null);
  const [attempted, setAttempted] = useState(false), [saved, setSaved] = useState(''), [busy, setBusy] = useState(false);
  const claimsHeading = useRef<HTMLHeadingElement>(null), summary = useRef<HTMLDivElement>(null);
  const uid = useId();

  const load = useCallback(async () => {
    setError(''); setLoading(true);
    try { setPlan(await (await request(REVIEW_CONNECTION, '/api/intake/build-plan')).json()); }
    catch (failure) { setPlan(null); setError(message(failure)); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void load(); }, [load, uploadId]);

  function patchClaim(uidValue: number, patch: Partial<ClaimDraft>) {
    setRows(list => list.map(row => row.uid === uidValue ? { ...row, draft: { ...row.draft, ...patch } } : row));
  }
  function addClaim() { setRows(list => [...list, { uid: nextUid.current++, draft: blankClaim() }]); setRemoved(null); }
  function removeClaim(index: number) {
    setRemoved({ row: rows[index], index });
    setRows(list => list.filter((_, i) => i !== index));
    claimsHeading.current?.focus();  // the removed claim's controls are gone, so keep keyboard focus on the list
  }
  function undoRemove() {
    if (!removed) return;
    setRows(list => { const copy = [...list]; copy.splice(Math.min(removed.index, copy.length), 0, removed.row); return copy; });
    setRemoved(null);
  }

  const form = { selected, subjects, claims: rows.map(row => row.draft) };
  // after the first save attempt the checks run live, so each message disappears as soon as its field is fixed
  const problems = attempted && plan ? buildProblems(plan, form) : [];

  async function save() {
    if (!plan || busy) return;
    setSaved(''); setError(''); setAttempted(true);
    const result = buildPayload(plan, form);
    if (!result.payload) { setTimeout(() => summary.current?.focus(), 0); return; }
    setBusy(true);
    try {
      const reply: { path: string; revision: number } = await (await request(REVIEW_CONNECTION, '/api/intake/build-metadata',
        { method: 'POST', body: JSON.stringify(result.payload) })).json();
      setSaved(`Saved build metadata for review revision ${reply.revision}.`);
    } catch (failure) { setError(message(failure)); }
    finally { setBusy(false); }
  }

  const ready = plan?.readings.filter(row => row.ready) ?? [], pending = plan?.readings.filter(row => !row.ready) ?? [];
  const assigned = [...new Set(selected.map(id => (subjects[id] ?? '').trim()).filter(Boolean))];
  const selectionProblem = problems.find(p => p.scope === 'selection')?.message;
  const claimsProblem = problems.find(p => p.scope === 'claims')?.message;
  const baseId = (name: string) => `${uid}-${name}`;

  return <section className="intake-section" id="build" aria-labelledby="build-heading">
    <div className="section-head"><span className="section-number" aria-hidden="true">4</span>
      <div><h2 id="build-heading">Build form for the open upload</h2>
        <p className="muted">Fill this after reviewing. Pick the readings that are ready, name the subject each one is about, then record the claims.</p></div></div>
    <p className="notice hold"><span><strong>Saving a review decision makes a saved form stale.</strong> After any later decision on the review page, save this form again.</span></p>
    <div className="toolbar"><Button variant="outline" disabled={loading} onClick={() => void load()}>{loading ? 'Loading readings…' : 'Reload readings'}</Button></div>
    <div aria-live="polite">
      {error && <p className="notice error" role="alert"><span><strong>That did not work.</strong> {error}</span></p>}
      {saved && <p className="notice success" role="status"><span>{saved} Nothing has been approved or activated.</span></p>}
      {removed && <p className="notice" role="status"><span>Claim {removed.index + 1} removed.</span><Button variant="outline" size="sm" onClick={undoRemove}>Undo</Button></p>}
    </div>
    {loading && !plan && <div role="status" aria-busy="true"><p className="muted"><span className="spinner" aria-hidden="true" /> Loading readings…</p>
      <div className="intake-upload" aria-hidden="true"><span className="skeleton skeleton-title" /><span className="skeleton" /><span className="skeleton skeleton-short" /></div></div>}
    {!loading && !plan && !error && <div className="empty-state"><h3>No readings to show</h3><p className="muted">Reload to ask the review server for this packet’s readings.</p></div>}

    {plan && <>
      <div className="build-group">
        <h3>Readings that are ready ({ready.length})</h3>
        {selectionProblem && <p className="field-error">{selectionProblem}</p>}
        {!plan.readings.length && <div className="empty-state"><p className="muted">This packet has no readings, so there is nothing to build.</p></div>}
        {!!plan.readings.length && !ready.length && <p className="muted">No reading is ready yet. See the pending readings below.</p>}
        <ul className="plain-list">{ready.map(row => {
          const checked = selected.includes(row.reading_id);
          const problem = problems.find(p => p.scope === 'reading' && p.readingId === row.reading_id)?.message;
          const subjectId = baseId('subject-' + row.reading_id);
          return <li key={row.reading_id} className={`reading-card${checked ? ' is-selected' : ''}`}>
            <label className="inline"><input type="checkbox" checked={checked} onChange={() => setSelected(list => toggle(list, row.reading_id))} />
              <span><code>{row.reading_id}</code> <span className="muted">{row.fields.length} {row.fields.length === 1 ? 'field' : 'fields'}</span></span></label>
            {checked && <Field id={subjectId} label="Subject id for this reading" hint="The record this reading is about." error={problem?.replace(/^Enter/, 'Enter')}>{described =>
              <input id={subjectId} value={subjects[row.reading_id] ?? ''} autoComplete="off"
                aria-describedby={described} aria-invalid={problem ? true : undefined}
                onChange={event => setSubjects(map => ({ ...map, [row.reading_id]: event.target.value }))} />}</Field>}
          </li>;
        })}</ul>
      </div>

      {!!pending.length && <details className="build-group">
        <summary>Not ready yet ({pending.length})</summary>
        <p className="muted">These readings still have fields waiting on a review decision. They cannot be selected until every field is settled.</p>
        <ul className="plain-list">{pending.map(row => <li key={row.reading_id} className="reading-card is-pending">
          <p><code>{row.reading_id}</code></p><p className="muted">Waiting on {row.pending_fields.length} {row.pending_fields.length === 1 ? 'field' : 'fields'}: {row.pending_fields.join(', ')}</p></li>)}</ul>
      </details>}

      {!!plan.withheld_items?.length && <details className="build-group" open>
        <summary>Withheld from the build ({plan.withheld_items.length})</summary>
        <ul className="plain-list">{plan.withheld_items.map(row => <li key={row.item_id} className="reading-card is-pending">
          <p><code>{row.item_id}</code></p><p className="muted">{withheldReason(row.reason)}</p></li>)}</ul>
      </details>}

      <div className="build-group">
        <h3 ref={claimsHeading} tabIndex={-1}>Claim reviews ({rows.length})</h3>
        {claimsProblem && <p className="field-error">{claimsProblem}</p>}
                {rows.map((row, index) => {
          const claim = row.draft, basis = ready.find(r => r.reading_id === claim.basis_reading_id), key = baseId('c' + row.uid);
          const err = (field: ClaimField) => claimError(problems, index, field);
          return <fieldset key={row.uid} className="claim-card"><legend>Claim {index + 1}</legend>
            <Field id={key + '-claim'} label="Claim" hint="One statement the chosen fields support, or do not state." error={err('claim')}>{described =>
              <Textarea id={key + '-claim'} rows={2} value={claim.claim} aria-describedby={described} aria-invalid={err('claim') ? true : undefined}
                onChange={event => patchClaim(row.uid, { claim: event.target.value })} />}</Field>
            <div className="field-row">
              <Field id={key + '-subject'} label="Subject" hint="Chosen from the subjects you assigned to readings above; picking a basis reading fills it in." error={err('subject')}>{described =>
                <select id={key + '-subject'} value={claim.subject_id} aria-describedby={described} aria-invalid={err('subject') ? true : undefined}
                  onChange={event => patchClaim(row.uid, { subject_id: event.target.value })}>
                  <option value="">{assigned.length ? 'Choose a subject' : 'Assign a subject to a reading first'}</option>
                  {assigned.map(value => <option key={value} value={value}>{value}</option>)}</select>}</Field>
              <Field id={key + '-basis'} label="Basis reading" error={err('basis')}>{described =>
                <select id={key + '-basis'} value={claim.basis_reading_id} aria-describedby={described} aria-invalid={err('basis') ? true : undefined}
                  onChange={event => { const id = event.target.value, own = (subjects[id] ?? '').trim();
                    patchClaim(row.uid, { basis_reading_id: id, field_refs: [], ...(own && selected.includes(id) ? { subject_id: own } : {}) }); }}>
                  <option value="">Choose a reading</option>
                  {ready.map(r => <option key={r.reading_id} value={r.reading_id}>{r.reading_id}{selected.includes(r.reading_id) ? '' : ' (not selected)'}</option>)}</select>}</Field>
            </div>
            <Field id={key + '-finding'} label="Finding" error={err('finding')}>{described =>
              <select id={key + '-finding'} value={claim.finding} aria-describedby={described} aria-invalid={err('finding') ? true : undefined}
                onChange={event => patchClaim(row.uid, { finding: event.target.value, field_refs: [] })}>
                <option value="visible_fields">Visible in the chosen fields</option>
                <option value="not_stated_in_selected_fields">Not stated in the selected fields</option></select>}</Field>
            {claim.finding === 'visible_fields' && <fieldset className="field-group" aria-describedby={err('fields') ? key + '-fields-error' : undefined}>
              <legend>Fields that show the claim</legend>
              {!basis && <p className="muted">Choose the basis reading first, then its fields appear here.</p>}
              {basis && <div className="check-grid">{basis.fields.map(name => <label className="inline" key={name}>
                <input type="checkbox" checked={claim.field_refs.includes(name)}
                  onChange={() => patchClaim(row.uid, { field_refs: toggle(claim.field_refs, name) })} />{name}</label>)}</div>}
              {err('fields') && <p className="field-error" id={key + '-fields-error'}>{err('fields')}</p>}
            </fieldset>}
            {rows.length > 1 && <div><Button type="button" variant="outline" size="sm" onClick={() => removeClaim(index)}>Remove claim {index + 1}</Button></div>}
          </fieldset>;
        })}
        <div><Button type="button" variant="outline" onClick={addClaim}>Add another claim</Button></div>
      </div>

      {!!problems.length && <div className="notice error" role="alert" tabIndex={-1} ref={summary}>
        <div><p><strong>{problems.length} {problems.length === 1 ? 'thing needs' : 'things need'} fixing before this can be saved:</strong></p>
          <ul>{problems.map(problem => <li key={problem.message}>{problem.message}</li>)}</ul></div></div>}
      <div className="form-actions"><Button disabled={busy} onClick={() => void save()}>{busy && <span className="spinner" aria-hidden="true" />}{busy ? 'Saving…' : 'Save build form'}</Button>
        <p className="muted">Saving records metadata only. It does not approve or activate anything.</p></div>
    </>}
  </section>;
}
