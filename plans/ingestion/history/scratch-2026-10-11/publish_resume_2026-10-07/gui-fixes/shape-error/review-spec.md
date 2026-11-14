# Scoped GUI response-shape specification review

Range: `41fe3c3241c7fdbbab66e50d805454488fbac656..6d8e81e9a83c65f5a92355de637e16112182ae46`.
Worktree: `C:\Users\Hawksprey\source\repos\Bintanong-wt\gui-fixes`.

Read `.claude/agents/extractor-reviewer.md`, applicable GUI plan and decision record, external `review-standards.md` and `shape-error/report.md`; traced all six JSON API consumers and server response construction in app/session/questions/render/geometry. Scope is the new shared response boundary and direct regressions. No tracked edits, staging, commits or push. Worktree remained clean.

## Confirmed specification finding

**P2 — Nested text-rendered values still escape recovery and replace the current question before throwing.** `backend/bintanong_tools/prospectus_review_gui/static/review.js:50` checks `question.reference` only as an object; line 51 checks proposal letter/field without checking interpolated old/new/note; `flagShape` at line 33 leaves optional field unchecked, including its use through line 61. An ordinary JSON-serializable object `{"toString": null}` placed in `question.reference.code`, `question.proposals[0].new`, or `course.flags[0].field` passes `responseShape`. Its own toString prevents conversion to text, so downstream String/template coercion at lines 188, 192, or 287 throws `TypeError: Cannot convert object to primitive value` outside api recovery.

All three cases replace current/view at lines 169-170 and give no visible GET recovery message. The course flag-field case reaches renderJson only after renderQuestion clears Other choice and reason at lines 217-218, losing entered state. This violates malformed-GET recovery before state mutation. Guard the actual text-consumed nested values before replacing/resetting state, retaining actual server-supported value types.

Reproducer: run this Python from the reviewed worktree with `py -3.13 -` and `PYTHONDONTWRITEBYTECODE=1`; it executes the real client in the existing Node VM harness:

```python
import copy, json, runpy
m = runpy.run_path('tests/test_review_gui_client.py')
for label in ['reference.code', 'proposal.new', 'flag.field']:
    v = copy.deepcopy(m['QUESTION_VIEW'])
    bad = {'toString': None}
    if label == 'reference.code':
        v['question']['reference']['code'] = bad
    elif label == 'proposal.new':
        v['question']['proposals'][0]['new'] = bad
    else:
        v['course']['flags'][0]['field'] = bad
    got = m['client_run'](r'''
        const bad = BODY;
        let calls = 0;
        fetch = async () => { calls++; return {ok:true, status:200, json:async()=>bad}; };
        current = 'keep'; view = {question:{kind:'course'}}; const before = view;
        radios[2].checked = true;
        document.getElementById('reason').value = 'Keep reason';
        document.getElementById('edit-course_title').value = 'Keep correction';
        let thrown = null;
        try { await show('S2-01'); } catch(error) { thrown = String(error); }
        console.log(JSON.stringify({accepted:responseShape('/api/question/S2-01',bad),
          calls, thrown, current, sameView:view===before, choice:chosen(),
          reason:nodes.reason.value, status:nodes.status ? nodes.status.textContent : ''}));
    '''.replace('BODY', json.dumps(v)))
    print(label, json.dumps(got))
```

Observed:

```text
reference.code {"accepted": true, "calls": 1, "thrown": "TypeError: Cannot convert object to primitive value", "current": "S2-01", "sameView": false, "choice": "other", "reason": "Keep reason", "status": ""}
proposal.new {"accepted": true, "calls": 1, "thrown": "TypeError: Cannot convert object to primitive value", "current": "S2-01", "sameView": false, "choice": "other", "reason": "Keep reason", "status": ""}
flag.field {"accepted": true, "calls": 1, "thrown": "TypeError: Cannot convert object to primitive value", "current": "S2-01", "sameView": false, "choice": null, "reason": "", "status": ""}
```

## Independently rerun evidence

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
New-Item -ItemType Directory -Force -Path 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error\spec-temp' | Out-Null
py -3.13 -m pytest -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error\spec-temp\verified-focused' tests/test_review_gui_client.py tests/test_review_gui_api.py
py -3.13 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error\server-shapes.py' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error\spec-temp'
```

- Focused client/API: **146 passed in 9.03s**, exit 0.
- Actual synthetic ReviewSession/FastAPI response probe: **16 response bodies**, all accepted; start/question/save/materialise consumers complete, no answer error, exit 0.
- Actual server emits nullable twin HTML with string fallback reason. State/answer/materialise consumer types match the predicates. Valid server 4xx string/string-array envelopes retain validation-failure behavior. Covered malformed POST/lost-response paths preserve choice/Other/reason/current, announce unknown save status, and make no retry or success announcement.
- The passing suite does not cover the three confirmed nested coercion failures. No unrelated finding. Broad gates were not rerun.

CHANGES NEEDED — one confirmed P2: accepted malformed nested question values throw after state mutation and can clear entered answers (`review.js:50`, `review.js:51`, `review.js:33`).
