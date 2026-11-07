// Prospectus review helpers, matching the original prospectus_review_gui (static/review.js) behavior.

const FIELD_LABELS: Record<string, string> = {
  course_code: 'Course code', course_title: 'Course title', code: 'Course code', title: 'Course title', term: 'Year and semester', lecture_units: 'Lecture units',
  lab_units: 'Lab units', total_units: 'Total units', prerequisites_raw: 'Prerequisites as printed',
};

export function prospectusFieldLabel(name: string) {
  return FIELD_LABELS[name] ?? name.replaceAll('_', ' ');
}

type AnswerQuestion = { qid: string; kind: string; editable_fields: string[] };

export function answerPayload(question: AnswerQuestion, choice: string, edits: Record<string, string>, text: string) {
  const sent: Record<string, string> = {};
  if (choice === 'other') {
    // an empty prerequisite is a real answer ("none"), so a prerequisite question always sends it;
    // elsewhere an empty box means "unchanged"
    for (const name of question.editable_fields) {
      const value = edits[name] ?? '';
      if (value.trim() || question.kind === 'prerequisite') sent[name] = value;
    }
  }
  const section = question.kind === 'section_confirm';
  return { qid: question.qid, choice, edits: sent, proposals: [], reason: section ? '' : text, note: section ? text : '' };
}

type QueueQuestion = { qid: string; prompt: string; section: { sid: string; title: string; health: string } };

// the question after qid in the queue as it stands after the save, wrapping round; never qid itself (a No stays open)
export function nextAfter<Q extends QueueQuestion>(queue: Q[], qid: string) {
  const ids = queue.map(q => q.qid), index = ids.indexOf(qid), start = index < 0 ? 0 : index + 1;
  return [...ids.slice(start), ...ids.slice(0, start)].find(id => id !== qid) ?? null;
}

export function step<Q extends QueueQuestion>(queue: Q[], qid: string | undefined, delta: number) {
  if (!queue.length) return null;
  const index = queue.findIndex(q => q.qid === qid);
  return queue[index < 0 ? 0 : Math.min(queue.length - 1, Math.max(0, index + delta))].qid;
}

export function filterQuestions<Q extends QueueQuestion>(queue: Q[], text: string) {
  const needle = text.trim().toLowerCase();
  return needle ? queue.filter(q => `${q.qid} ${q.prompt}`.toLowerCase().includes(needle)) : queue;
}

export function groupBySection<Q extends QueueQuestion>(queue: Q[]) {
  const groups = new Map<string, { section: Q['section']; items: Q[] }>();
  for (const q of queue) {
    if (!groups.has(q.section.sid)) groups.set(q.section.sid, { section: q.section, items: [] });
    groups.get(q.section.sid)!.items.push(q);
  }
  return [...groups.values()];
}

export type ProspectusState = {
  progress: { decided: number; questions: number };
  approval_line: string;
  review_states: { name: string; word: string; meaning: string }[];
  source_verification: { health: string; pdf_checked: boolean };
  prerequisites: { questions: number; decided: number; unclassified_courses: number };
  content_review: { stale_entries: number; inapplicable_entries: number; invalid_entries: number };
  docling?: { warning: string | null };
};

export function statusLines(state: ProspectusState | undefined) {
  if (!state) return [];
  const source = state.source_verification, prereq = state.prerequisites, review = state.content_review;
  const lines = [state.approval_line, ...state.review_states.map(s => `${s.name}: ${s.word} (${s.meaning})`),
    `PDF text check: ${source.health}, ${source.pdf_checked ? 'PDF text checked' : 'PDF text not checked'}`];
  if (prereq.questions) lines.push(`prerequisite questions: ${prereq.decided} of ${prereq.questions} decided (Yes and Other never hold back content review; a No does)`);
  if (prereq.unclassified_courses) lines.push(`${prereq.unclassified_courses} courses have no prerequisite state (a candidate from before Phase C): no prerequisite question for them`);
  if (state.docling?.warning) lines.push('Docling JSON: ' + state.docling.warning);
  if (review.stale_entries || review.inapplicable_entries || review.invalid_entries) {
    lines.push(`ledger: ${review.stale_entries} stale, ${review.inapplicable_entries} for another PDF, ${review.invalid_entries} unreadable`);
  }
  return lines;
}

export function progressLine(state: Pick<ProspectusState, 'progress'> | undefined) {
  return state ? `${state.progress.decided} of ${state.progress.questions} questions decided` : 'Loading questions…';
}

// how many status lines need the reviewer's attention; drives the collapsed status summary
export function warningCount(state: ProspectusState | undefined) {
  if (!state) return 0;
  const source = state.source_verification, review = state.content_review;
  return Number(source.health !== 'clean' || !source.pdf_checked) + Number(!!state.docling?.warning)
    + Number(!!(review.stale_entries || review.inapplicable_entries || review.invalid_entries));
}
