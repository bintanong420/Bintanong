"""Execute the actual review client with Node's stdlib VM and controlled DOM/transport boundaries."""

import copy
import json
import shutil
import subprocess
from pathlib import Path

import pytest

CLIENT = Path(__file__).resolve().parent.parent / "backend/bintanong_tools/prospectus_review_gui/static/review.js"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")

HARNESS = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const nodes = {};
function node(id) {
  const classes = new Set();
  return { id, textContent: '', value: '', hidden: false, children: [], attrs: {}, style: {},
    classList: { add: (...names) => names.forEach(n => classes.add(n)),
                 remove: (...names) => names.forEach(n => classes.delete(n)), contains: n => classes.has(n),
                 toggle: n => classes.has(n) ? (classes.delete(n), false) : (classes.add(n), true) },
    replaceChildren(...children) { this.children = children; },
    append(...children) { this.children.push(...children); },
    setAttribute(name, value) { this.attrs[name] = value; },
    removeAttribute(name) { delete this.attrs[name]; },
    focus() { this.focused = true; }, scrollIntoView() { this.scrolled = true; },
    addEventListener() {},
    querySelectorAll() { return []; }, querySelector() { return null; },
  };
}
const radios = ['yes', 'no', 'other'].map(value => ({ ...node(value), value, checked: false }));
const document = {
  getElementById: id => nodes[id] || (nodes[id] = node(id)),
  createElement: tag => node(tag),
  querySelector: selector => {
    if (selector.startsWith('meta')) return { content: 'token' };
    if (selector.endsWith(':checked')) return radios.find(r => r.checked) || null;
    const value = selector.match(/value="([^"]+)"/);
    return value ? radios.find(r => r.value === value[1]) : radios[0];
  },
  querySelectorAll: selector => selector.includes('choice') ? radios : [],
};
const context = vm.createContext({ document, nodes, radios, node, console, URL, CSS: { escape: x => x },
  window: { matchMedia: () => ({ matches: true }) }, fetch: async () => { throw new Error('unexpected fetch'); } });
const source = fs.readFileSync(process.argv[1], 'utf8').replace(/\nstart\(\);\s*$/, '');
vm.runInContext(source, context);
vm.runInContext('(async () => {' + process.argv[2] + '})().catch(error => { console.error(error); process.exitCode = 1; });',
                Object.assign(context, { process }));
"""


def client_run(scenario):
    done = subprocess.run([NODE, "-e", HARNESS, str(CLIENT), scenario], capture_output=True, text=True, timeout=30)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def test_section_pdf_is_visible_with_section_alt_and_no_highlights():
    got = client_run(r"""
      view = { question: { kind: 'section_confirm', section: { title: '1st Year - 1st Semester' }, reference: {} },
               pdf: { available: true, name: 'synthetic.pdf' }, boxes: { '1': { boxes: [], warning: null } } };
      renderPdf();
      console.log(JSON.stringify({ hidden: nodes['page-image'].hidden, src: nodes['page-image'].src,
                                   alt: nodes['page-image'].alt, boxes: nodes.overlays.children.length }));
    """)
    assert got["hidden"] is False and got["src"] == "/api/page/1.png?scale=1.5"
    assert "1st Year - 1st Semester" in got["alt"]
    assert "undefined" not in got["alt"] and "outlined" not in got["alt"]
    assert got["boxes"] == 0


@pytest.mark.parametrize("kind,has_prereq,asked,scrolled", [
    ("prerequisite", True, ["prereq-cell"], ["prereq-cell"]),
    ("prerequisite", False, [], []),
    ("course", True, ["code-cell"], ["code-cell"]),
])
def test_twin_focuses_the_asked_field_without_substituting_a_code_cell(kind, has_prereq, asked, scrolled):
    got = client_run(r"""
      const cells = { 'code-cell': node('code-cell'), 'prereq-cell': node('prereq-cell') };
      twinBox.querySelector = selector => cells[selector.match(/data-cell="([^"]+)"/)[1]];
      twin = { html: '<table></table>' };
      view = { question: { kind: KIND }, cells: [{ role: 'code', cell_id: 'code-cell' }], twin_cell_ids: ['code-cell'] };
      if (HAS_PREREQ) { view.cells.push({ role: 'prereq', cell_id: 'prereq-cell' }); view.twin_cell_ids.push('prereq-cell'); }
      renderTwin();
      console.log(JSON.stringify({ asked: Object.keys(cells).filter(id => cells[id].classList.contains('cell-asked')),
                                   scrolled: Object.keys(cells).filter(id => cells[id].scrolled) }));
    """.replace("KIND", json.dumps(kind)).replace("HAS_PREREQ", json.dumps(has_prereq)))
    assert got == {"asked": asked, "scrolled": scrolled}


def failed_transport(failure):
    return r"""
      let calls = 0, committed = 0;
      fetch = async (path, options) => {
        calls++;
        if (options.method === 'POST') committed++; // response can be lost after the write
        if (FAILURE === 'network') throw new TypeError('Failed to fetch');
        return { ok: FAILURE !== 'server', status: FAILURE === 'server' ? 500 : 200, json: async () => {
          if (FAILURE === 'malformed') throw new SyntaxError('Unexpected end of JSON input');
          return FAILURE === 'null' ? null : FAILURE === 'server' ? { error: 'server error' } : {};
        } };
      };
    """.replace("FAILURE", json.dumps(failure))


@pytest.mark.parametrize("failure", ["network", "malformed", "null", "missing_fields", "server"])
def test_answer_response_loss_reports_unknown_and_retains_all_entered_values(failure):
    got = client_run(failed_transport(failure) + r"""
      current = 'S1-01';
      view = { question: { kind: 'course' } };
      radios[2].checked = true;
      const field = document.getElementById('edit-course_title');
      field.name = 'course_title'; field.value = 'Reviewer title';
      document.getElementById('reason').value = 'Checked the printed source';
      document.getElementById('other-fields').querySelectorAll = () => [field];
      await submit({ preventDefault() {} });
      console.log(JSON.stringify({ error: nodes['answer-error'].textContent, calls, committed, current,
                                   choice: chosen(), title: field.value, reason: nodes.reason.value }));
    """)
    assert "status unknown" in got["error"].lower()
    assert "may have" in got["error"].lower() and "check" in got["error"].lower()
    assert "not saved" not in got["error"].lower()
    assert {key: value for key, value in got.items() if key != "error"} == {
        "calls": 1, "committed": 1, "current": "S1-01", "choice": "other",
        "title": "Reviewer title", "reason": "Checked the printed source",
    }


@pytest.mark.parametrize("failure", ["network", "malformed", "null", "missing_fields", "server"])
def test_materialise_response_loss_reports_unknown_without_retry(failure):
    got = client_run(failed_transport(failure) + r"""
      await writeCorrected();
      console.log(JSON.stringify({ status: nodes.status.textContent, calls, committed }));
    """)
    assert "status unknown" in got["status"].lower() and "not written" not in got["status"].lower()
    assert got["calls"] == got["committed"] == 1


@pytest.mark.parametrize("failure", ["network", "malformed", "null", "missing_fields"])
@pytest.mark.parametrize("action", ["loadState()", "loadQueue()", "show('S2-01')", "toggleMode()", "start()"])
def test_get_failures_are_visible_and_do_not_discard_the_current_answer(failure, action):
    got = client_run(failed_transport(failure) + r"""
      current = 'S1-01';
      radios[0].checked = true;
      document.getElementById('reason').value = 'Keep this answer';
      // start() installs listeners before loading; it must also handle a failed twin/state/list load.
      for (const id of ['answer-form', 'prev', 'next', 'zoom', 'mode', 'materialise', 'filter'])
        document.getElementById(id).addEventListener = () => {};
      for (const radio of radios) radio.addEventListener = () => {};
      document.addEventListener = () => {};
      await ACTION;
      console.log(JSON.stringify({ status: nodes.status.textContent, current, choice: chosen(), reason: nodes.reason.value,
                                   twinNote: nodes['twin-note'] ? nodes['twin-note'].textContent : '' }));
    """.replace("ACTION", action))
    assert "could not" in got["status"].lower() and "check" in got["status"].lower()
    if action == "start()":
        assert "could not" in got["twinNote"].lower()
    assert got["current"] == "S1-01" and got["choice"] == "yes" and got["reason"] == "Keep this answer"


def test_confirmed_validation_failure_retains_answer_and_shows_the_server_error():
    got = client_run(r"""
      fetch = async () => ({ ok: false, status: 422, json: async () => ({ errors: ['a reason is required'] }) });
      current = 'S1-01'; view = { question: { kind: 'course' } };
      radios[1].checked = true;
      document.getElementById('reason').value = 'Keep me';
      await submit({ preventDefault() {} });
      console.log(JSON.stringify({ error: nodes['answer-error'].textContent, choice: chosen(), reason: nodes.reason.value }));
    """)
    assert "a reason is required" in got["error"] and "status unknown" not in got["error"].lower()
    assert got["choice"] == "no" and got["reason"] == "Keep me"


@pytest.mark.parametrize("queue_fails", [True, False])
def test_saved_answer_keeps_a_followup_queue_failure_visible(queue_fails):
    got = client_run(r"""
      fetch = async path => {
        if (path.startsWith('/api/queue')) {
          if (QUEUE_FAILS) throw new TypeError('Failed to fetch');
          return { ok: true, status: 200, json: async () => ({ queue: [], all: [] }) };
        }
        return { ok: true, status: 200, json: async () => ({ written: 1, skipped: 0, errors: [], next: null, state: STATE_RESPONSE }) };
      };
      current = 'S1-01'; view = { question: { kind: 'course' } }; radios[0].checked = true;
      document.getElementById('reason').value = 'Checked';
      await submit({ preventDefault() {} });
      console.log(JSON.stringify({ status: nodes.status.textContent, error: nodes['answer-error'].textContent }));
    """.replace("QUEUE_FAILS", json.dumps(queue_fails)).replace("STATE_RESPONSE", json.dumps(STATE)))
    assert got["error"] == ""
    if queue_fails:
        assert "could not" in got["status"].lower() and "check" in got["status"].lower()
    else:
        assert "Saved" in got["status"] and "Every question has an answer" in got["status"]


@pytest.mark.parametrize("kind", ["course", "section_confirm"])
def test_pdf_image_failure_is_visible_without_losing_answers_or_save_uncertainty(kind):
    got = client_run(r"""
      current = 'S1-01'; radios[2].checked = true;
      document.getElementById('reason').value = 'Checked the source';
      document.getElementById('edit-course_title').value = 'Reviewer title';
      const uncertainty = 'Save status unknown. The server may have completed this request.';
      document.getElementById('status').textContent = uncertainty;
      document.getElementById('answer-error').textContent = uncertainty;
      view = { question: { kind: KIND, section: { title: 'First Year' }, reference: { code: 'X 1' } },
        pdf: { available: true, name: 'synthetic.pdf' }, boxes: { '1': { warning: null,
          boxes: [{ strong: true, fractions: { left: .1, top: .2, width: .1, height: .1 } }] } } };
      const img = document.getElementById('page-image');
      let requests = 0, source = '';
      Object.defineProperty(img, 'src', { set(value) { requests++; source = value; }, get() { return source; } });
      renderPdf();
      if (typeof img.onerror === 'function') img.onerror({ target: img });
      console.log(JSON.stringify({ hidden: img.hidden, overlays: nodes.overlays.children.length,
        note: nodes['pdf-note'].textContent, requests, current, choice: chosen(),
        title: nodes['edit-course_title'].value, reason: nodes.reason.value,
        status: nodes.status.textContent, error: nodes['answer-error'].textContent }));
    """.replace("KIND", json.dumps(kind)))
    assert got["hidden"] is True and got["overlays"] == 0
    assert "page 1" in got["note"].lower() and "could not" in got["note"].lower()
    assert "check" in got["note"].lower() and "zoom" in got["note"].lower()
    assert got["requests"] == 1
    assert {key: got[key] for key in ("current", "choice", "title", "reason")} == {
        "current": "S1-01", "choice": "other", "title": "Reviewer title", "reason": "Checked the source",
    }
    assert got["status"] == got["error"] == "Save status unknown. The server may have completed this request."


STATE = {
    "program": "Synthetic", "reviewer": "Test", "extraction_audit": "ok",
    "progress": {"decided": 0, "questions": 1},
    "content_review": {"state": "pending", "courses": 1, "decided": 0, "unresolved": 0,
                       "unclaimed_undecided": 0, "inapplicable_entries": 0, "invalid_entries": 0,
                       "stale_entries": 0, "orphan_entries": 0, "stale_lines": []},
    "source_verification": {"health": "clean", "pdf_checked": True},
    "review_states": [{"name": "content review", "word": "pending", "meaning": "whether a person decided every course row"}],
    "prerequisites": {"questions": 0, "decided": 0, "unclassified_courses": 0},
    "approval_line": "A reviewed prospectus is not an approved curriculum",
    "pdf": {"available": True, "name": "synthetic.pdf", "pages": 1},
    "docling": {"ok": True, "warning": None}, "note": "Local review",
}
QUESTION = {
    "qid": "S2-01", "kind": "course", "section": {"sid": "S2", "title": "Second Year", "health": "clean"},
    "prompt": "Is this course correct?", "reference": {"code": "X 1", "title": "Synthetic", "prerequisites_raw": ""},
    "flags": [{"severity": "warn", "kind": "test", "message": "Check source", "field": "course_title"}],
    "proposals": [{"letter": "a", "kind": "test", "field": "course_title", "old": "Synthetic", "new": "Correction", "note": "", "fix_id": "a"}],
    "editable_fields": ["course_title"], "other_allowed": True, "locator": {}, "pages": [1],
    "decision": None, "position": 0, "members": [], "decided": False,
}
QUESTION_VIEW = {
    "question": QUESTION, "pdf": STATE["pdf"],
    "boxes": {"1": {"boxes": [{"role": "code", "strong": True, "cell_id": "code-cell",
                              "fractions": {"left": .1, "top": .2, "width": .1, "height": .1}}], "warning": None}},
    "cells": [{"cell_id": "code-cell", "role": "code", "row": 0, "col": 0, "text": "X 1"}],
    "twin_cell_ids": ["code-cell"], "course": {"course": {"course_code": "X 1"}, "flags": QUESTION["flags"], "truncated": 0},
}
RESPONSES = {
    "/api/state": STATE,
    "/api/queue?mode=attention": {"mode": "attention", "queue": [], "all": []},
    "/api/question/S2-01": QUESTION_VIEW,
    "/api/twin": {"html": "<table></table>", "reason": None},
    "/api/answer": {"written": 1, "skipped": 0, "errors": [], "state": STATE, "next": None},
    "/api/materialise": {"file": "corrected.json", "applied": 0, "skipped": 0, "content_review": STATE["content_review"]},
}


def altered_response(path, location, value):
    body = copy.deepcopy(RESPONSES[path])
    parent = body
    for key in location[:-1]:
        parent = parent[key]
    parent[location[-1]] = value
    return body


@pytest.mark.parametrize("location,value,fallback", [
    (("question", "reference", "code"), {"toString": None}, False),
    (("question", "reference", "title"), {"toString": None}, False),
    (("question", "reference", "prerequisites_raw"), [{"toString": None}], False),
    (("question", "reference", "lecture_units"), {}, False),
    (("question", "reference", "lecture_units"), True, False),
    (("question", "reference", "lecture_units"), float("inf"), False),
    (("question", "proposals", 0, "old"), {"toString": None}, False),
    (("question", "proposals", 0, "new"), {"toString": None}, False),
    (("question", "proposals", 0, "note"), {"toString": None}, False),
    (("question", "proposals", 0, "old"), None, False),
    (("question", "proposals", 0, "new"), 3, False),
    (("question", "proposals", 0, "note"), None, False),
    (("question", "flags", 0, "field"), {"toString": None}, True),
    (("course", "flags", 0, "field"), {"toString": None}, False),
])
def test_invalid_nested_render_values_fail_before_replacing_the_question_or_clearing_inputs(location, value, fallback):
    body = altered_response("/api/question/S2-01", location, value)
    if fallback:
        body["course"] = None  # renderJson consumes question.flags when there is no course
    got = client_run(r"""
      let calls = 0;
      fetch = async () => { calls++; return { ok: true, status: 200, json: async () => (BODY) }; };
      current = 'keep'; view = { question: { kind: 'course' } }; const before = view;
      radios[2].checked = true;
      document.getElementById('reason').value = 'Keep reason';
      document.getElementById('edit-course_title').value = 'Keep correction';
      let thrown = null;
      try { await show('S2-01'); } catch (error) { thrown = String(error); }
      console.log(JSON.stringify({ calls, thrown, current, sameView: view === before, choice: chosen(),
        reason: nodes.reason.value, correction: nodes['edit-course_title'].value,
        status: nodes.status ? nodes.status.textContent : '' }));
    """.replace("BODY", json.dumps(body)))
    assert got["thrown"] is None
    assert "could not" in got["status"].lower() and "check" in got["status"].lower()
    assert {key: got[key] for key in ("calls", "current", "sameView", "choice", "reason", "correction")} == {
        "calls": 1, "current": "keep", "sameView": True, "choice": "other", "reason": "Keep reason", "correction": "Keep correction",
    }


@pytest.mark.parametrize("value,printed", [("Printed source", "Printed source"), ("", "(blank)"), (None, "(blank)"),
                                         (0, "0"), (3.5, "3.5"), (-1, "-1")])
def test_supported_reference_primitives_and_optional_flag_fields_still_render(value, printed):
    body = copy.deepcopy(QUESTION_VIEW)
    body["course"]["flags"] = copy.deepcopy(body["course"]["flags"])
    body["question"]["reference"]["printed_value"] = value
    body["question"]["reference"]["courses"] = [{"toString": None}]  # section member details are not text-rendered
    body["question"]["flags"][0]["field"] = None
    body["course"]["flags"][0].pop("field")
    got = client_run(r"""
      fetch = async () => ({ ok: true, status: 200, json: async () => (BODY) });
      await show('S2-01');
      useProposal(0);
      console.log(JSON.stringify({ current, printed: nodes.reference.children.at(-1).textContent,
        correction: nodes['edit-course_title'].value, choice: chosen(), flags: nodes['json-flags'].children.length }));
    """.replace("BODY", json.dumps(body)))
    assert got == {"current": "S2-01", "printed": printed, "correction": "Correction", "choice": "other", "flags": 1}


# Each case catches acceptance of a value that a real downstream consumer cannot use or would misreport.
GET_SHAPES = [
    ("/api/state", "loadState()", ("progress",), {}),
    ("/api/state", "loadState()", ("progress", "decided"), "0"),
    ("/api/state", "loadState()", ("progress", "questions"), True),
    ("/api/state", "loadState()", ("content_review",), []),
    ("/api/state", "loadState()", ("content_review", "stale_entries"), "0"),
    ("/api/state", "loadState()", ("source_verification",), {}),
    ("/api/state", "loadState()", ("source_verification", "pdf_checked"), "false"),
    ("/api/state", "loadState()", ("review_states",), {}),
    ("/api/state", "loadState()", ("review_states",), [None]),
    ("/api/state", "loadState()", ("review_states", 0, "meaning"), {}),
    ("/api/state", "loadState()", ("prerequisites",), {}),
    ("/api/state", "loadState()", ("prerequisites", "questions"), "0"),
    ("/api/state", "loadState()", ("docling",), "warning"),
    ("/api/state", "loadState()", ("reviewer",), {}),
    ("/api/state", "loadState()", ("approval_line",), []),
    ("/api/queue?mode=attention", "loadQueue()", ("queue",), {}),
    ("/api/queue?mode=attention", "loadQueue()", ("queue",), [None]),
    ("/api/queue?mode=attention", "loadQueue()", ("queue",), [{"qid": 1, "prompt": "Check"}]),
    ("/api/queue?mode=attention", "loadQueue()", ("all",), {}),
    ("/api/queue?mode=attention", "loadQueue()", ("all",), [{"qid": "S2-01", "prompt": "Check", "section": None}]),
    ("/api/queue?mode=attention", "loadQueue()", ("all",), [{"qid": "S2-01", "prompt": "Check", "section": {}}]),
    ("/api/question/S2-01", "show('S2-01')", ("question",), {}),
    ("/api/question/S2-01", "show('S2-01')", ("question", "section"), None),
    ("/api/question/S2-01", "show('S2-01')", ("question", "flags"), {}),
    ("/api/question/S2-01", "show('S2-01')", ("question", "flags"), [None]),
    ("/api/question/S2-01", "show('S2-01')", ("question", "reference"), []),
    ("/api/question/S2-01", "show('S2-01')", ("question", "proposals"), [None]),
    ("/api/question/S2-01", "show('S2-01')", ("question", "editable_fields"), [None]),
    ("/api/question/S2-01", "show('S2-01')", ("question", "other_allowed"), "false"),
    ("/api/question/S2-01", "show('S2-01')", ("question", "decision"), {}),
    ("/api/question/S2-01", "show('S2-01')", ("pdf",), {}),
    ("/api/question/S2-01", "show('S2-01')", ("boxes",), []),
    ("/api/question/S2-01", "show('S2-01')", ("boxes", "1", "boxes"), [None]),
    ("/api/question/S2-01", "show('S2-01')", ("boxes", "1", "boxes", 0, "fractions"), {}),
    ("/api/question/S2-01", "show('S2-01')", ("boxes", "1", "boxes", 0, "fractions", "width"), "0.1"),
    ("/api/question/S2-01", "show('S2-01')", ("cells",), [None]),
    ("/api/question/S2-01", "show('S2-01')", ("twin_cell_ids",), [None]),
    ("/api/question/S2-01", "show('S2-01')", ("course", "flags"), {}),
    ("/api/question/S2-01", "show('S2-01')", ("course", "course"), []),
    ("/api/twin", "start()", ("html",), {}),
    ("/api/twin", "start()", ("html",), 0),
    ("/api/twin", "start()", ("reason",), None),  # unusable when html is null
]


@pytest.mark.parametrize("path,action,location,value", GET_SHAPES)
def test_present_but_invalid_get_shapes_are_visible_before_current_state_changes(path, action, location, value):
    responses = copy.deepcopy(RESPONSES)
    responses[path] = altered_response(path, location, value)
    if path == "/api/twin" and location == ("reason",):
        responses[path]["html"] = None
    got = client_run(r"""
      const responses = RESPONSES;
      let calls = 0;
      fetch = async path => { calls++; return { ok: true, status: 200, json: async () => responses[path] }; };
      document.addEventListener = () => {};
      current = 'S1-01'; view = { question: { kind: 'course' } }; const before = view;
      queue = [{ qid: 'keep' }]; all = [{ qid: 'keep' }];
      radios[2].checked = true;
      const field = document.getElementById('edit-course_title'); field.value = 'Keep this correction';
      document.getElementById('reason').value = 'Checked source';
      document.getElementById('program').textContent = 'Keep current program';
      document.getElementById('queue').textContent = 'Keep current list';
      let thrown = null;
      try { await ACTION; } catch (error) { thrown = String(error); }
      console.log(JSON.stringify({ thrown, calls, current, sameView: view === before, choice: chosen(),
        title: field.value, reason: nodes.reason.value, status: nodes.status.textContent,
        program: nodes.program.textContent, list: nodes.queue.textContent,
        twinNote: nodes['twin-note'] ? nodes['twin-note'].textContent : '' }));
    """.replace("RESPONSES", json.dumps(responses)).replace("ACTION", action))
    assert got["thrown"] is None
    assert "could not" in got["status"].lower() and "check" in got["status"].lower()
    assert got["calls"] == (3 if action == "start()" else 1)
    assert {key: got[key] for key in ("current", "sameView", "choice", "title", "reason")} == {
        "current": "S1-01", "sameView": True, "choice": "other", "title": "Keep this correction", "reason": "Checked source",
    }
    if action != "start()":
        assert got["program"] == "Keep current program" and got["list"] == "Keep current list"
    else:
        assert "could not" in got["twinNote"].lower()


POST_SHAPES = [
    ("/api/answer", ("written",), "1"),
    ("/api/answer", ("written",), -1),
    ("/api/answer", ("written",), True),
    ("/api/answer", ("state",), {}),
    ("/api/answer", ("state", "review_states"), [None]),
    ("/api/answer", ("state", "progress", "decided"), "1"),
    ("/api/answer", ("next",), {}),
    ("/api/answer", ("next",), 0),
    ("/api/materialise", ("file",), {}),
    ("/api/materialise", ("applied",), "0"),
    ("/api/materialise", ("applied",), -1),
    ("/api/materialise", ("skipped",), []),
]


@pytest.mark.parametrize("path,location,value", POST_SHAPES)
def test_present_but_invalid_post_shapes_report_unknown_without_a_success_or_retry(path, location, value):
    responses = copy.deepcopy(RESPONSES)
    responses[path] = altered_response(path, location, value)
    got = client_run(r"""
      const responses = RESPONSES;
      let calls = 0, committed = 0;
      fetch = async (path, options) => { calls++; if (options.method === 'POST') committed++;
        return { ok: true, status: 200, json: async () => responses[path] }; };
      current = 'S1-01'; view = { question: { kind: 'course' } }; const before = view;
      radios[2].checked = true;
      const field = document.getElementById('edit-course_title'); field.name = 'course_title'; field.value = 'Keep this correction';
      document.getElementById('other-fields').querySelectorAll = () => [field];
      document.getElementById('reason').value = 'Checked source';
      document.getElementById('program').textContent = 'Keep current program';
      let thrown = null;
      try { await ACTION; } catch (error) { thrown = String(error); }
      console.log(JSON.stringify({ thrown, calls, committed, current, sameView: view === before, choice: chosen(),
        title: field.value, reason: nodes.reason.value, program: nodes.program.textContent,
        status: nodes.status ? nodes.status.textContent : '', error: nodes['answer-error'] ? nodes['answer-error'].textContent : '' }));
    """.replace("RESPONSES", json.dumps(responses)).replace("ACTION", "submit({ preventDefault() {} })" if path == "/api/answer" else "writeCorrected()"))
    assert got["thrown"] is None
    message = got["error"] if path == "/api/answer" else got["status"]
    assert "status unknown" in message.lower() and "check" in message.lower()
    assert "Saved" not in got["status"] and "written:" not in got["status"]
    assert got["calls"] == got["committed"] == 1
    assert {key: got[key] for key in ("current", "sameView", "choice", "title", "reason", "program")} == {
        "current": "S1-01", "sameView": True, "choice": "other", "title": "Keep this correction", "reason": "Checked source",
        "program": "Keep current program",
    }


@pytest.mark.parametrize("fallback", [False, True])
def test_consumer_shaped_success_responses_render_and_confirm_writes(fallback):
    responses = copy.deepcopy(RESPONSES)
    responses["/api/queue?mode=attention"].update(queue=[QUESTION], all=[QUESTION])
    if fallback:
        responses["/api/twin"] = {"html": None, "reason": "No semantic evidence"}
        responses["/api/question/S2-01"].update(pdf={"available": False, "reason": "No PDF"}, boxes={}, course=None)
    got = client_run(r"""
      const responses = RESPONSES;
      fetch = async path => ({ ok: true, status: 200, json: async () => responses[path] });
      document.addEventListener = () => {};
      await start();
      const loaded = { current, program: nodes.program.textContent, prompt: nodes.prompt.textContent,
        hidden: nodes['page-image'].hidden, pdfNote: nodes['pdf-note'].textContent, fields: nodes['other-fields'].children.length };
      radios[0].checked = true;
      await submit({ preventDefault() {} });
      const saved = nodes.status.textContent;
      await writeCorrected();
      console.log(JSON.stringify({ loaded, saved, written: nodes.status.textContent, error: nodes['answer-error'].textContent }));
    """.replace("RESPONSES", json.dumps(responses)))
    assert got["loaded"] == {"current": "S2-01", "program": "Synthetic", "prompt": "Is this course correct?",
                             "hidden": fallback, "pdfNote": "No PDF" if fallback else "", "fields": 1}
    assert "Saved" in got["saved"] and got["error"] == ""
    assert got["written"] == "corrected.json written: 0 corrections applied, 0 entries skipped."


@pytest.mark.parametrize("body", [{"errors": 1}, {"errors": [None]}, {"errors": "bad"}, {"error": {}},
                                  {"error": "Bad request", "errors": {}}, {}])
@pytest.mark.parametrize("action", ["submit({ preventDefault() {} })", "writeCorrected()", "loadState()"])
def test_invalid_error_envelopes_use_recovery_instead_of_throwing_or_claiming_a_known_write_result(body, action):
    got = client_run(r"""
      let calls = 0;
      fetch = async () => { calls++; return { ok: false, status: 400, json: async () => (BODY) }; };
      current = 'S1-01'; view = { question: { kind: 'course' } }; const before = view;
      radios[0].checked = true;
      document.getElementById('reason').value = 'Keep this answer';
      let thrown = null;
      try { await ACTION; } catch (error) { thrown = String(error); }
      console.log(JSON.stringify({ thrown, calls, current, sameView: view === before, choice: chosen(), reason: nodes.reason.value,
        status: nodes.status ? nodes.status.textContent : '', error: nodes['answer-error'] ? nodes['answer-error'].textContent : '' }));
    """.replace("BODY", json.dumps(body)).replace("ACTION", action))
    assert got["thrown"] is None
    message = got["error"] if action.startswith("submit") else got["status"]
    assert "check" in message.lower()
    assert ("could not" if action == "loadState()" else "status unknown") in message.lower()
    assert got["calls"] == 1 and got["sameView"] is True
    assert (got["current"], got["choice"], got["reason"]) == ("S1-01", "yes", "Keep this answer")


@pytest.mark.parametrize("body", [{"errors": ["a reason is required"]}, {"error": "Bad request"},
                                  {"error": "Bad request", "errors": ["a reason is required"]}])
def test_valid_error_envelopes_keep_definite_failure_semantics(body):
    got = client_run(r"""
      fetch = async () => ({ ok: false, status: 400, json: async () => (BODY) });
      current = 'S1-01'; view = { question: { kind: 'course' } }; radios[0].checked = true;
      await submit({ preventDefault() {} });
      console.log(JSON.stringify({ error: nodes['answer-error'].textContent }));
    """.replace("BODY", json.dumps(body)))
    assert "Not saved:" in got["error"] and "status unknown" not in got["error"].lower()
    assert body.get("errors", [body.get("error")])[0] in got["error"]


def test_pdf_image_can_recover_only_on_a_manual_render():
    got = client_run(r"""
      view = { question: { kind: 'course', reference: { code: 'X 1' } },
        pdf: { available: true, name: 'synthetic.pdf' }, boxes: { '1': { warning: null,
          boxes: [{ strong: true, fractions: { left: .1, top: .2, width: .1, height: .1 } }] } } };
      const img = document.getElementById('page-image');
      let requests = 0;
      Object.defineProperty(img, 'src', { set() { requests++; } });
      renderPdf();
      if (typeof img.onerror === 'function') img.onerror({ target: img });
      const failed = { hidden: img.hidden, overlays: nodes.overlays.children.length, requests };
      toggleZoom(); // explicit user recovery action; renderPdf installs a fresh source and handler
      console.log(JSON.stringify({ failed, recovered: { hidden: img.hidden,
        overlays: nodes.overlays.children.length, note: nodes['pdf-note'].textContent, requests } }));
    """)
    assert got["failed"] == {"hidden": True, "overlays": 0, "requests": 1}
    assert got["recovered"] == {"hidden": False, "overlays": 1, "note": "", "requests": 2}


@pytest.mark.parametrize("available", [False, True])
def test_pdf_error_handler_is_detached_for_an_unavailable_or_empty_view(available):
    got = client_run(r"""
      view = { question: { kind: 'section_confirm', section: { title: 'First Year' }, reference: {} },
        pdf: { available: true, name: 'synthetic.pdf' }, boxes: { '1': { boxes: [], warning: null } } };
      const img = document.getElementById('page-image');
      renderPdf();
      view = { pdf: { available: AVAILABLE, reason: 'No PDF was supplied' }, boxes: {} };
      renderPdf();
      if (typeof img.onerror === 'function') img.onerror({ target: img });
      console.log(JSON.stringify({ hidden: img.hidden, overlays: nodes.overlays.children.length,
        note: nodes['pdf-note'].textContent, handlerActive: typeof img.onerror === 'function' }));
    """.replace("AVAILABLE", json.dumps(available)))
    assert got == {"hidden": True, "overlays": 0, "handlerActive": False,
                   "note": "This question has no page to show." if available else "No PDF was supplied"}
