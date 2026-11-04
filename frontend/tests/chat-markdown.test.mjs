import assert from "node:assert/strict";
import { test } from "node:test";
import { parseInline, parseMarkdown } from "../lib/chat-markdown.ts";

const text = v => ({ t: "text", v });

test("a plain-text reply stays one paragraph with its text unchanged", () => {
  assert.deepEqual(parseMarkdown("You may enroll in CC 5 next term."), [{ t: "p", c: [text("You may enroll in CC 5 next term.")] }]);
});

test("single newlines become line breaks and blank lines split paragraphs", () => {
  assert.deepEqual(parseMarkdown("a\nb\n\nc"), [
    { t: "p", c: [text("a"), { t: "br" }, text("b")] },
    { t: "p", c: [text("c")] },
  ]);
});

test("headings level 1 to 3", () => {
  assert.deepEqual(parseMarkdown("# One\n## Two\n### Three"), [
    { t: "heading", level: 1, c: [text("One")] },
    { t: "heading", level: 2, c: [text("Two")] },
    { t: "heading", level: 3, c: [text("Three")] },
  ]);
});

test("bullet and numbered lists with two-space nesting", () => {
  const [bullets, numbers] = parseMarkdown("- A\n  - A1\n* B\n\n1. First\n2. Second");
  assert.equal(bullets.t, "list");
  assert.equal(bullets.ordered, false);
  assert.equal(bullets.items.length, 2);
  assert.equal(bullets.items[0].children[0].items[0].c[0].v, "A1");
  assert.equal(numbers.ordered, true);
  assert.deepEqual(numbers.items.map(item => item.c[0].v), ["First", "Second"]);
});

test("pipe table with header separator", () => {
  const [table] = parseMarkdown("| Course | Units |\n|---|---|\n| CC 5 | 3 |\n| CC 6 | 3 |");
  assert.equal(table.t, "table");
  assert.deepEqual(table.head.map(cell => cell[0].v), ["Course", "Units"]);
  assert.equal(table.rows.length, 2);
  assert.equal(table.rows[1][0][0].v, "CC 6");
});

test("pipes without a separator row are plain text", () => {
  assert.equal(parseMarkdown("a | b")[0].t, "p");
});

test("bold, code and http links; other schemes stay literal text", () => {
  assert.deepEqual(parseInline("x **bold** `c`"), [text("x "), { t: "bold", c: [text("bold")] }, text(" "), { t: "code", v: "c" }]);
  assert.equal(parseInline("[site](https://palsu.edu.ph)")[0].t, "link");
  assert.deepEqual(parseInline("[x](javascript:alert(1))"), [text("[x](javascript:alert(1))")]);
});

test("HTML such as a script tag is kept as literal text", () => {
  const [p] = parseMarkdown("<script>alert(1)</script>");
  assert.deepEqual(p, { t: "p", c: [text("<script>alert(1)</script>")] });
  const [h] = parseMarkdown("## <img src=x onerror=alert(1)>");
  assert.equal(h.c[0].v, "<img src=x onerror=alert(1)>");
});

test("unfinished syntax renders as text", () => {
  assert.deepEqual(parseInline("**not closed"), [text("**not closed")]);
  assert.deepEqual(parseMarkdown("#hashtag"), [{ t: "p", c: [text("#hashtag")] }]);
});
