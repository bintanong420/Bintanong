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
