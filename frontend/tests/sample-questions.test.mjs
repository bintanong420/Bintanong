import assert from "node:assert/strict";
import { test } from "node:test";
import { handbookFaqQuestions, pickFaqQuestions, sampleQuestionSets } from "../lib/sample-questions.ts";
import { prerequisiteQuestions } from "../lib/prerequisite-questions.ts";

const scope = (curriculumId) => ({ programId: "p", curriculumId, programName: "Program", curriculumName: "2018-2019" });
const sequence = (...values) => { let i = 0; return () => values[i++ % values.length]; };

test("the eight Student Handbook FAQs are the retrieval samples", () => {
  assert.equal(handbookFaqQuestions.length, 8);
});

test("three different FAQ questions are drawn at random", () => {
  const picked = pickFaqQuestions(sequence(0, 0, 0, 0.99));
  assert.equal(picked.length, 3);
  assert.equal(new Set(picked).size, 3);
  assert.ok(picked.every(question => handbookFaqQuestions.includes(question)));
  assert.notDeepEqual(pickFaqQuestions(sequence(0.9, 0.5, 0.1)), pickFaqQuestions(sequence(0.1, 0.5, 0.9)));
});

test("exactly two sets alternate: random FAQs, then the selected curriculum's prerequisite checks", () => {
  const sets = sampleQuestionSets(scope("bscs-2018-2019"), { "bscs-2018-2019": ["A?", "B?", "C?"] }, sequence(0.2, 0.4, 0.6));
  assert.deepEqual(sets.map(set => set.kind), ["faq", "prerequisite"]);
  assert.equal(sets[0].questions.length, 3);
  assert.deepEqual(sets[1].questions, ["A?", "B?", "C?"]);
});

test("changing program changes the prerequisite set", () => {
  const table = { a: ["A?"], b: ["B?"] };
  assert.deepEqual(sampleQuestionSets(scope("a"), table)[1].questions, ["A?"]);
  assert.deepEqual(sampleQuestionSets(scope("b"), table)[1].questions, ["B?"]);
});

test("without a program, or for a curriculum without samples, only the FAQ set shows", () => {
  assert.deepEqual(sampleQuestionSets(null, prerequisiteQuestions).map(set => set.kind), ["faq"]);
  assert.deepEqual(sampleQuestionSets(scope("unknown"), prerequisiteQuestions).map(set => set.kind), ["faq"]);
});

test("the handed-over table covers all 39 curricula, BSCS twice, without the known failing question", () => {
  assert.equal(Object.keys(prerequisiteQuestions).length, 39);
  assert.ok(prerequisiteQuestions["bscs-2018-2019"].length === 3 && prerequisiteQuestions["bscs-proposed-2025-2026"].length === 3);
  assert.ok(Object.values(prerequisiteQuestions).every(questions => questions.length >= 1 && questions.length <= 3));
  assert.equal(Object.values(prerequisiteQuestions).flat().includes("Can I take BE 2001 next semester? I haven't taken GE-PC yet."), false);
});
