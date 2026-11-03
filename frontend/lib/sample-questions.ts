import type { StudentCurriculum } from "./student-contracts";

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

/**
 * Prerequisite eligibility samples: three per curriculum ID, 39 curricula (BSCS 2018-2019 and
 * BSCS 2025-2026 are separate entries).
 * PLACEHOLDER: awaiting another developer's handover of the 39 x 3 questions. Until a curriculum
 * has its three entries, it shows the Handbook FAQ samples only.
 */
export const prerequisiteQuestions: Record<string, string[]> = {};

export type SampleQuestionSet = { kind: "faq" | "prerequisite"; label: string; questions: string[] };

export function sampleQuestionSets(scope: StudentCurriculum | null, table: Record<string, string[]> = prerequisiteQuestions): SampleQuestionSet[] {
  const faqPages = [0, 3, 6].map(start => ({ kind: "faq" as const, label: "From the Student Handbook FAQ",
    questions: [0, 1, 2].map(offset => handbookFaqQuestions[(start + offset) % handbookFaqQuestions.length]) }));
  const prerequisites = scope ? table[scope.curriculumId]?.slice(0, 3) : undefined;
  if (!scope || !prerequisites || prerequisites.length < 3) return faqPages;
  const prerequisiteSet = { kind: "prerequisite" as const, label: `Prerequisite checks · ${scope.curriculumName} curriculum`, questions: prerequisites };
  return faqPages.flatMap(page => [page, prerequisiteSet]);
}
