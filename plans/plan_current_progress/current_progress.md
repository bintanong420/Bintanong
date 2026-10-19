# Current progress

Updated:19October2026,11:58. Phase07 remains active in p07/feat/p07-router-taglish-nlp.
[Plan](../phase-07-multilingual-routing-plan.md), [checkpoint](../phase-07-checkpoint.md),
[stage results](../2026-10-19-phase07-style-stage-evaluation.md),
[design/evidence trail](../2026-10-19-phase07-response-style-design.md).
Pre-condensation snapshot:614e3c3:plans/plan_current_progress/current_progress.md.

## Latest verified change

Two independent structured calls to the SAME Gemma/Bintu model isolate routing
from conversational style. Routing messages/schema remain d019318. Style receives
only original_text and returns bounded literal evidence plus a style label.
One shared format repair:normal2/max3calls. Unknown/rejected style and invalid
course proposals cannot bypass guards. No executor/API/institutional activation.

Retained implementation:ac00ac9 bytes. Actual fixed15-case composition has
15/15proposed/effective routes, entities, claims and operations; five consistent
families. Style13/15:English5/5,Filipino5/5,Taglish3/5. procedure-taglish and
excluded-taglish still select fil. Fifteen exact routing captures reused;
15fresh style calls,30logical calls,zero repairs; replay is not model latency.

A span-instruction variant fails the same two cases. Label-first614e3c3 passes
five selected cases but regresses four pure-language course queries in the full
set (style11/15); retired. Restore exact ac00ac9 backend/test bytes. No further
equivalent prompt sweep or host dictionary. Raw failed experiments stay preserved.
Only Gemma and SEA-LION embedding folders exist; no separate Bintu checkpoint found.

## Verification

Stage TDD:RED35failed/18passed ->GREEN127tests1.34s; independent review:no P1/P2,
127passed1.30s. Broad24-file gate1555passed/11subtests179.81s,exit0.
Retired label-first focused127passed3.38s; broad1555/11subtests141.12s.
Restore verified with git diff --exit-code ac00ac9 -- backend tests.
Fresh restored routing/docs/phase-state gate696passed/11subtests12.37s,exit0.
Selected fresh two-stage model checks pending.
Two inherited Docling failures remain disclosed; no whole-project-green claim.

## Boundaries and next action

Existing Python3.13 readiness venv; no installs/locks/weights/source changes.
Owner-corrected models:C:/Coding-projects/bintanong_workspace/MODELS.
Task-owned localhost18087 runtime running for selected fresh verification; other
containers/worktrees preserved. Raw:workspace/audit-evidence/p07-implementation-20261019/.
Context thesis scope17-18 refreshed from saved extraction; routing PNG viewed.
Prior39-44/58-59/master3/11/12/13 and Phase06 acceptance/source holds stay settled.

Next:commit restored candidate after checks, finish selected fresh two-stage
requests, seal evidence and stop only the task container. Phase07 stays open;
its language-style requirement still needs a model/design decision. No Phase08.
