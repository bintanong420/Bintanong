
### Standards fixes F1 RED (2026-10-07T05:19:14.5594843+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M tests/test_prospectus_ledger.py.
- Result: 3 failed, 2 passed, 10 deselected; exit 1; wrong reviewed status for undecided/wrong-PDF/stale anomaly. Command: py -3.13 -m pytest tests/test_prospectus_ledger.py -k persisted_anomalies -q -p no:cacheprovider --basetemp <scratch>/f1-red-temp (PYTHONDONTWRITEBYTECODE=1; f1-red.log).
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: Reuse placement.unclaimed_items in both ledger completion and staleness checks; then focused green. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.


### Standards fixes F1 GREEN (2026-10-07T05:19:58.4364815+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M backend/bintanong_tools/prospectus_extractor/ledger.py;  M plans/plan_current_progress/extractor_split_progress.md;  M tests/test_prospectus_ledger.py.
- Result: 141 passed; exit 0; ledger, sheet, B2 regression files. Command: py -3.13 -m pytest tests/test_prospectus_ledger.py tests/test_prospectus_b2_codex_review.py tests/test_prospectus_b2_review_fixes.py tests/test_prospectus_sheet.py -q -p no:cacheprovider --basetemp <scratch>/f1-green-temp (PYTHONDONTWRITEBYTECODE=1; f1-green.log).
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: F2 write authority regressions before production changes. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.


### Standards fixes F2 RED (2026-10-07T05:20:20.7830196+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M backend/bintanong_tools/prospectus_extractor/ledger.py;  M plans/plan_current_progress/extractor_split_progress.md;  M tests/test_prospectus_ledger.py;  M tests/test_prospectus_materialise.py.
- Result: 5 failed, 9 deselected; exit 1; executable inherited authority, zero incomplete count, pending top-level review. Command: py -3.13 -m pytest tests/test_prospectus_materialise.py -k "stale_authority or top_level_review_status" -q -p no:cacheprovider --basetemp <scratch>/f2-red-temp (PYTHONDONTWRITEBYTECODE=1; f2-red.log).
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: Recompute via authority.build_authority, preserve source gates, explicitly block stale derived sections. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.


### Standards fixes F2 GREEN (2026-10-07T05:21:21.6656947+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M backend/bintanong_tools/prospectus_extractor/ledger.py;  M plans/plan_current_progress/extractor_split_progress.md;  M tests/test_prospectus_ledger.py;  M tests/test_prospectus_materialise.py.
- Result: 351 passed; exit 0; authority, materialise, ledger and B2 regression files. Command: py -3.13 -m pytest tests/test_prospectus_materialise.py tests/test_prospectus_authority.py tests/test_prospectus_ledger.py tests/test_prospectus_b2_codex_review.py tests/test_prospectus_b2_review_fixes.py -q -p no:cacheprovider --basetemp <scratch>/f2-green-temp (PYTHONDONTWRITEBYTECODE=1; f2-green.log).
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: F3 write immutable semantic-map identity/publication regressions before production changes. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.


### Standards fixes F3 RED (2026-10-07T05:22:03.5026300+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M backend/bintanong_tools/prospectus_extractor/ledger.py;  M plans/plan_current_progress/extractor_split_progress.md;  M tests/test_prospectus_input_snapshot.py;  M tests/test_prospectus_ledger.py;  M tests/test_prospectus_materialise.py.
- Result: 4 failed, 2 passed, 11 deselected; exit 1; map edits/deletion/appearance publish and transient edit mislabels metadata under original digest. Command: py -3.13 -m pytest tests/test_prospectus_input_snapshot.py -k semantic -q -p no:cacheprovider --basetemp <scratch>/f3-red-temp (PYTHONDONTWRITEBYTECODE=1; f3-red.log).
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: Capture semantic bytes via InputSnapshot, parse captured text with metadata owner, pass same capture to run_identity, check map bytes/presence before publication. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.


### Standards fixes F3 GREEN (2026-10-07T05:23:04.2020195+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M backend/bintanong_tools/prospectus_extractor/identity.py;  M backend/bintanong_tools/prospectus_extractor/ledger.py;  M backend/bintanong_tools/prospectus_extractor/metadata.py;  M backend/bintanong_tools/prospectus_extractor/pipeline.py;  M plans/plan_current_progress/extractor_split_progress.md;  M tests/test_prospectus_input_snapshot.py;  M tests/test_prospectus_ledger.py;  M tests/test_prospectus_materialise.py.
- Result: 212 passed; exit 0; captured input, identity, cache, skip and publication files. Earlier green selection error: nonexistent historical test_prospectus_runs.py, exit 4, no tests; preserved f3-green-selection-error.log. Command: py -3.13 -m pytest tests/test_prospectus_input_snapshot.py tests/test_prospectus_identity.py tests/test_prospectus_cache.py tests/test_prospectus_batch_skip.py tests/test_prospectus_publish.py -q -p no:cacheprovider --basetemp <scratch>/f3-green-temp (PYTHONDONTWRITEBYTECODE=1; f3-green.log).
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: Self-review diff and update two existing decision notes; report uncommitted batch to root for broad gates/review/commits. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.


### Standards fixes IMPLEMENTER HANDOFF (2026-10-07T05:24:24.2172574+08:00)
- HEAD: 407813c1fad100bceb662a129d2c64321791bc8f; dirty paths:  M backend/bintanong_tools/prospectus_extractor/identity.py;  M backend/bintanong_tools/prospectus_extractor/ledger.py;  M backend/bintanong_tools/prospectus_extractor/metadata.py;  M backend/bintanong_tools/prospectus_extractor/pipeline.py;  M docs/decisions/prospectus-cache-and-publication.md;  M docs/decisions/prospectus-status-separation.md;  M plans/plan_current_progress/extractor_split_progress.md;  M tests/test_prospectus_input_snapshot.py;  M tests/test_prospectus_ledger.py;  M tests/test_prospectus_materialise.py.
- Result: Exactly three fixes implemented; F1 red3failed2passed -> green141passed; F2 red5failed -> green351passed; F3 red4failed2passed -> green212passed. No broad gates or commits run by implementer. git diff --check passes. Command: See external report.md and f1/f2/f3-red/green.log for exact commands and actual results; all pytest invocations py -3.13, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider, basetemp under standards-fixes.
- Scratch: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\standards-fixes; running processes: none at boundary.
- Next: Root pins current dirty code; run fresh full gates and independent scoped specification/standards reviews; only root commits explicit logical paths after gates. Implementer will make no further edits. Root broad gates and logical commits pending; human trial/approval/real-photo gates pending.


## Implementer report (final; all edits UNCOMMITTED)

HEAD 407813c1fad100bceb662a129d2c64321791bc8f; worktree C:\Users\Hawksprey\source\repos\Bintanong-wt\publish-a-d. No live test processes at handoff; no agents, installs, commits, pushes, merges, branch changes, dev/main writes or institutional source modifications.

F1: ledger.split_stale and content_review_state reuse placement.unclaimed_items with no PDF pages, preserving PDF-only decision semantics and the sheet/verifier's covered-anomaly policy. Regressions cover undecided, accepted, unresolved, another PDF and stale old-value decisions. Files ledger.py + test_prospectus_ledger.py; status-separation decision paragraph documents behavior.

F2: materialise rebuilds authority through build_authority using inherited source/identity gates and reclassified courses; refreshes top-level content_review and authority.content_review_detail. It marks authority/extraction_audit stale and unconditionally blocks eligibility with derived_sections_stale. Verified synthetic source stays verified; pending stays pending. No source approval is manufactured. Regressions cover no-change and incomplete corrections for verified/pending sources plus fresh ledger evidence. Files ledger.py + test_prospectus_materialise.py; status-separation decision paragraph documents behavior.

F3: semantic-map bytes captured through InputSnapshot once, parsed through parse_semantic_markdown(text=...), passed as semantic_map to build_payload, and their same snapshot supplies run_identity digest. The prepublication guard compares bytes and detects missing-map appearance. Regressions cover equal-size/restored-mtime mutation, deletion, absence->presence, transient edit+restore, unchanged absent/present maps and two-value loader compatibility. Files identity.py, metadata.py, pipeline.py + test_prospectus_input_snapshot.py; cache-and-publication decision paragraph documents behavior.

Tests were written and authentically failed before each corresponding production change. No reconstructed RED. Focused commands (all from isolated worktree; PYTHONDONTWRITEBYTECODE=1; all below append -q -p no:cacheprovider --basetemp "$SCRATCH/<name>-temp", where $SCRATCH is this report's standards-fixes directory):

- f1-red: py -3.13 -m pytest tests/test_prospectus_ledger.py -k persisted_anomalies; 3 failed, 2 passed, 10 deselected; exit 1.
- f1-green: py -3.13 -m pytest tests/test_prospectus_ledger.py tests/test_prospectus_b2_codex_review.py tests/test_prospectus_b2_review_fixes.py tests/test_prospectus_sheet.py; 141 passed; exit 0.
- f2-red: py -3.13 -m pytest tests/test_prospectus_materialise.py -k "stale_authority or top_level_review_status"; 5 failed, 9 deselected; exit 1.
- f2-green: py -3.13 -m pytest tests/test_prospectus_materialise.py tests/test_prospectus_authority.py tests/test_prospectus_ledger.py tests/test_prospectus_b2_codex_review.py tests/test_prospectus_b2_review_fixes.py; 351 passed; exit 0.
- f3-red: py -3.13 -m pytest tests/test_prospectus_input_snapshot.py -k semantic; 4 failed, 2 passed, 11 deselected; exit 1.
- f3-green: py -3.13 -m pytest tests/test_prospectus_input_snapshot.py tests/test_prospectus_identity.py tests/test_prospectus_cache.py tests/test_prospectus_batch_skip.py tests/test_prospectus_publish.py; 212 passed; exit 0.
- f3-green-selection-error.log: first green command used historical nonexistent tests/test_prospectus_runs.py instead of current tests/test_prospectus_cache.py; no tests ran, exit 4. Corrected command above then passed; failed evidence retained.

Final git diff --check exit 0. Line-ending normalization warnings only from Git; no pytest warnings observed in focused runs. Focused counts overlap; do not add them. Sixteen additional parametrized cases total. Previous root 997/13/5 and other broad numbers are stale for this changed code until root repeats appropriate gates.

Dirty paths at handoff:
backend/bintanong_tools/prospectus_extractor/identity.py
backend/bintanong_tools/prospectus_extractor/ledger.py
backend/bintanong_tools/prospectus_extractor/metadata.py
backend/bintanong_tools/prospectus_extractor/pipeline.py
docs/decisions/prospectus-cache-and-publication.md
docs/decisions/prospectus-status-separation.md
plans/plan_current_progress/extractor_split_progress.md
tests/test_prospectus_input_snapshot.py
tests/test_prospectus_ledger.py
tests/test_prospectus_materialise.py

Ruling carried from task brief: every materialised review artifact defaults non-executable, including no-change reviewed candidates, because audit/Prolog/RAG remain stale. Cost: a no-change materialised review artifact must still be re-derived before execution; deliberate requirement, not a new institution approval rule or schema bump.

Self-review: every changed production owner/caller read; anomaly policy reused; correction effects reclassified and source gates retained; semantic metadata never reopens map during process_prospectus. Original standalone build_payload/run_identity and loader interfaces remain compatible with additive optional keywords. No whole-corpus retention.

Remaining work: root fullsuite/comparer/selftest/corpus/trial gates as appropriate, independent scoped spec/standards reviews, then root-only explicit-path logical commits. Human PDF/photo comparison, human B2 Tasks 12-14 and source/institution approval remain pending. No accuracy/readiness claim. Implementer makes no further edits after this report.
