'use client';

import { useCallback, useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { request } from '@/lib/api';
import { buildPayload, withheldReason, type BuildPlan, type ClaimDraft } from '@/lib/intake';
import { REVIEW_CONNECTION } from '@/lib/review-state';

const blankClaim = (): ClaimDraft => ({ subject_id: '', claim: '', finding: 'visible_fields', field_refs: [], basis_reading_id: '' });
function message(error: unknown) { return error instanceof Error ? error.message : 'The request failed.'; }

export function IntakeBuild({ uploadId }: { uploadId: string }) {
  const [plan, setPlan] = useState<BuildPlan | null>(null), [error, setError] = useState('');
  const [selected, setSelected] = useState<string[]>([]), [subjects, setSubjects] = useState<Record<string, string>>({});
  const [claims, setClaims] = useState<ClaimDraft[]>([blankClaim()]);
  const [problems, setProblems] = useState<string[]>([]), [saved, setSaved] = useState(''), [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setError('');
    try { setPlan(await (await request(REVIEW_CONNECTION, '/api/intake/build-plan')).json()); }
    catch (failure) { setPlan(null); setError(message(failure)); }
  }, []);
  useEffect(() => { void load(); }, [load, uploadId]);

  function patchClaim(index: number, patch: Partial<ClaimDraft>) {
    setClaims(rows => rows.map((row, i) => i === index ? { ...row, ...patch } : row));
  }
  function toggle(list: string[], value: string) { return list.includes(value) ? list.filter(v => v !== value) : [...list, value]; }

  async function save() {
    if (!plan || busy) return;
    setSaved(''); setError('');
    const result = buildPayload(plan, { selected, subjects, claims });
    setProblems(result.errors);
    if (!result.payload) return;
    setBusy(true);
    try {
      const reply: { path: string; revision: number } = await (await request(REVIEW_CONNECTION, '/api/intake/build-metadata',
        { method: 'POST', body: JSON.stringify(result.payload) })).json();
      setSaved(`Saved build metadata for review revision ${reply.revision}.`);
    } catch (failure) { setError(message(failure)); }
    finally { setBusy(false); }
  }

  const ready = plan?.readings.filter(row => row.ready) ?? [];
  return <section className="intake-section" aria-labelledby="build-heading">
    <h2 id="build-heading">3. Build form for the open upload</h2>
    <p className="muted">Fill this after reviewing. Saving another review decision makes the saved form stale: save the form again afterwards.</p>
    <div><Button variant="outline" onClick={() => void load()}>Reload readings</Button></div>
    <div aria-live="polite">
      {error && <p className="notice error" role="alert">{error}</p>}
      {saved && <p className="notice success" role="status">{saved}</p>}
    </div>
    {plan && <>
      <fieldset><legend>Readings</legend>
        {plan.readings.map(row => <div key={row.reading_id} className="intake-reading">
          <label className="inline"><input type="checkbox" disabled={!row.ready} checked={selected.includes(row.reading_id) && row.ready}
            onChange={() => setSelected(list => toggle(list, row.reading_id))} />
            <span><code>{row.reading_id}</code> · {row.ready ? 'ready' : `pending fields: ${row.pending_fields.join(', ')}`}</span></label>
          {row.ready && selected.includes(row.reading_id) && <label>Subject id for this reading
            <input value={subjects[row.reading_id] ?? ''} onChange={event => setSubjects(map => ({ ...map, [row.reading_id]: event.target.value }))} /></label>}
        </div>)}
        {!plan.readings.length && <p className="muted">This packet has no readings.</p>}
      </fieldset>
      {!!plan.withheld_items?.length && <section aria-label="Withheld items"><h3>Withheld from the build</h3>
        <ul>{plan.withheld_items.map(row => <li key={row.item_id}><code>{row.item_id}</code>: {withheldReason(row.reason)}</li>)}</ul></section>}
      <fieldset><legend>Claim reviews</legend>
        {claims.map((claim, index) => {
          const basis = ready.find(row => row.reading_id === claim.basis_reading_id);
          return <div key={index} className="intake-claim"><h3>Claim {index + 1}</h3>
            <label>Subject id<input value={claim.subject_id} onChange={event => patchClaim(index, { subject_id: event.target.value })} /></label>
            <label>Claim<Textarea rows={2} value={claim.claim} onChange={event => patchClaim(index, { claim: event.target.value })} /></label>
            <label>Finding<select value={claim.finding} onChange={event => patchClaim(index, { finding: event.target.value, field_refs: [] })}>
              <option value="visible_fields">Visible in the chosen fields</option>
              <option value="not_stated_in_selected_fields">Not stated in the selected fields</option></select></label>
            <label>Basis reading<select value={claim.basis_reading_id} onChange={event => patchClaim(index, { basis_reading_id: event.target.value, field_refs: [] })}>
              <option value="">Choose a reading</option>{ready.map(row => <option key={row.reading_id} value={row.reading_id}>{row.reading_id}</option>)}</select></label>
            {claim.finding === 'visible_fields' && <fieldset><legend>Fields that show the claim</legend>
              {!basis && <p className="muted">Choose the basis reading first.</p>}
              {basis?.fields.map(name => <label className="inline" key={name}>
                <input type="checkbox" checked={claim.field_refs.includes(name)}
                  onChange={() => patchClaim(index, { field_refs: toggle(claim.field_refs, name) })} />{name}</label>)}</fieldset>}
            {claims.length > 1 && <div><Button variant="outline" onClick={() => setClaims(rows => rows.filter((_, i) => i !== index))}>Remove claim {index + 1}</Button></div>}
          </div>;
        })}
        <div><Button variant="outline" onClick={() => setClaims(rows => [...rows, blankClaim()])}>Add another claim</Button></div>
      </fieldset>
      {!!problems.length && <div className="notice error" role="alert"><ul>{problems.map(text => <li key={text}>{text}</li>)}</ul></div>}
      <div><Button disabled={busy} onClick={() => void save()}>{busy ? 'Saving…' : 'Save build form'}</Button></div>
    </>}
  </section>;
}
