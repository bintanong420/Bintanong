import type { StudentAnswer, StudentCurriculum, StudentScope } from "./student-contracts.ts";

export const clarificationCopy = {
  en: { title: "A little more detail", open: "Answer a few details", resume: "Continue clarification", next: "Continue", back: "Back", later: "Not now", review: "Review your reply", send: "Confirm and send", explanation: "Explain another way or add a detail", unknown: "I don't know", other: "Explain another way", choose: "Choose an answer", scope: "Which program and curriculum do you follow?", course: "Which course do you mean?", status: "Which courses have you passed or are you taking?", details: "What else should I know about your question?", hint: "Nothing is sent until you confirm. You can leave information unknown.", tooLong: "This reply is too long. Shorten your explanation, or close this prompt and edit your question.", retry: "Try loading curricula again", unavailable: "Curriculum choices are unavailable. You can explain or choose “I don't know”.", loading: "Loading reviewed curricula…", count: "Question", of: "of", prompt: "Your question", reply: "Your reply", unknownReply: "I do not know this detail." },
  fil: { title: "May kulang pang detalye", open: "Sagutin ang kulang na detalye", resume: "Ituloy ang paglilinaw", next: "Tuloy", back: "Balik", later: "Mamaya na", review: "Tingnan ang sagot mo", send: "Kumpirmahin at ipadala", explanation: "Ipaliwanag sa ibang paraan o magdagdag ng detalye", unknown: "Hindi ko alam", other: "Ipaliwanag sa ibang paraan", choose: "Pumili ng sagot", scope: "Ano ang program at curriculum mo?", course: "Anong course ang tinutukoy mo?", status: "Aling courses ang pasado ka na o kinukuha mo ngayon?", details: "Ano pa ang dapat kong malaman tungkol sa tanong mo?", hint: "Walang ipapadala hangga't hindi mo kinukumpirma. Puwedeng hindi mo alam ang sagot.", tooLong: "Masyadong mahaba ang sagot. Paikliin ang paliwanag, o isara ito at i-edit ang tanong mo.", retry: "Subukang i-load ulit ang curricula", unavailable: "Hindi available ang curriculum choices. Puwedeng magpaliwanag o piliin ang “Hindi ko alam”.", loading: "Nilo-load ang reviewed curricula…", count: "Tanong", of: "sa", prompt: "Tanong mo", reply: "Sagot mo", unknownReply: "Hindi ko alam ang detalyeng ito." },
  taglish: { title: "May kulang pang details", open: "Answer ang kulang na details", resume: "Continue ang clarification", next: "Continue", back: "Back", later: "Later na", review: "Review ang reply mo", send: "Confirm at send", explanation: "Explain another way o magdagdag ng detail", unknown: "Hindi ko alam", other: "Explain another way", choose: "Pumili ng answer", scope: "Anong program at curriculum mo?", course: "Anong course ang ibig mong sabihin?", status: "Aling courses ang passed na o currently taking mo?", details: "Anong details pa ang kailangan kong malaman sa question mo?", hint: "Walang ise-send hangga't hindi ka nag-confirm. Puwedeng unknown ang details.", tooLong: "Too long ang reply. Paikliin ang explanation, o close ito at i-edit ang question mo.", retry: "Try i-load ulit ang curricula", unavailable: "Unavailable ang curriculum choices. Puwedeng mag-explain o piliin ang “Hindi ko alam”.", loading: "Loading ang reviewed curricula…", count: "Question", of: "of", prompt: "Question mo", reply: "Reply mo", unknownReply: "Hindi ko alam ang detail na ito." },
};
export type ClarificationDrafts = Record<string, { value: string; explanation: string }>;
type Choice = { value: string; label: string; text: string; scope?: StudentScope };
export type ClarificationQuestion = { key: string; title: string; options: Choice[] };
export type SuppliedDetail = StudentScope & { key: string; code: string; label: string; text: string };
type Answer = Pick<StudentAnswer, "status" | "language" | "missingFields" | "clarification">;
export const copyForClarification = (language: StudentAnswer["language"]) => clarificationCopy[language === "unknown" ? "en" : language];

export function clarificationQuestions(answer: Answer, curricula: StudentCurriculum[]): ClarificationQuestion[] {
  if (answer.status !== "clarification_needed") return [];
  const copy = copyForClarification(answer.language), en = answer.language === "en" || answer.language === "unknown", fil = answer.language === "fil";
  const extra = [{ value: "unknown", label: copy.unknown, text: copy.unknownReply }, { value: "other", label: copy.other, text: "" }];
  const questions: ClarificationQuestion[] = [];
  if (answer.missingFields.some(f => f === "program" || f === "curriculum")) questions.push({ key: "scope", title: copy.scope, options: [
    ...curricula.map(c => ({ value: c.curriculumId, label: `${c.programName} · ${c.curriculumName}`,
      text: `${c.programName} · ${c.curriculumName}`, scope: { programId: c.programId, curriculumId: c.curriculumId } })), ...extra,
  ] });
  if (answer.missingFields.includes("course")) questions.push({ key: "course", title: copy.course, options: extra });
  for (const { code, kind } of answer.clarification?.courses ?? []) {
    const completion = kind === "completion";
    const key = `${kind}:${code}`;
    if (questions.some(q => q.key === key)) continue;
    questions.push({ key, title: en ? (completion ? `Have you passed ${code}?` : `Are you currently enrolled in ${code}?`)
      : completion ? (fil ? `Pasado ka na ba sa ${code}?` : `Passed ka na ba sa ${code}?`) : `Naka-enroll ka ba ngayon sa ${code}?`,
      options: [
        { value: completion ? "passed" : "enrolled", label: en ? (completion ? "Passed" : "Currently enrolled") : (completion ? (fil ? "Pasado na" : "Passed na") : "Naka-enroll ngayon"),
          text: en ? (completion ? `I have passed ${code}.` : `I am currently enrolled in ${code}.`) : (completion ? (fil ? `Pasado na ako sa ${code}.` : `Passed na ako sa ${code}.`) : `Naka-enroll ako ngayon sa ${code}.`) },
        { value: completion ? "not_passed" : "not_enrolled", label: en ? (completion ? "Not passed" : "Not enrolled") : (completion ? (fil ? "Hindi pa pasado" : "Hindi pa passed") : "Hindi naka-enroll"),
          text: en ? (completion ? `I have not passed ${code}.` : `I am not enrolled in ${code}.`) : (completion ? (fil ? `Hindi pa ako pasado sa ${code}.` : `Hindi pa ako passed sa ${code}.`) : `Hindi ako naka-enroll sa ${code}.`) },
        { ...extra[0], text: en ? `I do not know whether I ${completion ? "have passed" : "am enrolled in"} ${code}.`
          : `Hindi ko alam kung ${completion ? (fil ? "pasado na ako sa" : "passed na ako sa") : "naka-enroll ako sa"} ${code}.` }, extra[1],
      ] });
  }
  if (answer.missingFields.includes("course_status") && !answer.clarification?.courses.length) questions.push({ key: "course_status", title: copy.status, options: extra });
  return questions;
}

export function clarificationReply(original: string, answer: Answer, curricula: StudentCurriculum[], drafts: ClarificationDrafts): { text: string; scope: StudentScope | null } | null {
  const questions = clarificationQuestions(answer, curricula);
  if (!questions.length) return null;
  const lines = [original];
  const canonical = answer.clarification?.scope;
  let scope: StudentScope | null = canonical && curricula.some(c => c.programId === canonical.programId && c.curriculumId === canonical.curriculumId) ? canonical : null;
  for (const question of questions) {
    const draft = drafts[question.key], explanation = draft?.explanation.trim();
    const option = question.options.find(o => o.value === draft?.value);
    if ((!option && !explanation) || (draft?.value && !option) || (option?.value === "other" && !explanation)) return null;
    if (question.key === "scope") scope = option?.scope ?? null;
    lines.push([option?.text, explanation].filter(Boolean).join("\n"));
  }
  const text = `${lines[0]}\n\n${lines.slice(1).join("\n")}`;
  if (text.length > 8192 || new TextEncoder().encode(text).byteLength > 16384) throw new Error("clarification_too_long");
  return { text, scope };
}

export function sameScope(a: StudentScope | null, b: StudentScope | null) {
  return !!a && !!b && a.programId === b.programId && a.curriculumId === b.curriculumId;
}

export function confirmedDetails(answer: Answer, curricula: StudentCurriculum[], drafts: ClarificationDrafts, scope: StudentScope | null): SuppliedDetail[] {
  if (!scope || !curricula.some(c => sameScope(c, scope))) return [];
  const reply = clarificationReply("", answer, curricula, drafts);
  if (!reply || (reply.scope && !sameScope(reply.scope, scope))) return [];
  return clarificationQuestions(answer, curricula).flatMap(question => {
    const course = answer.clarification?.courses.find(c => question.key === `${c.kind}:${c.code}`);
    const draft = drafts[question.key], option = question.options.find(o => o.value === draft?.value);
    if (!course || !option) return [];
    return [{ ...scope, key: question.key, code: course.code, label: option.label,
      text: [option.text, draft.explanation.trim()].filter(Boolean).join("\n") }];
  });
}

export function followUpMessage(question: string, scope: StudentScope | null, details: SuppliedDetail[], selected: string[]) {
  const lines = [...new Set(selected)].map(key => {
    const detail = details.find(d => d.key === key && sameScope(d, scope));
    if (!detail) throw new Error("details_changed");
    return detail.text;
  });
  const text = question.trim() + (lines.length ? "\n\n" + lines.join("\n") : "");
  if (!question.trim() || text.length > 8192 || new TextEncoder().encode(text).byteLength > 16384) throw new Error("clarification_too_long");
  return text;
}
