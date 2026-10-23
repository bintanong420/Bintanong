import assert from "node:assert/strict";
import { test } from "node:test";
import { createWorkspace, workspaceReducer, selectFiles, shouldSend } from "../lib/workspace.ts";

const send = (state, id = "r1") => workspaceReducer(state, { type: "submit", id });
const draft = (text) => workspaceReducer(createWorkspace(), { type: "draft", text });
const file = (name, type = "application/pdf", size = 42) => ({ name, type, size });

test("empty and whitespace drafts never start a request", () => {
  for (const text of ["", "  \n\t"]) assert.equal(send(draft(text)).pending, null);
});

test("submission keeps the question and attachments, clears the draft, and refuses duplicates", () => {
  let state = draft("  A sample question?  ");
  state = workspaceReducer(state, { type: "select", ...selectFiles([file("sample.pdf")], () => "f1") });
  state = send(state);
  assert.equal(state.messages[0].text, "A sample question?");
  assert.equal(state.messages[0].attachments[0].name, "sample.pdf");
  assert.equal(state.draft, "");
  assert.equal(state.attachments.length, 0);
  assert.equal(send(state, "r2"), state);
});

test("New Chat clears everything and a late completion cannot repopulate it", () => {
  let state = send(draft("Example"));
  state = workspaceReducer(state, { type: "new-chat" });
  assert.deepEqual(state, createWorkspace());
  assert.equal(workspaceReducer(state, { type: "complete", id: "r1", text: "late", sources: [] }), state);
});

test("a completion for another request is ignored; the right completion is accepted once", () => {
  const state = send(draft("Example"));
  assert.equal(workspaceReducer(state, { type: "complete", id: "other", text: "wrong", sources: [] }), state);
  const done = workspaceReducer(state, { type: "complete", id: "r1", text: "Sample answer", sources: ["Sample source"] });
  assert.equal(done.pending, null);
  assert.equal(done.messages.at(-1).text, "Sample answer");
  assert.equal(workspaceReducer(done, { type: "complete", id: "r1", text: "duplicate", sources: [] }), done);
});

test("removing one attachment preserves unrelated files and draft", () => {
  let n = 0;
  let state = workspaceReducer(draft("Keep this"), { type: "select", ...selectFiles([file("a.pdf"), file("b.pdf")], () => `f${++n}`) });
  state = workspaceReducer(state, { type: "remove", id: "f1" });
  assert.deepEqual(state.attachments.map(f => f.name), ["b.pdf"]);
  assert.equal(state.draft, "Keep this");
});

test("unsupported, empty and oversized selections warn without dropping existing files", () => {
  let state = workspaceReducer(createWorkspace(), { type: "select", ...selectFiles([file("a.pdf")], () => "keep") });
  for (const invalid of [file("bad.exe", "application/octet-stream"), file("empty.pdf", "application/pdf", 0), file("huge.pdf", "application/pdf", 15 * 1024 * 1024 + 1)]) {
    const selection = selectFiles([invalid], () => "bad");
    assert.equal(selection.attachments.length, 0);
    assert.ok(selection.warning);
    state = workspaceReducer(state, { type: "select", ...selection });
    assert.equal(state.attachments[0].id, "keep");
  }
});

test("PDF/JPEG/PNG metadata selection never reads bytes and permits same-file reselection", () => {
  let n = 0;
  const item = { ...file("sample.pdf"), arrayBuffer() { throw Error("must not read"); } };
  const first = selectFiles([item, file("a.jpg", "image/jpeg"), file("b.png", "image/png")], () => `f${++n}`);
  assert.equal(first.attachments.length, 3);
  assert.equal(first.warning, null);
  assert.deepEqual(Object.keys(first.attachments[0]).sort(), ["id", "name", "size", "type"]);
  const again = selectFiles([item], () => `f${++n}`);
  assert.notEqual(first.attachments[0].id, again.attachments[0].id);
});

test("Enter sends only outside composition; Shift+Enter keeps a newline", () => {
  assert.equal(shouldSend({ key: "Enter", shiftKey: false, isComposing: false, keyCode: 13 }), true);
  for (const event of [{ key: "Enter", shiftKey: true }, { key: "Enter", isComposing: true }, { key: "Enter", keyCode: 229 }, { key: "a" }]) assert.equal(shouldSend(event), false);
});
