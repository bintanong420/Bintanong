"use strict";
// The review page: fetch and render, the key map, overlay boxes from the server's fractions, scroll-to-cell in the
// twin, and posting answers. Every rule about what is valid or what comes next is the server's.

const TOKEN = document.querySelector('meta[name="review-token"]').content;
const FIELD_LABELS = {
  course_code: "Course code", course_title: "Course title", term: "Year and semester", lecture_units: "Lecture units",
  lab_units: "Lab units", total_units: "Total units", prerequisites_raw: "Prerequisites as printed",
};
const $ = (id) => document.getElementById(id);
const twinBox = $("twin");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let mode = "attention";
let queue = [];
let all = [];
let current = null;
let view = null;
let twin = null;
let zoomed = false;

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined && text !== null) node.textContent = String(text);
  if (className) node.className = className;
  return node;
}

const record = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
const text = (value) => typeof value === "string";
const count = (value) => Number.isSafeInteger(value) && value >= 0;
const listOf = (value, valid) => Array.isArray(value) && value.every(valid);
const sectionShape = (s) => record(s) && text(s.sid) && text(s.title) && text(s.health);
const flagShape = (f) => record(f) && text(f.severity) && text(f.message)
  && (f.field === undefined || f.field === null || text(f.field));
const errorShape = (d) => (d.error === undefined || text(d.error))
  && (d.errors === undefined || listOf(d.errors, text)) && (text(d.error) || Array.isArray(d.errors));

function stateShape(s) {
  return record(s) && text(s.program) && text(s.reviewer) && text(s.approval_line)
    && record(s.progress) && count(s.progress.decided) && count(s.progress.questions)
    && record(s.content_review) && ["stale_entries", "inapplicable_entries", "invalid_entries"].every(key => count(s.content_review[key]))
    && record(s.source_verification) && text(s.source_verification.health) && typeof s.source_verification.pdf_checked === "boolean"
    && listOf(s.review_states, v => record(v) && text(v.name) && text(v.word) && text(v.meaning))
    && record(s.prerequisites) && ["questions", "decided", "unclassified_courses"].every(key => count(s.prerequisites[key]))
    && (s.docling === undefined || (record(s.docling) && (s.docling.warning === null || text(s.docling.warning))));
}

function questionShape(v) {
  const q = v.question;
  return record(q) && text(q.qid) && ["course", "unclaimed", "section_confirm", "prerequisite"].includes(q.kind)
    && sectionShape(q.section) && text(q.prompt) && record(q.reference)
    && Object.entries(q.reference).every(([name, value]) => name === "courses" || value === null || text(value) || Number.isFinite(value))
    && listOf(q.flags, flagShape)
    && listOf(q.proposals, p => record(p) && text(p.letter) && text(p.field) && text(p.old) && text(p.new) && text(p.note))
    && listOf(q.editable_fields, text) && typeof q.other_allowed === "boolean"
    && (q.decision === null || (record(q.decision) && text(q.decision.disposition)))
    && record(v.pdf) && typeof v.pdf.available === "boolean" && (v.pdf.available ? text(v.pdf.name) : text(v.pdf.reason))
    && record(v.boxes) && Object.values(v.boxes).every(page => record(page) && (page.warning === null || text(page.warning))
      && listOf(page.boxes, box => record(box) && typeof box.strong === "boolean" && record(box.fractions)
        && ["left", "top", "width", "height"].every(key => Number.isFinite(box.fractions[key]) && box.fractions[key] >= 0 && box.fractions[key] <= 1)))
    && listOf(v.cells, c => record(c) && text(c.cell_id) && text(c.role)
      && (c.row === null || Number.isInteger(c.row)) && (c.col === null || Number.isInteger(c.col)) && (c.text === null || text(c.text)))
    && listOf(v.twin_cell_ids, text)
    && (v.course === null || (record(v.course) && record(v.course.course) && listOf(v.course.flags, flagShape) && count(v.course.truncated)));
}

function responseShape(path, data) {
  if (!record(data)) return false;
  if (path === "/api/answer") return count(data.written) && stateShape(data.state) && (data.next === null || text(data.next));
  if (path === "/api/materialise") return text(data.file) && count(data.applied) && count(data.skipped);
  if (path === "/api/state") return stateShape(data);
  if (path.startsWith("/api/queue")) return listOf(data.queue, q => record(q) && text(q.qid) && text(q.prompt))
    && listOf(data.all, q => record(q) && text(q.qid) && text(q.prompt) && sectionShape(q.section) && typeof q.decided === "boolean");
  if (path.startsWith("/api/question/")) return questionShape(data);
  return text(data.html) || (data.html === null && text(data.reason));
}

async function api(path, body) {
  const options = body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json", "X-Review-Token": TOKEN }, body: JSON.stringify(body),
  };
  try {
    const response = await fetch(path, options);
    const data = await response.json();
    if (!record(data) || !(response.ok ? responseShape(path, data) : errorShape(data))
        || (body !== undefined && response.status >= 500)) throw new Error("unusable response");
    return { ok: response.ok, status: response.status, data };
  } catch (error) {
    return { ok: false, status: 0, data: null, error: body === undefined
      ? "The requested data could not be loaded. Check the connection and reload when the server is available."
      : "Save status unknown. The server may have completed this request. Check the connection and inspect the ledger or corrected file before submitting again." };
  }
}

function say(text) { $("status").textContent = text; }

function renderState(state) {
  $("program").textContent = state.program || "Prospectus review";
  document.title = `${state.program || "Prospectus"} - review`;
  $("reviewer").textContent = state.reviewer;
  $("progress").textContent = `decided ${state.progress.decided} of ${state.progress.questions}`;
  const review = state.content_review;
  const source = state.source_verification;
  // each state is its own word, written out; none of them is an approval and the page says so beside them
  const badges = state.review_states.map((s) => `${s.name}: ${s.word} (${s.meaning})`);
  badges.push(`PDF text check: ${source.health}, ${source.pdf_checked ? "PDF text checked" : "PDF text not checked"}`);
  if (state.prerequisites.questions) badges.push(`prerequisite questions: ${state.prerequisites.decided} of ${state.prerequisites.questions} decided (Yes and Other never hold back content review; a No does)`);
  if (state.prerequisites.unclassified_courses) badges.push(`${state.prerequisites.unclassified_courses} courses have no prerequisite state (a candidate from before Phase C): no prerequisite question for them`);
  $("approval").textContent = state.approval_line;
  if (state.docling && state.docling.warning) badges.push("Docling JSON: " + state.docling.warning);
  if (review.stale_entries || review.inapplicable_entries || review.invalid_entries) {
    badges.push(`ledger: ${review.stale_entries} stale, ${review.inapplicable_entries} for another PDF, ${review.invalid_entries} unreadable`);
  }
  $("states").replaceChildren(...badges.map((text) => el("li", text)));
}

async function loadState() {
  const response = await api("/api/state");
  if (!response.ok) { say(response.error || "The review state could not be loaded. Check the server."); return false; }
  renderState(response.data);
  return true;
}

async function loadQueue() {
  const response = await api(`/api/queue?mode=${mode}`);
  if (!response.ok) { say(response.error || "The question list could not be loaded. Check the server."); return false; }
  queue = response.data.queue;
  all = response.data.all;
  renderQueue();
  renderSections();
  return true;
}

function questionButton(item, extra) {
  const button = el("button", `${item.qid}: ${item.prompt}${extra || ""}`);
  button.type = "button";
  if (item.qid === current) button.setAttribute("aria-current", "true");
  button.addEventListener("click", () => show(item.qid));
  return button;
}

function renderQueue() {
  const filter = $("filter").value.trim().toLowerCase();
  const items = queue.filter((q) => !filter || `${q.qid} ${q.prompt}`.toLowerCase().includes(filter));
  $("queue").replaceChildren(...items.map((q) => { const li = el("li"); li.append(questionButton(q)); return li; }));
  if (!items.length) $("queue").append(el("li", queue.length ? "No question matches the filter." : "Every question has an answer."));
}

function renderSections() {
  const groups = new Map();
  for (const item of all) {
    if (!groups.has(item.section.sid)) groups.set(item.section.sid, { section: item.section, items: [] });
    groups.get(item.section.sid).items.push(item);
  }
  const blocks = [];
  for (const { section, items } of groups.values()) {
    const details = el("details");
    const summary = el("summary", `${section.title} `);
    summary.append(el("span", section.health, `health health-${section.health}`));
    details.append(summary);
    const list = el("ul");
    for (const item of items) { const li = el("li"); li.append(questionButton(item, item.decided ? " (decided)" : "")); list.append(li); }
    details.append(list);
    blocks.push(details);
  }
  $("sections").replaceChildren(...blocks);
}

async function show(qid) {
  const response = await api(`/api/question/${encodeURIComponent(qid)}`);
  if (!response.ok) { say(response.error || (response.data && response.data.error) || "That question could not be loaded. Check the server."); return; }
  current = qid;
  view = response.data;
  renderQuestion();
  renderPdf();
  renderTwin();
  renderJson();
  renderQueue();
  renderSections();
}

function renderQuestion() {
  const q = view.question;
  const decided = q.decision ? `; current decision: ${q.decision.disposition}` : "";
  $("where").textContent = `${q.section.title} (${q.section.health})${decided}`;
  $("prompt").textContent = q.prompt;
  $("flags").replaceChildren(...q.flags.map((f) => el("li", `${f.severity}: ${f.message}`, `flag-${f.severity}`)));
  const reference = [];
  for (const [name, value] of Object.entries(q.reference)) {
    if (name === "courses") continue;
    reference.push(el("dt", name.replace(/_/g, " ")), el("dd", value === null || value === "" ? "(blank)" : value));
  }
  $("reference").replaceChildren(...reference);
  $("proposals").replaceChildren(...q.proposals.map((p, index) => {
    const box = el("p", `Proposal ${p.letter}: ${FIELD_LABELS[p.field] || p.field} "${p.old}" to "${p.new}". ${p.note || ""} `);
    const button = el("button", `Use proposal ${p.letter} (key ${index + 1})`);
    button.type = "button";
    button.addEventListener("click", () => useProposal(index));
    box.append(button);
    return box;
  }));
  const fields = q.editable_fields.map((name) => {
    const wrap = el("div");
    const label = el("label", FIELD_LABELS[name] || name);
    label.htmlFor = `edit-${name}`;
    const input = el("input");
    input.id = `edit-${name}`;
    input.name = name;
    input.autocomplete = "off";
    input.setAttribute("aria-describedby", "answer-error");
    wrap.append(label, input);
    return wrap;
  });
  $("other-fields").replaceChildren(...fields);
  const other = document.querySelector('input[name="choice"][value="other"]');
  other.disabled = !q.other_allowed;
  $("other-why").hidden = q.other_allowed;
  $("other-why").textContent = q.other_allowed ? "" : "Other is not available here: there is nothing to type for this question.";
  $("reason-label").textContent = q.kind === "section_confirm" ? "Note (optional)" : "Reason";
  for (const radio of document.querySelectorAll('input[name="choice"]')) radio.checked = false;
  $("reason").value = "";
  clearError();
  updateForm();
}

function renderPdf() {
  const img = $("page-image");
  img.onerror = null;
  const pages = Object.keys(view.boxes);
  if (!view.pdf.available || !pages.length) {
    img.hidden = true;
    img.removeAttribute("src");
    $("overlays").replaceChildren();
    $("pdf-note").textContent = view.pdf.available ? "This question has no page to show." : view.pdf.reason;
    return;
  }
  const page = pages[0];
  const found = view.boxes[page];
  const what = view.question.kind === "unclaimed" ? `the printed code ${view.question.reference.code}` : `the cells of ${view.question.reference.code}`;
  const detail = view.question.kind === "section_confirm" ? `for review of ${view.question.section.title}`
    : found.boxes.length ? `with ${what} outlined` : `showing ${what}`;
  img.alt = `Page ${page} of ${view.pdf.name}, ${detail}`;
  img.onerror = () => {
    img.hidden = true;
    $("overlays").replaceChildren();
    $("pdf-note").textContent = `PDF page ${page} could not be loaded. Check the connection, then use Zoom to load the page again.`;
  };
  img.src = `/api/page/${page}.png?scale=${zoomed ? 3 : 1.5}`;
  img.hidden = false;
  $("pdf-note").textContent = found.warning || (pages.length > 1 ? `Also on page ${pages.slice(1).join(", ")}.` : "");
  $("overlays").replaceChildren(...found.boxes.map((box) => {
    const div = el("div", null, box.strong ? "box" : "box box-faint");
    div.style.left = `${box.fractions.left * 100}%`;
    div.style.top = `${box.fractions.top * 100}%`;
    div.style.width = `${box.fractions.width * 100}%`;
    div.style.height = `${box.fractions.height * 100}%`;
    return div;
  }));
}

function renderTwin() {
  if (!twin || twin.html === null) {
    $("twin-note").textContent = twin ? twin.reason : "markup twin unavailable";
    const rows = view.cells.map((c) => { const tr = el("tr"); tr.append(el("td", c.cell_id), el("td", c.role), el("td", c.row), el("td", c.col), el("td", c.text)); return tr; });
    if (!rows.length) { twinBox.replaceChildren(el("p", "No cells for this question.")); return; }
    const table = el("table");
    const head = el("tr");
    for (const name of ["cell", "role", "row", "column", "text"]) head.append(el("th", name));
    table.append(head, ...rows);
    twinBox.replaceChildren(table);
    return;
  }
  for (const cell of twinBox.querySelectorAll(".cell-own, .cell-asked")) cell.classList.remove("cell-own", "cell-asked");
  const askedRole = view.question.kind === "prerequisite" ? "prereq" : "code";
  const asked = (view.cells.find((c) => c.role === askedRole) || {}).cell_id;
  let first = null;
  for (const id of view.twin_cell_ids) {
    const cell = twinBox.querySelector(`[data-cell="${CSS.escape(id)}"]`);
    if (!cell) continue;
    cell.classList.add("cell-own");
    if (id === asked) { cell.classList.add("cell-asked"); first = cell; }
    if (view.question.kind !== "prerequisite") first = first || cell;
  }
  if (first) first.scrollIntoView({ block: "nearest", inline: "nearest", behavior: reducedMotion ? "auto" : "smooth" });
}

function renderJson() {
  $("json").textContent = JSON.stringify(view.course ? view.course.course : view.question.reference, null, 2);
  const flags = view.course ? view.course.flags : view.question.flags;
  const notes = flags.map((f) => el("li", `${f.severity} ${f.field ? `(${f.field})` : ""}: ${f.message}`, `flag-${f.severity}`));
  if (view.course && view.course.truncated) notes.push(el("li", `${view.course.truncated} source cells are not shown.`));
  $("json-flags").replaceChildren(...notes);
}

function chosen() {
  const radio = document.querySelector('input[name="choice"]:checked');
  return radio ? radio.value : null;
}

function choose(value) {
  const radio = document.querySelector(`input[name="choice"][value="${value}"]`);
  if (!radio || radio.disabled) return;
  radio.checked = true;
  radio.focus();
  updateForm();
  if (value === "other") { const field = $("other-fields").querySelector("input"); if (field) field.focus(); }
}

function updateForm() {
  $("other-fields").hidden = chosen() !== "other";
}

function closeOther() {
  if (chosen() !== "other") return;
  document.querySelector('input[name="choice"][value="other"]').checked = false;
  updateForm();
  document.querySelector('input[name="choice"]').focus();
}

function useProposal(index) {
  if (!view) return;
  const proposal = view.question.proposals[index];
  if (!proposal) return;
  choose("other");
  const field = $(`edit-${proposal.field}`);
  if (field) { field.value = String(proposal.new); field.focus(); }
  say(`Proposal ${proposal.letter} copied into ${FIELD_LABELS[proposal.field] || proposal.field}. Save to record it.`);
}

function clearError() {
  $("answer-error").textContent = "";
  for (const node of document.querySelectorAll('[aria-invalid="true"]')) node.removeAttribute("aria-invalid");
}

async function submit(event) {
  event.preventDefault();
  if (!view) return;
  clearError();
  const choice = chosen();
  if (!choice) { $("answer-error").textContent = "Choose Yes, No or Other first."; return; }
  const edits = {};
  if (choice === "other") {
    // an empty prerequisite is a real answer ("none"), so a prerequisite question sends it; elsewhere an empty box means "unchanged"
    for (const input of $("other-fields").querySelectorAll("input")) if (input.value.trim() || view.question.kind === "prerequisite") edits[input.name] = input.value;
  }
  const text = $("reason").value;
  const section = view.question.kind === "section_confirm";
  const response = await api("/api/answer", { qid: current, choice, edits, proposals: [], reason: section ? "" : text, note: section ? text : "", mode });
  if (!response.ok) {
    if (response.error) { $("answer-error").textContent = response.error; return; }
    const errors = response.data ? (response.data.errors || [response.data.error]) : ["The answer was not saved."];
    $("answer-error").textContent = `Not saved: ${errors.join("; ")}`;
    $("reason").setAttribute("aria-invalid", "true");
    for (const name of Object.keys(edits)) $(`edit-${name}`).setAttribute("aria-invalid", "true");
    return;
  }
  say(`Saved ${current}: ${response.data.written} new ledger line(s).`);
  renderState(response.data.state);
  if (!await loadQueue()) return;
  if (response.data.next) await show(response.data.next);
  else say("Saved. Every question has an answer; write the corrected candidate when you are ready.");
  $("question").focus();
}

function move(delta) {
  if (!queue.length) return;
  const index = queue.findIndex((q) => q.qid === current);
  const target = index < 0 ? 0 : Math.min(queue.length - 1, Math.max(0, index + delta));
  show(queue[target].qid);
}

function toggleZoom() {
  zoomed = !zoomed;
  $("zoom").setAttribute("aria-pressed", String(zoomed));
  $("page-wrap").classList.toggle("zoomed", zoomed);
  if (view) renderPdf();
}

async function toggleMode() {
  mode = mode === "attention" ? "print" : "attention";
  $("mode").setAttribute("aria-pressed", String(mode === "print"));
  if (await loadQueue()) say(mode === "print" ? "Questions in printed order." : "Questions that need attention first.");
}

async function writeCorrected() {
  const response = await api("/api/materialise", {});
  say(response.ok ? `${response.data.file} written: ${response.data.applied} corrections applied, ${response.data.skipped} entries skipped.`
    : response.error || (response.data && response.data.error) || "The corrected candidate was not written.");
}

const ACTIONS = {
  "yes": () => choose("yes"),
  "no": () => choose("no"),
  "other": () => choose("other"),
  "submit": () => $("answer-form").requestSubmit(),
  "close-other": () => closeOther(),
  "next": () => move(1),
  "previous": () => move(-1),
  "zoom": () => toggleZoom(),
  "mode": () => toggleMode(),
  "filter": () => $("filter").focus(),
  "help": () => $("key-help").focus(),
};

function onKey(event) {
  if (event.metaKey || event.altKey) return;
  const target = event.target instanceof Element ? event.target : document.body;
  // keyAction (keys.js) decides which key means what, and leaves a focused field's or radio's own keys alone
  const action = keyAction({ key: event.key, ctrl: event.ctrlKey, tag: target.tagName.toLowerCase(), type: target.type || "" });
  if (!action) return;
  event.preventDefault();
  if (action.startsWith("proposal:")) useProposal(Number(action.slice(9)));
  else ACTIONS[action]();
}

async function start() {
  $("answer-form").addEventListener("submit", submit);
  for (const radio of document.querySelectorAll('input[name="choice"]')) radio.addEventListener("change", updateForm);
  $("prev").addEventListener("click", () => move(-1));
  $("next").addEventListener("click", () => move(1));
  $("zoom").addEventListener("click", toggleZoom);
  $("mode").addEventListener("click", toggleMode);
  $("materialise").addEventListener("click", writeCorrected);
  $("filter").addEventListener("input", renderQueue);
  document.addEventListener("keydown", onKey);
  const response = await api("/api/twin");
  twin = response.ok ? response.data : { html: null, reason: response.error || "The markup twin could not be loaded. Check the server." };
  if (!response.ok) { $("twin-note").textContent = twin.reason; say(twin.reason); }
  if (twin.html !== null) { twinBox.innerHTML = twin.html; $("twin-note").textContent = ""; }
  if (!await loadState()) return;
  if (!await loadQueue()) return;
  const first = queue[0] || all[0];
  if (first) await show(first.qid);
  else if (response.ok) say("This candidate has no questions.");
}

start();
