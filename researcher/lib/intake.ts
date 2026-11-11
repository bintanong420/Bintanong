// Pure logic for the Intake page. The server stays authoritative: these checks only save a round trip.

export const MAX_UPLOAD_BYTES = 128 * 1024 * 1024;
export const TEXT_LIMIT = 300;
export const KINDS = ['handbook', 'charter'] as const;
export type UploadKind = (typeof KINDS)[number];

export type UploadFields = { kind: string; title: string; edition: string; office: string; audience: string };

export function checkUploadFile(file: { name: string; type: string; size: number } | null | undefined) {
  if (!file) return 'Choose a PDF file first.';
  if (file.type !== 'application/pdf' && !(file.type === '' && /\.pdf$/i.test(file.name))) return 'Only PDF files can be uploaded.';
  if (file.size === 0) return 'That file is empty.';
  if (file.size > MAX_UPLOAD_BYTES) return 'That file is over 128 MiB, which is the upload limit.';
  return null;
}

export function validateUploadFields(fields: UploadFields) {
  if (!(KINDS as readonly string[]).includes(fields.kind)) return 'Choose a document kind.';
  if (!fields.title.trim()) return 'Enter the document title.';
  if (!fields.edition.trim()) return 'Enter the edition or year.';
  for (const [name, value] of [['Title', fields.title], ['Edition', fields.edition], ['Office', fields.office], ['Audience note', fields.audience]]) {
    if (value.trim().length > TEXT_LIMIT) return `${name} must be at most ${TEXT_LIMIT} characters.`;
  }
  return null;
}

export function uploadQuery(fields: UploadFields) {
  const query = new URLSearchParams({ kind: fields.kind, title: fields.title.trim(), edition: fields.edition.trim() });
  if (fields.office.trim()) query.set('office', fields.office.trim());
  if (fields.audience.trim()) query.set('audience', fields.audience.trim());
  return query.toString();
}

const LABELS: Record<string, string> = { running: 'Running', done: 'Finished', failed: 'Failed',
  interrupted: 'Interrupted (the review server restarted while it ran)', not_started: 'Not started' };
export function prepareLabel(state: string) { return LABELS[state] ?? 'Unknown state'; }
export function shouldPoll(state: string | undefined) { return state === 'running'; }

// The review API answers 422 with this text while no upload is open; the home page turns it into a link.
export function isNoPacketError(message: string, status: number) {
  return status === 422 && message === 'Open an upload for review first.';
}

const WITHHELD: Record<string, string> = {
  prior_review_reference: 'A prior review is shown here for reference only; it cannot be rebuilt here.',
  missing_policy_fields_or_pages: 'It has no policy fields or no source pages, so it cannot be built.' };
export function withheldReason(reason: string) { return WITHHELD[reason] ?? reason; }

export type PlanReading = { reading_id: string; fields: string[]; pending_fields: string[]; ready: boolean };
export type BuildPlan = { packet_id?: string; revision?: number; readings: PlanReading[];
  withheld_items?: { item_id: string; reason: string }[] };
export type ClaimDraft = { subject_id: string; claim: string; finding: string; field_refs: string[]; basis_reading_id: string };
export type BuildForm = { selected: string[]; subjects: Record<string, string>; claims: ClaimDraft[] };
export type BuildPayload = { reading_ids: string[]; assignments: { reading_id: string; subject_id: string }[];
  claim_reviews: ClaimDraft[] };

export const FINDINGS = ['visible_fields', 'not_stated_in_selected_fields'] as const;

export function buildPayload(plan: Pick<BuildPlan, 'readings'>, form: BuildForm):
    { payload: BuildPayload; errors: never[] } | { payload: null; errors: string[] } {
  const errors: string[] = [];
  const byId = new Map(plan.readings.map(row => [row.reading_id, row]));
  // keep plan order; a pending or unknown reading is never sent
  const ids = plan.readings.filter(row => row.ready && form.selected.includes(row.reading_id)).map(row => row.reading_id);
  if (!ids.length) errors.push('Select at least one reading that is ready.');
  const assignments = ids.map(id => ({ reading_id: id, subject_id: (form.subjects[id] ?? '').trim() }));
  for (const row of assignments) if (!row.subject_id) errors.push(`Enter a subject id for reading ${row.reading_id}.`);
  const subjects = new Set(assignments.map(row => row.subject_id).filter(Boolean));
  if (!form.claims.length) errors.push('Add at least one claim review.');
  const claims = form.claims.map((draft, index): ClaimDraft => {
    const label = `Claim ${index + 1}`, claim = draft.claim.trim(), subject = draft.subject_id.trim();
    if (!claim) errors.push(`${label}: enter the claim text.`);
    if (!subjects.has(subject)) errors.push(`${label}: its subject must be one assigned to a selected reading.`);
    if (!(FINDINGS as readonly string[]).includes(draft.finding)) errors.push(`${label}: choose a finding.`);
    const basis = byId.get(draft.basis_reading_id);
    if (!basis || !ids.includes(draft.basis_reading_id)) errors.push(`${label}: the basis must be a selected reading.`);
    let refs: string[] = [];
    if (draft.finding === 'visible_fields') {
      refs = draft.field_refs;
      if (!refs.length) errors.push(`${label}: choose the field(s) that show the claim.`);
      else if (basis && refs.some(name => !basis.fields.includes(name))) errors.push(`${label}: a chosen field is not in the basis reading.`);
    }
    return { subject_id: subject, claim, finding: draft.finding, field_refs: refs, basis_reading_id: draft.basis_reading_id };
  });
  if (errors.length) return { payload: null, errors };
  return { payload: { reading_ids: ids, assignments, claim_reviews: claims }, errors: [] };
}
