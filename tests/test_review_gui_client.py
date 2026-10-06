"""Execute the actual review client with Node's stdlib VM and controlled DOM/transport boundaries."""

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
                 remove: (...names) => names.forEach(n => classes.delete(n)), contains: n => classes.has(n) },
    replaceChildren(...children) { this.children = children; },
    append(...children) { this.children.push(...children); },
    setAttribute(name, value) { this.attrs[name] = value; },
    removeAttribute(name) { delete this.attrs[name]; },
    focus() { this.focused = true; }, scrollIntoView() { this.scrolled = true; },
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
        return { ok: true, status: 200, json: async () => ({ written: 1, next: null, state: {
          program: 'Synthetic', reviewer: 'Test', progress: { decided: 1, questions: 1 }, content_review: {},
          source_verification: { health: 'clean', pdf_checked: true }, review_states: [], prerequisites: {},
          approval_line: 'A reviewed prospectus is not an approved curriculum',
        } }) };
      };
      current = 'S1-01'; view = { question: { kind: 'course' } }; radios[0].checked = true;
      document.getElementById('reason').value = 'Checked';
      await submit({ preventDefault() {} });
      console.log(JSON.stringify({ status: nodes.status.textContent, error: nodes['answer-error'].textContent }));
    """.replace("QUEUE_FAILS", json.dumps(queue_fails)))
    assert got["error"] == ""
    if queue_fails:
        assert "could not" in got["status"].lower() and "check" in got["status"].lower()
    else:
        assert "Saved" in got["status"] and "Every question has an answer" in got["status"]
