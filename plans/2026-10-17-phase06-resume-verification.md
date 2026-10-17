# Phase 06 resume verification and evidence recovery

**Correction after owner direction:** the transfer-only next action in this audit
was too broad. Historical receipts are still missing, but original PDFs and tracked
settled decisions support explicit fresh generation with new provenance. Both
local candidates now exist; see [local regeneration](2026-10-17-phase06-local-regeneration.md).
Retain this audit as the record of historical-file availability, not a blocker to
generating new inactive artifacts or authorization to recreate old receipts.

Verified 17 October 2026 in the existing p06 worktree on
`chore/p06-hawksprey420-scaffold`, starting clean at `ff39af8`.
This is a resume audit, not Phase 06 completion or generated-output approval.

## Git, photos and architecture

`6fedc45` implements partial review export; `85366d4` records its delivery;
`ff39af8` adds the machine scaffold. GitHub MCP independently found the exact
delivery commit `85366d40a48f3d4ddd6d1e9f894676ad5f001184`; no remote writes.
The original checkout remains at85366d4 with its untracked model metadata untouched.

The supplied first photo describes the later generated delivery and its inactive
status. The second describes the earlier preparation stage. Their order is
resolved by Git; the older photo does not invalidate the delivered exporter.
Neither photo supplies missing artifact bytes or a generated-output review answer.
Reviews01–03 and the export design remain approved; do not reopen them.

Read AGENTS.md, both local handoff skills/artifact contract, current Phase06
plan/checkpoint, export design/plan, delivery, review01–03 and linked authoring
records. Consulted master3/11/13, thesis physical17–18/39–44 and routing PNG;
visually checked scope pages. Undergraduate/read-only/private separation stands.
Master11.4's unknown semantics supersede the thesis's illustrative missing-fact
denial. Structured authoring remains truth; generated Prolog is derived data.

## Current ignored assets

The dataset differs from the scaffold snapshot:62 files, comprising44 PDFs,
12 JPGs, one CSV, four MD files and one JSON. Prospectus subtree remains39 PDFs
and its CSV; memo/enrollment and student-government originals are now present.
Presence/counts are not source review or proof of the previous machine's inventory.
No dataset files were moved, restored, modified or staged during this audit.

All101 scaffold source paths still match their saved hashes. At destinations,
86 match at the saved paths;15 old dataset paths are absent. Eight of those have
byte-identical files in the current categorized tree. Seven old file copies have
no hash match there but remain available in the original checkout. Do not copy
them back over the supplied layout. The sealed scaffold manifest stays unchanged.
Both BSCS originals match review01 hashes; artifact/archived-state copies match.
Current dataset/local artifacts remain ignored; see [locations](dataset-locations.md).

The owner identified `C:/Coding-projects/bintanong_workspace` as recovery storage.
Directory/archive and exact-filename searches there found no original Phase06
bundles, ledgers, receipts or delivery scripts. Only synthetic test `.pl` files
were found. Model/env/cache trees and junctions were excluded from traversal;
observed junction targets were model storage or pytest aliases, not missing data.
The owner suggested the source code: a separate primary-checkout search, text
search for delivery hashes/ledger and predicate markers, and all-ref Git filename
history found compiler/tests/reports only, not original generated files/receipts.

## Recovery package and acceptance

Transfer original folders into shared `workspace/audit-evidence/`, preserving
relative paths and bytes; retain the sender's copy and avoid overwriting conflicts:

- `p06-review-bundle-20261017/`: complete921-file sealed delivery, REVIEW.md,
  both generated `.pl` files, ledgers, coverage, line maps, owner-approval.json,
  input bindings, scripts, manifests and verification records.
- `p06-bscs-authoring-selections-20261017/` and
  `p06-bscs-reference-extension-20261017/`: original proposals/review receipts,
  source renders, structured selections and their dependency bindings.
- `p06-partial-export-preparation-20261017/`, `p06-foundation-20261017/`
  and `p06-authoring-20261017/`: draft-reference preparation, review01 evidence
  and upstream authoring inputs. Follow recovered input manifests for other dependencies.

Before replay, verify original manifests and each recorded dependency. Delivery
manifest SHA-256 is `8f578ad04dc039011621b08b7952a11498502a51ba1b1e7aa54fcabd6ea1cb1a`;
owner receipt is `5f06f640b750656300dc9bfc2b11abdbe722e4b86ce640ea07635d4ade092282`.
Exact old/proposed Prolog and ledger hashes are in the [delivery report](2026-10-17-phase06-prolog-review-delivery.md).
Inspect recovered scripts/path assumptions before executing; the previous readiness
venv is absent. Preserve historical evidence; use a separate output root for replay.
Do not reconstruct approval receipts, independently edit Prolog or substitute a
synthetic bundle. After hash verification, resume human generated-output inspection.

## Fresh verification and toolchain

Raw root: `C:/Coding-projects/bintanong_workspace/audit-evidence/p06-resume-20261017/`.
Python3.13.12, Pydantic2.13.4, pytest9.0.3; explicit `py -3.13 -B`, no pytest cache,
TEMP/TMP and basetemp under raw root. No implementation or dependency changes.

```powershell
py -3.13 -B -m pytest -q -p no:cacheprovider tests/test_symbolic_review_bundle.py tests/test_symbolic_compiler.py tests/test_symbolic_authoring.py tests/test_contracts_symbolic.py tests/test_rule_candidates.py tests/test_prospectus_rule_handoff.py --basetemp=<raw-root>/symbolic-temp
py -3.13 -B -m pytest -q -p no:cacheprovider tests/test_docs_hygiene.py .agents/skills/bintanong-phase-handoff/tests/test_phase_state.py --basetemp=<raw-root>/docs-temp
```

Initial results:330 passed54.02s;542 passed/11 subtests17.94s, both exit0.
Documentation checks are rerun after this report; final result is in checkpoint.
Synthetic ground-data parsing tests passed; no real-source Prolog was consulted.
Bare Python3.11.15, Node22.22.3/npm10.9.8, SWI10.1.6 and Janus distribution1.5.2
were observed. Package/Node versions differ from pins. A fresh Python3.13
subprocess imported `janus_swi` and called fixed `X is A+1` with binding `A=2`:
exit0, `truth=True`, `X=3`; raw `janus-probe.json`. This resolves the scaffold's
bridge-untested note for this bounded probe, not runtime acceptance/concurrency.
The [official Janus API](https://www.swi-prolog.org/pldoc/man?section=janus-call-prolog)
was consulted for fixed goals with bound inputs. No arbitrary user goal was run.
Docker Linux daemon pipe remains absent. No installs, model inference, DB/API/
frontend validation, source promotion, activation, push or phase advancement.
Owner's latest request authorizes continuing remaining Phase06 runtime work in
the existing scope; real-source artifact verification remains blocked on missing
original evidence. No typed runtime or institutional execution is claimed here.
