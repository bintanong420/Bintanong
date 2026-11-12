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

export type UploadField = 'kind' | 'title' | 'edition' | 'office' | 'audience';

// One message per field, so the form can show each next to its input. Order matches the visible form order.
export function fieldErrors(fields: UploadFields): Partial<Record<UploadField, string>> {
  const errors: Partial<Record<UploadField, string>> = {};
  if (!(KINDS as readonly string[]).includes(fields.kind)) errors.kind = 'Choose a document kind.';
  if (!fields.title.trim()) errors.title = 'Enter the document title.';
  if (!fields.edition.trim()) errors.edition = 'Enter the edition or year.';
  const limited: [UploadField, string, string][] = [['title', 'Title', fields.title], ['edition', 'Edition', fields.edition],
    ['office', 'Office', fields.office], ['audience', 'Audience note', fields.audience]];
  for (const [key, name, value] of limited) {
    if (!errors[key] && value.trim().length > TEXT_LIMIT) errors[key] = `${name} must be at most ${TEXT_LIMIT} characters.`;
  }
  return errors;
}

export function validateUploadFields(fields: UploadFields) {
  const errors = fieldErrors(fields);
  const first = (['kind', 'title', 'edition', 'office', 'audience'] as const).find(key => errors[key]);
  return first ? errors[first]! : null;
}
export function uploadQuery(fields: UploadFields) {
  const query = new URLSearchParams({ kind: fields.kind, title: fields.title.trim(), edition: fields.edition.trim() });
  if (fields.office.trim()) query.set('office', fields.office.trim());
  if (fields.audience.trim()) query.set('audience', fields.audience.trim());
  return query.toString();
}

const LABELS: Record<string, string> = { running: 'Running', done: 'Done', failed: 'Failed',
  interrupted: 'Interrupted (the review server restarted while it ran)', not_started: 'Not started' };
export function prepareLabel(state: string) { return LABELS[state] ?? 'Unknown state'; }
export function shouldPoll(state: string | undefined) { return state === 'running'; }

// The prepare step ends by printing the packet as one JSON line; people read a count, not 64 hex digits.
function packetSummary(line: string) {
  if (!line.startsWith('{')) return null;
  try {
    const value = JSON.parse(line);
    if (!value || typeof value !== 'object' || typeof value.packet_id !== 'string') return null;
    const items = value.items ?? value.item_count;
    return typeof items === 'number' ? `Prepared: ${items} ${items === 1 ? 'item' : 'items'}` : 'Prepared: the review draft is written';
  } catch { return null; }
}

// Newest line worth reading in a raw Docling log: skips blanks, tqdm bars and warnings. The full log stays available untouched.
export function latestLogLine(lines: string[]) {
  for (const raw of [...lines].reverse()) {
    const line = packetSummary(raw.trim()) ?? raw.trim();
    if (!line || /\d+%\||it\/s|s\/it/.test(line) || /warn/i.test(line)) continue;
    return line.length > 160 ? line.slice(0, 157) + '...' : line;
  }
  return '';
}

export function formatBytes(bytes: number) {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 B';
  if (bytes < 1024) return `${Math.round(bytes)} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KiB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MiB`;
}

export function formatElapsed(ms: number) {
  const total = Number.isFinite(ms) && ms > 0 ? Math.floor(ms / 1000) : 0;
  const hours = Math.floor(total / 3600), minutes = Math.floor((total % 3600) / 60), seconds = total % 60;
  const two = (n: number) => String(n).padStart(2, '0');
  if (hours) return `${hours} h ${two(minutes)} min`;
  if (minutes) return `${minutes} min ${two(seconds)} s`;
  return `${seconds} s`;
}

export type StepStatus = 'done' | 'active' | 'todo' | 'failed' | 'blocked' | 'unknown';
export type PipelineStep = { key: 'upload' | 'prepare' | 'review' | 'build'; label: string; status: StepStatus; text: string };

// Where one upload sits in Upload -> Prepare -> Review -> Build. Every status carries words, not only a symbol.
export function pipelineSteps(prepareState: string | undefined, open: boolean,
    build?: Pick<BuildStatus, 'state' | 'package'>): PipelineStep[] {
  const prepare: Record<string, [StepStatus, string]> = { not_started: ['todo', 'Not started'], running: ['active', 'Running'],
    done: ['done', 'Done'], failed: ['failed', 'Failed'], interrupted: ['failed', 'Interrupted'] };
  const [prepareStatus, prepareText] = prepareState === undefined ? ['unknown', 'Checking'] : prepare[prepareState] ?? ['unknown', 'Unknown'];
  const prepared = prepareState === 'done';
  return [
    { key: 'upload', label: 'Upload', status: 'done', text: 'Uploaded' },
    { key: 'prepare', label: 'Prepare', status: prepareStatus as StepStatus, text: prepareText },
    { key: 'review', label: 'Review', ...(open ? { status: 'active' as const, text: 'Open for review' }
      : prepared ? { status: 'todo' as const, text: 'Ready to open' } : { status: 'blocked' as const, text: 'Waiting for Prepare' }) },
    { key: 'build', label: 'Build', ...buildStep(prepared, build) },
  ];
}

export type BuildStatus = { state: string; metadata_saved?: boolean; exit_code?: number; error?: string; log_tail?: string[];
  package?: { package_id: string; chunk_count: number } };
const BUILD_LABELS: Record<string, string> = { running: 'Running', done: 'Done', failed: 'Failed',
  interrupted: 'Interrupted (the review server restarted while it ran)', not_started: 'Not started' };
export function buildLabel(state: string) { return BUILD_LABELS[state] ?? 'Unknown state'; }
export function shouldPollBuild(state: string | undefined) { return state === 'running'; }
const chunks = (n: number) => `${n} ${n === 1 ? 'chunk' : 'chunks'}`;
export function buildSummary(build: Pick<BuildStatus, 'state' | 'package'> | undefined) {
  return build?.state === 'done' && build.package ? 'Built ' + chunks(build.package.chunk_count) : '';
}
export const INTERRUPTED_NOTE = 'This build was interrupted and may still be running. Make a new upload to build again.';
export const REBUILD_NOTE = 'Built. A rebuild with changed review decisions needs a new upload.';

// The server allows a build only once per upload (package_exists), and a retry only after a failure.
export function buildControl(prepared: boolean, build: Pick<BuildStatus, 'state'> | undefined):
    { kind: 'start' | 'retry' | 'running' | 'none'; label: string } {
  if (build?.state === 'running') return { kind: 'running', label: 'Building…' };
  // done and interrupted both offer nothing: after an interruption the old process may still be running
  if (build?.state === 'done' || build?.state === 'interrupted') return { kind: 'none', label: '' };
  if (build?.state === 'failed') return { kind: 'retry', label: 'Try the build again' };
  return { kind: 'start', label: 'Build chunks' };
}

// What the UI can know before the first build. Whether the readings and claims form was saved is only known to the server.
export function buildChecklist(prepared: boolean, formSaved?: boolean): { key: 'prepared' | 'form'; status: StepStatus; text: string }[] {
  return [{ key: 'prepared', status: prepared ? 'done' : 'blocked', text: prepared ? 'Prepared' : 'Not prepared yet: finish Prepare first' },
    formSaved === undefined ? { key: 'form', status: 'unknown', text: 'Checking whether the passages and claims form is saved' }
      : { key: 'form', status: formSaved ? 'done' : 'blocked', text: formSaved ? 'Passages and claims form saved' : 'Save the passages and claims form first' }];
}

// Why the Build button is off, in words; empty when it can run.
export function buildBlocker(prepared: boolean, formSaved: boolean | undefined, open = false) {
  if (!prepared) return 'Build is available once Prepare is done.';
  if (formSaved === undefined) return 'Checking whether the passages and claims form is saved.';
  if (formSaved) return '';
  return open ? 'Save the passages and claims form below first.' : 'Save the passages and claims form first (open this upload for review to fill it in).';
}

// The one thing to do next for an upload, from the same states the progress steps show.
export function nextStep({ prepare, open, build, formSaved }: { prepare: string | undefined; open?: boolean; build?: string; formSaved?: boolean }) {
  if (prepare === undefined) return 'Checking where this upload stands.';
  if (prepare === 'not_started') return 'Next: prepare it with Docling.';
  if (prepare === 'running') return 'Next: wait for Docling to finish. This page checks on its own.';
  if (prepare === 'failed' || prepare === 'interrupted') return 'Prepare stopped. Upload the PDF again to retry.';
  if (build === 'done') return 'Next: read the new chunks in Knowledge.';
  if (build === 'running') return 'Next: wait for the build to finish.';
  if (build === 'failed') return 'The build failed. Read the build log below, then try again.';
  if (!open) return 'Next: open it for review.';
  return formSaved ? 'Next: build chunks.' : 'Next: check the passages you trust, save the form, then build chunks.';
}

export function passageLabel(row: { reading_id: string; preview?: string }) {
  return row.preview ? '“' + row.preview + '”' : 'Passage ' + row.reading_id;
}
export function opensMetadataForm(code: string | undefined) { return code === 'metadata_missing'; }

function buildStep(prepared: boolean, build: Pick<BuildStatus, 'state' | 'package'> | undefined):
    { status: StepStatus; text: string } {
  if (build?.state === 'running') return { status: 'active', text: 'Building' };
  if (build?.state === 'failed' || build?.state === 'interrupted') return { status: 'failed', text: build.state === 'failed' ? 'Failed' : 'Interrupted' };
  if (build?.state === 'done') return { status: 'done', text: buildSummary(build) || 'Built' };
  return prepared ? { status: 'todo', text: 'Ready to build' } : { status: 'blocked', text: 'Needs Prepare' };
}

// The review API answers 422 with this text while no upload is open; the home page turns it into a link.
export function isNoPacketError(message: string, status: number) {
  return status === 422 && message === 'Open an upload for review first.';
}

const WITHHELD: Record<string, string> = {
  prior_review_reference: 'A prior review is shown here for reference only; it cannot be rebuilt here.',
  missing_policy_fields_or_pages: 'It has no policy fields or no source pages, so it cannot be built.' };
export function withheldReason(reason: string) { return WITHHELD[reason] ?? reason; }

export type PlanReading = { reading_id: string; fields: string[]; pending_fields: string[]; ready: boolean; preview?: string };
export type BuildPlan = { packet_id?: string; revision?: number; metadata_saved?: boolean; readings: PlanReading[];
  withheld_items?: { item_id: string; reason: string }[] };
export type ClaimDraft = { subject_id: string; claim: string; finding: string; field_refs: string[]; basis_reading_id: string };
export type BuildForm = { selected: string[]; subjects: Record<string, string>; claims: ClaimDraft[] };
export type FieldRef = { reading_id: string; field_name: string };
export type BuildPayload = { reading_ids: string[]; assignments: { reading_id: string; subject_id: string }[];
  claim_reviews: (Omit<ClaimDraft, 'field_refs'> & { field_refs: FieldRef[] })[] };

export const FINDINGS = ['visible_fields', 'not_stated_in_selected_fields'] as const;

export type BuildProblem =
  | { scope: 'selection' | 'claims'; message: string }
  | { scope: 'reading'; readingId: string; message: string }
  | { scope: 'claim'; index: number; field: 'claim' | 'subject' | 'finding' | 'basis' | 'fields'; message: string };

// Same checks as before, but each problem says where it belongs so the form can show it inline.
export function buildProblems(plan: Pick<BuildPlan, 'readings'>, form: BuildForm): BuildProblem[] {
  const problems: BuildProblem[] = [];
  const byId = new Map(plan.readings.map(row => [row.reading_id, row]));
  const ids = plan.readings.filter(row => row.ready && form.selected.includes(row.reading_id)).map(row => row.reading_id);
  if (!ids.length) problems.push({ scope: 'selection', message: 'Select at least one passage that is ready.' });
  const assignments = ids.map(id => ({ reading_id: id, subject_id: (form.subjects[id] ?? '').trim() }));
  for (const row of assignments) if (!row.subject_id) problems.push({ scope: 'reading', readingId: row.reading_id, message: `Enter a topic for ${passageLabel(byId.get(row.reading_id) ?? row)}.` });
  const subjects = new Set(assignments.map(row => row.subject_id).filter(Boolean));
  if (!form.claims.length) problems.push({ scope: 'claims', message: 'Add at least one claim review.' });
  form.claims.forEach((draft, index) => {
    const label = `Claim ${index + 1}`;
    const add = (field: 'claim' | 'subject' | 'finding' | 'basis' | 'fields', text: string) =>
      problems.push({ scope: 'claim', index, field, message: `${label}: ${text}` });
    if (!draft.claim.trim()) add('claim', 'enter the claim text.');
    if (!subjects.has(draft.subject_id.trim())) add('subject', 'its topic must be one you gave to a selected passage.');
    if (!(FINDINGS as readonly string[]).includes(draft.finding)) add('finding', 'choose a finding.');
    const basis = byId.get(draft.basis_reading_id);
    if (!basis || !ids.includes(draft.basis_reading_id)) add('basis', 'the basis passage must be a selected one.');
    if (draft.finding === 'visible_fields') {
      if (!draft.field_refs.length) add('fields', 'choose the field(s) that show the claim.');
      else if (basis && draft.field_refs.some(name => !basis.fields.includes(name))) add('fields', 'a chosen field is not in the basis passage.');
    }
  });
  return problems;
}

export function buildPayload(plan: Pick<BuildPlan, 'readings'>, form: BuildForm):
    { payload: BuildPayload; errors: never[] } | { payload: null; errors: string[] } {
  const problems = buildProblems(plan, form);
  if (problems.length) return { payload: null, errors: problems.map(problem => problem.message) };
  const ids = plan.readings.filter(row => row.ready && form.selected.includes(row.reading_id)).map(row => row.reading_id);
  const assignments = ids.map(id => ({ reading_id: id, subject_id: (form.subjects[id] ?? '').trim() }));
  const claims = form.claims.map((draft): BuildPayload['claim_reviews'][number] => ({
    subject_id: draft.subject_id.trim(), claim: draft.claim.trim(), finding: draft.finding,
    field_refs: draft.finding === 'visible_fields' ? draft.field_refs.map(field_name => ({ reading_id: draft.basis_reading_id, field_name })) : [],
    basis_reading_id: draft.basis_reading_id }));
  return { payload: { reading_ids: ids, assignments, claim_reviews: claims }, errors: [] };
}

const FINDING_LABELS: Record<string, string> = { visible_fields: 'The text shows this', not_stated_in_selected_fields: 'The text does not say this' };
export const findingLabel = (value: string) => FINDING_LABELS[value] ?? value;

