# Independent specification review — publication A–D

Reviewed base `36d89b412ba8144f8a98a8fef85899c103ebadc0` through `40801acb7eab5dec4dfa6c6b437da6f9b4c3ae38` (original assigned tip `6579483`; the additional commit removes test whitespace only). Root changes made after this tip are not approved by this initial report.

## Confirmed findings

- **P2 — PDF hash is omitted from the published markup.** `backend/bintanong_tools/prospectus_extractor/pipeline.py:255` calls the renderer without its `pdf_sha256` keyword. The renderer only reads that keyword, so even a Phase D payload containing the captured PDF digest says `pdf_sha256: not recorded`. Phase B plan D4 (`plans/2026-10-03-prospectus-phase-b-markup-twin.md:26`) defers display until Phase D passes the digest; the markup decision repeats that dependency. Pass the already captured `payload.run_identity.pdf_sha256`; keep JSON review inputs unverified. Reproducer F1 supplies a payload with a 64-character PDF hash to the actual staging helper: first line still prints `not recorded`.

- **P2 — Corrected courses retain stale prerequisite states.** `backend/bintanong_tools/prospectus_extractor/ledger.py:428` re-finalizes courses without running Phase C's annotation. The approved O1 extension (`plans/plan_current_progress/extractor_split_progress.md:96`) promises derived prerequisite fields follow corrections; Phase C's goal requires unresolved rules to remain non-executable. Reproducer F2 makes an honest ledger correction on CS 2 from `CS 1` to `CS 1, Ghost 99`: one correction applies and `prerequisites_unresolved` becomes `['Ghost 99']`, but stored `prerequisite_state` remains `resolved` rather than `unresolved_reference`. The existing Prolog generator then puts CS 2 in `rule_complete`. This state is not marked stale. Re-annotate **all** finalized courses, including siblings whose prerequisites become unresolved after a code correction. Preserve `audit.structural_anomalies` when annotating: text corrections do not prove ambiguous source-cell ownership was repaired. GUI-specific `reviewed_empty` handling remains outside publication scope.

## Evidence and limits

Executed `python "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\spec-reproducer.py"`: exit 0; both outputs above confirmed. Reproducer and its generated files stay in external scratch. No broad gate was rerun by this reviewer; root owns fresh suite, self-test and comparer verification. Root reported fresh system Python full suite 992 passed / 13 subtests; this report does not claim an independent rerun.

Other confirmed specification defects: **NONE**. Unconfirmed suspicions: **NONE** requiring publication blockage. Reviewed the A/B/B2/C/D plans, cross-phase rules, master source/review boundaries, and cache/publication decision. GUI and OCR implementation are excluded and their plans explicitly say unfinished; B2 Tasks 12–14 and institutional approval remain human/future gates, not claimed completed.

**CHANGES NEEDED — P2 markup hash; P2 materialised prerequisite states.**
