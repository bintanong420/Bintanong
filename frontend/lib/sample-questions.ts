import type { StudentCurriculum } from "./student-contracts";
import { prerequisiteQuestions } from "./prerequisite-questions.ts";

// Student-phrased versions of the eight Student Handbook FAQ items (retrieval samples).
export const handbookFaqQuestions = [
  "How do I get a good moral certificate?",
  "How do I request my transfer credentials?",
  "What should I do if I lose or forget my school ID?",
  "How do I claim accident insurance?",
  "How do I get a vehicle or gate pass?",
  "How can I use a university room or facility?",
  "How do I drop a subject?",
  "How do I shift to another program?",
];

/** Three different FAQ questions; `random` returns [0, 1) like Math.random. */
export function pickFaqQuestions(random: () => number = Math.random): string[] {
  const pool = [...handbookFaqQuestions], picked: string[] = [];
  while (picked.length < 3) picked.push(pool.splice(Math.floor(random() * pool.length), 1)[0]);
  return picked;
}

export type SampleQuestionSet = { kind: "faq" | "prerequisite"; questions: string[] };

/** Two alternating sets: three random FAQs, then the selected curriculum's prerequisite checks. */
export function sampleQuestionSets(scope: StudentCurriculum | null, table: Record<string, string[]> = prerequisiteQuestions,
  random: () => number = Math.random): SampleQuestionSet[] {
  const faq: SampleQuestionSet = { kind: "faq", questions: pickFaqQuestions(random) };
  const prerequisites = scope ? table[scope.curriculumId]?.slice(0, 3) : undefined;
  return prerequisites?.length ? [faq, { kind: "prerequisite", questions: prerequisites }] : [faq];
}
