import assert from "node:assert/strict";
import { test } from "node:test";
import { handbookFaqQuestions, sampleQuestionSets } from "../lib/sample-questions.ts";

test("the eight Student Handbook FAQs are the retrieval samples", () => {
  assert.equal(handbookFaqQuestions.length, 8);
});

test("sets hold three questions; FAQ pages cycle through all eight", () => {
  const sets = sampleQuestionSets(null, {});
  assert.ok(sets.every(set => set.questions.length === 3));
  assert.ok(sets.every(set => set.kind === "faq"));
  assert.deepEqual(new Set(sets.flatMap(set => set.questions)), new Set(handbookFaqQuestions));
});

test("prerequisite samples follow the chosen curriculum and alternate with FAQ pages", () => {
  const scope = { programId: "palsu-bscs", curriculumId: "bscs-2018-2019", programName: "Bachelor of Science in Computer Science", curriculumName: "2018-2019" };
  const table = { "bscs-2018-2019": ["Q1?", "Q2?", "Q3?"] };
  const sets = sampleQuestionSets(scope, table);
  assert.deepEqual(sets.map(set => set.kind), ["faq", "prerequisite", "faq", "prerequisite", "faq", "prerequisite"]);
  assert.deepEqual(sets[1].questions, ["Q1?", "Q2?", "Q3?"]);
});

test("a curriculum without handed-over samples shows only FAQ pages", () => {
  const scope = { programId: "palsu-bsn", curriculumId: "bsn-2018-2019", programName: "Nursing", curriculumName: "2018-2019" };
  assert.ok(sampleQuestionSets(scope, {}).every(set => set.kind === "faq"));
});
