# Save control and prospectus reviewer

27 October 2026. Local ingestion/research review workstream, Phase 11 active.

## Owner request and behavior

The owner reported that a grading row with 17 context links could not be saved,
and requested the prospectus reviewer alongside Handbook/Charter review.
The policy form required a reason but disabled its distant save button without
explaining the requirement. The save action now stays visible while scrolling;
clicking it with a missing note focuses the required field. Server-side reason
validation remains mandatory. Saving a record includes its context links without
approving the linked records' fields or audience.

The owner confirmed the draft saved and authorized restart. Before shutdown the
actual policy packet reported revision0 and no decisions.jsonl; the user's browser
save could not be confirmed in that packet. The packet remains intact, with no
automated content decisions added. Updated main-port browser check passes5.61s.

## Prospectus inputs and launch

Reuse the existing39 source-bound prospectus bundles under ignored workspace
`audit-evidence/review-20261019/_evidence/<source-sha>/ingestion/`, with original PDFs
at their recorded relative paths below `review-20261019/`. All39 PDF hashes match
review-bindings.json. Preparation reuses those bundles; no conversion/model run.
No prior CSV comment or candidate parsing success becomes a new source approval.
The original structured/Prolog authoring and candidate-only export paths remain;
these are source-review questions, not vector-based course eligibility decisions.

Document switching also exposed the prior question/answer controls while the new
prospectus was loading. The focused browser regression reproduced this; keying
the existing review component by document clears that old state immediately.

The previous32-document manifest limit rejected this39-document corpus. It now
allows1..64 documents with a focused regression retaining an upper bound.
Packet digest: `2b571b6ca796ebd99df357e4fc0f06c564276625ca56e5410a2af4f8e3e67d63`.
All original PDFs, candidate bundles and journals stay ignored/local.

Main policy reviewer remains UI3001/API8765. Prospectus uses UI3002/API8766 with
an isolated frontend copy, sharing installed dependencies. Separate frontend
builds keep their compiled local API origins apart. The machine-local helper and
current authenticated launch link are below workspace
`audit-evidence/prospectus-review-ui-20261027/`: `run_reviewer.py`, `launch-url.txt`,
`packet/`, `frontend.log`. Orca terminal `Prospectus document review` owns both
prospectus processes; Ctrl+C closes both. Restart with system Python3.13 running
that helper. For a single reviewer, the supported CLI also opens the prospectus
packet using `py -3.13 -m backend.bintanong_tools.knowledge_update review <packet>
--reviewer Researcher --no-open`; close the policy reviewer first for its default
ports. Links contain launch tokens; do not commit or share those tokens.

## Verification and limits

UI fix:93053f3;manifest roster fix:f02ce05. The tracked browser test accepts a
policy packet or a prospectus packet via BINTANONG_REVIEW_TEST_LAUNCH;prospectus
mode checks document switching without saving any source decisions. The old
prospectus UI fails the stale-control check65.45s;updated isolated production UI
passes73.92s,showing the new CBA question with its own Management Accounting PDF
and source highlights. No prospectus decision journals were created by these checks.
Browser evidence covers first/last documents,not all39 question queues or accuracy.
The bounded390px/720px reflow check passed before the one-line reset;CSS unchanged.

RED: prior save action browser assertion failed;39-document manifest rejected.
GREEN:275 backend tests/80subtests in68.31s,6 Node state tests,TypeScript and
production builds pass. System Python3.13/pytest without cache; basetemp below
workspace audit-evidence/p11-policy-ingestion/save-prospectus-regressions.
Isolated browser rehearsal9.40s verifies sticky save, required-note focus,
related-context highlighting and page links, region feedback/history/export,
preserved unsaved review draft and390px/720px layout. Test decisions remain only
in the separate automated rehearsal packet.

Prospectus full-packet validation measured5.88s in a local probe; multiple
requests can make startup/document changes slow. This is researcher-tool startup,
not a student-response latency measurement. Do not weaken source integrity checks
for speed. Corpus accuracy, full accessibility, full repository and database-role
checks are not established. Existing Node22.22.3 differs from target24.21.0.
No dependency installation, hosted access, runtime pin/release change or activation.
The newer336 policy-candidate evidence remains absent. T4/T5 remain unfinished.
Prospectus answers must be saved before switching documents; this adapter does not
restore unsaved per-document answer drafts. The separate policy draft guard stays.

Frozen baseline verified again:11/11 files,7/7 seals,78 chunk/vector bindings and
both original PDF hashes pass;inventory unchanged. Policy revision remains0 and
its decisions journal remains absent. No saved decision was discarded by restart.
