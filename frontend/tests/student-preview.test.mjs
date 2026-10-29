import assert from "node:assert/strict";
import { test } from "node:test";
import { createWorkspace, workspaceReducer as reduce } from "../lib/workspace.ts";

const file = id => ({ id, name: `${id}.pdf`, type: "application/pdf", size: 42 });
const seed = () => reduce(createWorkspace(), { type: "example", kind: "clarification", id: "question", files: [file("a"), file("b")], facts: [
  { id: "course", label: "Course", value: "Course A", fileId: "a", decision: "unconfirmed" },
  { id: "note", label: "Course note", value: "Sample note", fileId: "b", decision: "unconfirmed" },
] });

test("clarification cancel preserves question/files and does not submit a draft", () => {
  let s = seed();
  s = reduce(s, { type: "clarification-draft", value: "Course B", unknown: false });
  s = reduce(s, { type: "clarification-cancel" });
  assert.equal(s.preview.clarification, "dismissed");
  assert.equal(s.messages.filter(m => m.role === "user").length, 1);
  assert.equal(s.preview.files.length, 2);
  assert.equal(s.pending, null);
});
test("blank clarification is rejected; explicit unknown submits once", () => {
  let s = seed();
  assert.equal(reduce(s, { type: "clarification-submit", id: "reply" }), s);
  s = reduce(s, { type: "clarification-draft", value: "", unknown: true });
  s = reduce(s, { type: "clarification-submit", id: "reply" });
  assert.equal(s.messages.at(-1).text, "I don’t know");
  assert.equal(s.pending, "reply");
  assert.equal(reduce(s, { type: "clarification-submit", id: "duplicate" }), s);
});
test("editing a confirmed detail revokes confirmation until explicitly confirmed", () => {
  let s = reduce(seed(), { type: "fact-confirm", id: "course" });
  s = reduce(s, { type: "fact-edit", id: "course", value: "Course B" });
  assert.equal(s.preview.facts[0].decision, "unconfirmed");
  assert.equal(s.preview.facts[0].value, "Course A");
  assert.equal(s.preview.facts[0].draft, "Course B");
  s = reduce(s, { type: "fact-confirm", id: "course" });
  assert.equal(s.preview.facts[0].value, "Course B");
  assert.equal(s.preview.facts[0].decision, "confirmed");
  assert.equal(s.preview.facts[1].decision, "unconfirmed");
});
test("canceling an edit preserves value without silently reconfirming it", () => {
  let s = reduce(seed(), { type: "fact-edit", id: "course", value: "Course B" });
  s = reduce(s, { type: "fact-cancel", id: "course" });
  assert.equal(s.preview.facts[0].value, "Course A");
  assert.equal(s.preview.facts[0].draft, undefined);
  assert.equal(s.preview.facts[0].decision, "unconfirmed");
});
test("empty edits cannot be confirmed; removed details never count as confirmed", () => {
  let s = reduce(seed(), { type: "fact-edit", id: "course", value: "  " });
  assert.equal(reduce(s, { type: "fact-confirm", id: "course" }), s);
  s = reduce(s, { type: "fact-remove", id: "course" });
  assert.equal(s.preview.facts[0].decision, "removed");
  assert.equal(reduce(s, { type: "fact-confirm", id: "course" }), s);
});
test("file removal invalidates only its linked details", () => {
  let s = reduce(seed(), { type: "fact-confirm", id: "course" });
  s = reduce(s, { type: "remove", id: "a" });
  assert.deepEqual(s.preview.files.map(f => f.id), ["b"]);
  assert.deepEqual(s.preview.facts.map(f => f.id), ["note"]);
});
test("retry keeps the original question and refuses duplicates", () => {
  let s = reduce(createWorkspace(), { type: "example", kind: "connection", id: "original", files: [], facts: [] });
  s = reduce(s, { type: "retry" });
  assert.equal(s.pending, "original");
  assert.equal(s.messages.filter(m => m.role === "user").length, 1);
  assert.equal(reduce(s, { type: "retry" }), s);
});
test("expiry keeps the question while dropping every file and detail", () => {
  let s = reduce(seed(), { type: "fact-confirm", id: "course" });
  const question = s.messages[0].text;
  s = reduce(s, { type: "expire" });
  assert.equal(s.messages[0].text, question);
  assert.deepEqual(s.preview.files, []);
  assert.deepEqual(s.preview.facts, []);
  assert.deepEqual(s.attachments, []);
});
test("clear waits for acknowledgment and preserves all chat data on failure", () => {
  const before = seed();
  let s = reduce(before, { type: "clear-start", id: "clear" });
  assert.deepEqual(s.messages, before.messages);
  assert.deepEqual(s.preview.files, before.preview.files);
  s = reduce(s, { type: "clear-complete", id: "clear", confirmed: false });
  assert.equal(s.preview.clear, "failed");
  assert.deepEqual(s.messages, before.messages);
  assert.deepEqual(s.preview.facts, before.preview.facts);
  s = reduce(s, { type: "clear-start", id: "retry-clear" });
  s = reduce(s, { type: "clear-complete", id: "retry-clear", confirmed: true });
  assert.deepEqual(s, createWorkspace());
});
test("stale clear and file-stage completions cannot alter a new chat", () => {
  const pending = reduce(seed(), { type: "clear-start", id: "old" });
  const fresh = reduce(pending, { type: "new-chat" });
  assert.equal(reduce(fresh, { type: "clear-complete", id: "old", confirmed: true }), fresh);
  assert.equal(reduce(fresh, { type: "file-stage", id: "old", stage: "review" }), fresh);
});

test("new file selection cancels a stale preview check without losing other files", () => {
  let s = reduce(seed(), { type: "file-start", id: "old-check", facts: [] });
  s = reduce(s, { type: "select", attachments: [file("c")], warning: null });
  assert.equal(s.preview.fileRequest, null);
  assert.deepEqual(s.preview.files.map(f => f.id), ["a", "b", "c"]);
  assert.equal(reduce(s, { type: "file-stage", id: "old-check", stage: "review" }), s);
});
test("clarification cannot submit while a clear is awaiting acknowledgment", () => {
  let s = reduce(seed(), { type: "clarification-draft", value: "Course B", unknown: false });
  s = reduce(s, { type: "clear-start", id: "clearing" });
  assert.equal(reduce(s, { type: "clarification-submit", id: "new-answer" }), s);
});
test("typed details need an explicit decision; Continue never confirms untouched facts", () => {
  let s = reduce(seed(), { type: "fact-add", id: "typed", value: "  A detail I supplied  " });
  assert.equal(s.preview.facts.at(-1).fileId, null);
  assert.equal(s.preview.facts.at(-1).decision, "unconfirmed");
  assert.equal(reduce(s, { type: "review-continue" }), s);
  s = reduce(s, { type: "fact-confirm", id: "typed" });
  s = reduce(s, { type: "review-continue" });
  assert.deepEqual(s.preview.facts.filter(f => f.decision === "confirmed").map(f => f.id), ["typed"]);
});
test("removed details cannot be revived by a stale editing action", () => {
  const s = reduce(seed(), { type: "fact-remove", id: "course" });
  assert.equal(reduce(s, { type: "fact-edit", id: "course", value: "Course B" }).preview.facts[0].decision, "removed");
});
test("an awaiting clear freezes draft, file selection and retry until its result", () => {
  const s = reduce(seed(), { type: "clear-start", id: "clear" });
  for (const action of [{ type: "draft", text: "late edit" }, { type: "select", attachments: [file("c")], warning: null }, { type: "retry" }]) assert.equal(reduce(s, action), s);
});
