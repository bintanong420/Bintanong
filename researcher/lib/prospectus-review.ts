// Prospectus review helpers, matching the original prospectus_review_gui (static/review.js) behavior.

const FIELD_LABELS: Record<string, string> = {
  course_code: 'Course code', course_title: 'Course title', term: 'Year and semester', lecture_units: 'Lecture units',
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

export type ProspectusState = {
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
