# Owner benchmark repairs — 6 November 2026

Bounded repair work on `p12-dev` / `p12-post-gathering-fixes`, starting `730344e7`.
No new numbered phase, corpus activation or dependency/model change. Main gathering checkout stays separate.

## Evidence and acceptance

- Owner CSV: `E:/Hawksprey/Downloads/1_Bintanong 72 bench queries test log.csv`, SHA-256
  `293bc578ab3a41066825bdf3544596abe6e95f0f974d8eb70bf2322fba950273`.
- PDF edition 4: SHA-256 `be467633c1429dc72b49e473d4633f81045f340859dd86f0d167ff368577a9a3`;
  same 24 rows / 72 variants as the [existing run](2026-11-05-live-language-browser-results.md).
- Marks: 47 Y, 8 P, 14 N, 3 blank. Row 7 was not tested because program selection is mandatory.
  These are owner marks, not independent adjudication or a newly measured accuracy score.
- Owner confirmed these results came from 3217, whose temporary rate-limit override works.
  Do not modify main/public limits or reopen that resolved issue.
- Consulted thesis physical 17–18, 39–44, runtime routing PNG, master section 3, current handoffs,
  undergraduate/source-gap policy and owner decisions. Preserve advisory scope, structured course reasoning,
  English/Taglish replies and existing deadline discrepancy readings. No architectural discrepancy identified.

## Repair order and reach

1. Course identity: row 9 cannot list a reviewed named course's prerequisites. Inspect literal extraction,
   scoped catalog binding and router validation; reuse existing routing tests with synthetic curricula.
2. Document selection: rows 10, 13–19 vary by language or choose the wrong topic/claim. Trace selector,
   interpretation and evidence separately; fix a demonstrated shared failure, not benchmark phrase routing.
3. Procedure completeness: rows 23–24 omit application requirements or substitute a library-specific service.
   Preserve original source limitations; establish applicable service coverage before changing claims.
4. Reply quality: row 8 should answer listing directly; Taglish wording and unrelated service prose need
   review at the shared generation seam. Source quotations retain their printed English.

For each slice: reproduce, failing public-boundary regression, smallest fix, related regressions, then a
bounded live rerun of affected variants. Keep evaluation questions out of prompt examples. Do not infer
source approval from a CSV expected-answer cell, or count a clarified source ambiguity as a fixed procedure.
Raw traces and original-source evidence remain ignored under workspace `audit-evidence/benchmark-fixes-20261106/`.

## Current state

Row 9 live router trace resolved `Forensic 3/L` but rejected the program phrase `BSCrim student`: the catalog
contains `BS Crim`, not its compact spelling. Shared program-alias matching now allows omitted whitespace
within a reviewed alias; whole-word boundaries, ambiguity and selected-scope checks remain. No course alias
or source data changed. Synthetic public validation regressions: corrected RED 6 failed / 5 passed;
GREEN 11 passed. Related validation/compiler/program-switch/catalog suite: 217 passed.
Commands use existing Python 3.13 venv, `-m pytest`, `-p no:cacheprovider`, external `--basetemp` beneath
the raw evidence directory. Bare `python` resolves to an unrelated environment; system Python lacks pytest.
No install was performed. Test files: `test_routing_program_spacing.py`, `test_routing_validation.py`,
`test_routing_compile.py`, `test_routing_program_switch.py`, `test_routing_catalog_separation.py`.

Next: finish real-router Forensic variants and isolate document selection/evidence failures. Existing
72-turn evidence is reused rather than repeating the whole benchmark before identifying causes.
