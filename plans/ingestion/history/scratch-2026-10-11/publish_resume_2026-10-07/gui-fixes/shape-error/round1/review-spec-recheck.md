# Scoped specification recheck: nested render-value P2

Base: `6d8e81e9a83c65f5a92355de637e16112182ae46`.
Reviewed the frozen four-file working diff in `C:\Users\Hawksprey\source\repos\Bintanong-wt\gui-fixes`, not a subsequent commit:

- backend/bintanong_tools/prospectus_review_gui/static/review.js
- tests/test_review_gui_client.py
- docs/decisions/prospectus-review-gui.md
- plans/plan_current_progress/extractor_split_progress.md

Scope: only the original nested text-coercion P2 in shape-error/review-spec.md and its direct sibling cases. Read round1/report.md and the exact diff. No code edits, staging, commits, dependencies, agents, broad gates or owner-checkout writes were performed.

## Verdict

**APPROVED / NONE.** The original finding is resolved by the frozen working diff. Reference text-rendered values accept strings/null/finite numbers; undisplayed section member courses remain allowed. Proposal old/new/note require actual server strings. Optional flag.field accepts absent/null/string for both question and course flags. Validation runs in api before show replaces current/view or renderQuestion resets the answer.

Reused the original Python/Node reproducer unchanged. For reference.code, proposal.new and course.flags[0].field containing the JSON object {"toString":null}, all three now return:

```text
accepted=false; calls=1; thrown=null; current=keep; sameView=true;
choice=other; reason=Keep reason;
status=The requested data could not be loaded. Check the connection and reload when the server is available.
```

Thus all original failures are visible GET recovery before mutation or answer clearing, with one request and no retry. The focused tests directly verify preservation of the Other correction too. Direct sibling cases cover reference title, prerequisite array, unit object/bool/nonfinite; proposal old/new/note object and invalid null/number; question flag.field through course-null fallback; course flag.field. Legitimate reference strings/blank/null/zero/negative/fractional numbers still render; absent/null flag fields and proposal copying remain functional.

Actual server evidence was inspected rather than inferred only from validator-shaped fixtures: Fix.old/new/note are strings across strip_banner, move_term and title_from_pdf producers; format_term produces a string; Question reference construction supplies printed strings, finite numeric units/null, plus skipped courses details. Actual FastAPI/ReviewSession response consumption also passed unchanged.

## Independent verification

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
New-Item -ItemType Directory -Force -Path 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error\round1\spec-temp' | Out-Null
py -3.13 -m pytest -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error\round1\spec-temp\focused' tests/test_review_gui_client.py tests/test_review_gui_api.py
py -3.13 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error\server-shapes.py' 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error\round1\spec-temp'
```

- **166 passed in 11.70s**, pytest exit 0.
- **16 actual server-generated response bodies accepted**, actual start/question/save/materialise consumers complete, answer error empty, probe exit 0.
- Unchanged original three reproducers complete with the preserved-state/visible-error results above.
- Only the expected four frozen modified files remained; no review edits were made to the worktree. Root owns later full gates and commit mapping of this same production diff.

APPROVED — NONE within the original nested-render-value finding and its direct regressions.
