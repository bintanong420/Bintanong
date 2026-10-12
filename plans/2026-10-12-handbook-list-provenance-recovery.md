# Phase05 bounded handbook list provenance recovery

Continuation of `2026-10-12-phase05-policy-candidates-handoff.md`, resumed from
clean `29b2e89`. Preserve all existing originals, candidate bundles and evidence.
This is supplemental source recovery within Phase05; formal exit stays blocked.

## Evidence and decision

All1546 invalid-range rejected handbook items have one provenance range exactly
covering `orig`; their list-item `orig` equals the explicit marker, one space and
`text`. Installed Docling2.133.0 list-marker processor strips the marker from
`text` without updating provenance. The reader currently indexes those ranges
against the shorter `text`. Context7 Docling Core documentation was consulted;
the installed processor provides the version-specific behavior evidence.

Ruling: preserve marker-bearing `orig` only for this exact, fully located list
relationship. Keep other transformations, partial ranges, multiple provenance
entries and the10 existing incomplete-range items under existing refusal guards.
Cost if wrong: a candidate original-text choice would need revision; no source
approval or active publication follows from this repair.

## Steps and verification

1. Verify45 dataset entries and63 handbook/70 Charter sealed files before edits
   to product code or saved-byte replay; capture new evidence separately.
2. Write synthetic tests for original list-marker retention and refusal of
   mismatched/partial provenance. Observe the positive regression RED.
3. Select exact fully covered list `orig` consistently for units and spans;
   preserve raw JSON and provenance unchanged. Run GREEN and relevant regressions.
4. Commit a small verified implementation and record commands/results here and
   in the checkpoint/current progress. Reuse existing isolated environment.
5. Replay verified retained raw through the existing pipeline into a new ignored
   directory. Check complete bundle, byte identity, accounting and original-backed
   samples; preserve unresolved grades separately without editing sealed bundles.
6. Run the product suite without pytest cache and with external basetemp; review
   the bounded change, record results, update the exact next action and commit.

No new PDF conversion, installation, dependency/lock change, model download,
institutional approval, runtime activation or Phase06 work is authorized here.

## Progress

- Resume: instructions/context/Git reviewed; root cause and exact1546-item
  relationship established. Source/evidence preservation verification next.
- Preservation:45 original dataset entries and all63 handbook/70 Charter sealed
  files unchanged. Diagnostic evidence lives in workspace
  `audit-evidence/p05-list-provenance-recovery-20261012/`;11 original-bbox samples,
  9 whitespace-exact,2 pending content/typography review. Exactly1546 handbook
  interpretations change,0 Charter interpretations change.
- TDD:3 original-list regression failures/6 guard passes0.79s. Minimal guarded
  original-text selection implemented. Additional exception attachment regression
  failed0.49s, then detection kept on marker-free text while cited text preserves
  the original marker. Final120 policy/procedure/chunk tests pass17.70s.
- Broader ingestion suite215passed/3skipped/1warning52.05s before exception fix.
  Initial environment-only integration failure retained in `list-green.log`;
  corrected offline workspace environment passes in `list-green-offline.log`.
  First GREEN attempt named nonexistent pipeline/bundle modules and collected
  no tests; actual repository paths were used afterward.
- Next: full product verification, fresh saved-byte candidate replay, read-only
  bounded review and updated source findings. Existing bundles stay immutable.
- Candidate replay `ba6752f`:4272chunks,4154covered/10rejected/1567omitted text,
  115emitted/18rejected tables;401.998s. New bundle independently checked;2726old
  chunks are identical and1546original list items are newly covered.45original
  entries and63+70sealed files unchanged; Charter427chunks still validates.
- Full `ba6752f` gate:4947pytest/107subtests pass463.12s,6skips/6warnings; phase
  ledger19passes16.330s.26original grade rows checked with native character geometry.
  Remaining10refusals have whitespace gaps; retain unchanged strict refusal.
- Independent GPT-6.1 Sol review:120focused tests pass18.92s. OneP2 procedure-field
  recognition regression reproduced5RED cases0.73s and fixed;156related tests/
  1skip passed24.12s. Marker-only empty content also reproduced RED0.51s and
  omitted under a nonempty-content guard.16final correction regressions pass0.69s.
- Final: fixed procedure labels and marker-only phantom clauses; final full-code
  gate still pending. Reviewer exclusions: source accuracy/grading, authority/
  activation/retrieval and executor's full replay evidence require separate gates.
  They remain explicitly pending or independently verified by the executor;
  withholding these claims costs no authority promotion. No minor findings.
