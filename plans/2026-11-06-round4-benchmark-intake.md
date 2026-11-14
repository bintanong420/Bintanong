# Round 4 owner benchmark intake

Read-only import: `E:/Hawksprey/Downloads/Bintanong_AI_Export_2026-11-06_1733.csv`.
SHA256 `3183d7d8f23f3c0d656f51d8e3aa5fe6cbe0c1309c12855d0b17715ac6d1470b`.
72 unique rows,30 columns. Owner marks, not independent accuracy adjudication.

| Stage | Y | P | N | Blank |
|---|---:|---:|---:|---:|
| Phase4 | 62 | 6 | 1 | 3 |
| Final | 63 | 0 | 0 | 9 |
| Latest retained | 63 | 6 | 0 | 3 |

Latest per-language distribution is21Y/2P/1blank each. All21 actually tested Round3
variants were retested in Phase4:20Y remainY and B13TL changesN toY. Phase4 adds48
previously unmarked variants. No prompt/roster or Round3-mark edits found.

- B20 good moral and B23 gate pass: all languages P; Final blank. Good-moral Final
  note `#REF!` is an export artifact, not an additional behavioral failure.
- B12 shifting TL: Phase4N -> FinalY. All three Final notes request less verbosity.
- B15 grade4: allY, qualified by note that removal-form location exists in Charter;
  Taglish question is a compound stress case. Investigate the omitted source location.
- A07 all languages untested because curriculum chat locking prevents the test.
- No commit/release/port fields identify a frozen candidate. Main/dev note is inherited
  from Round3, not a new Phase4 note. Do not call this a fresh complete72-case run.

Detailed source-derived comparison remains ignored at
`audit-evidence/benchmark-fixes-20261106/round4-audit.json`. Inputs unchanged.
