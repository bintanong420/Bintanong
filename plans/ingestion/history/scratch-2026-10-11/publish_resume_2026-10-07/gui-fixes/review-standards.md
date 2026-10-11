# Independent standards and quality review

Range: `cf8b11c566d76bd5048a761a169907aee31a242b..41fe3c3241c7fdbbab66e50d805454488fbac656`, worktree `C:\Users\Hawksprey\source\repos\Bintanong-wt\gui-fixes`.

Reviewed against `.claude/agents/extractor-reviewer.md`, `plans/2026-10-05-prospectus-review-gui.md`, `docs/decisions/prospectus-review-gui.md`, and the supplied engineering instructions. No tracked files were edited, staged, committed or pushed. Worktree status was clean before and after verification.

## Confirmed finding

**P2 — Validate successful response values before treating the request as usable.** `backend/bintanong_tools/prospectus_review_gui/static/review.js:41` only checks that required keys exist and are non-null. It accepts structurally invalid values that callers cannot consume. A 200 answer response `{written: 1, state: {}, next: null}` passes `api()`, then `submit()` announces `Saved S1-01: 1 new ledger line(s).` at line 313 and throws while `renderState()` reads `state.progress.decided`. `answer-error` remains empty; the save-status-unknown recovery message never appears. A 200 queue response `{queue: {}, all: []}` also passes and throws `queue.filter is not a function` without any visible load failure. These are malformed-response cases the new recovery logic is supposed to handle. Validate consumer-required types/shapes inside the protected response path, or otherwise ensure malformed response consumption produces the same visible GET/POST recovery and preserves current inputs. Add regression cases for present-but-wrong field values.

Reproduced against the actual client with the existing Node VM harness. Run the following Python with `py -3.13 -` from the reviewed worktree:

```python
import runpy
m = runpy.run_path('tests/test_review_gui_client.py')
print(m['client_run'](r"""
fetch = async () => ({ ok: true, status: 200, json: async () => ({ written: 1, state: {}, next: null }) });
current = 'S1-01'; view = { question: { kind: 'course' } }; radios[2].checked = true;
const field = document.getElementById('edit-course_title'); field.name = 'course_title'; field.value = 'Keep this correction';
document.getElementById('other-fields').querySelectorAll = () => [field];
document.getElementById('reason').value = 'Checked source';
let thrown = null;
try { await submit({preventDefault(){}}); } catch (error) { thrown = String(error); }
console.log(JSON.stringify({ thrown, status: nodes.status.textContent, error: nodes['answer-error'].textContent, title: field.value, reason: nodes.reason.value, choice: chosen() }));
"""))
print(m['client_run'](r"""
fetch = async () => ({ ok: true, status: 200, json: async () => ({ queue: {}, all: [] }) });
let thrown = null;
try { await loadQueue(); } catch (error) { thrown = String(error); }
console.log(JSON.stringify({ thrown, status: nodes.status ? nodes.status.textContent : '' }));
"""))
```

Actual results:

```text
{'thrown': "TypeError: Cannot read properties of undefined (reading 'decided')", 'status': 'Saved S1-01: 1 new ledger line(s).', 'error': '', 'title': 'Keep this correction', 'reason': 'Checked source', 'choice': 'other'}
{'thrown': 'TypeError: queue.filter is not a function', 'status': ''}
```

## Evidence rerun

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
py -3.13 -m pytest -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\quality-resume-temp' tests/test_review_gui_client.py tests/test_review_gui_session.py tests/test_review_gui_api.py tests/test_review_gui_prerequisites.py tests/test_review_gui_sheet_equivalence.py tests/test_prospectus_materialise.py tests/test_prospectus_input_snapshot.py tests/test_prospectus_ledger.py
```

**214 passed in 56.29 seconds.** Existing tests cover transport loss, invalid JSON, null and missing top-level keys, but do not cover the present-but-invalid shapes above.

## Other inspection results

Section pages preserve no-box behavior, prerequisite twin selection does not substitute a code cell, and native image-error handling hides the image/overlays with its own live note while preserving answer/save uncertainty and requiring manual recovery. API security/input validation remain at the server boundary; session appends are serialized and use the shared entry builder/ledger lock. Materialisation rebuilds authority after classification and blank acceptance, retains source ambiguity, and forces non-executable review artifacts with the derived-sections blocker. Captured PDF and semantic-map bytes remain bound to publication identity. No additional confirmed defect was found in those changes.

Human trial, real browser/keyboard checks, Lighthouse, and Linux/macOS verification were not performed here. Root broad gates and real-corpus checks are separate evidence and were not rerun. This report does not complete Tasks 12 or 13.

CHANGES NEEDED — one confirmed P2: malformed response value shapes escape client recovery (`review.js:41`).
