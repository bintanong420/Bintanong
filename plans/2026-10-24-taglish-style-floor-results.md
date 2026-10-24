# Taglish reply style (24.2): results, 24 October 2026

Owner path, 23 Oct: "lets go with what u recommend. we are going to super polish it". That means (1) the
closed-class English floor and (2) one bounded style-prompt trial, tuned only on a fresh practice set (ledger entry).

## Built

- `floor_style` (`backend/bintanong_routing/style.py`), commits `3eb4f59` and `6abfb40`.
- A `filipino` label becomes `taglish` when the message has a literal English grammar or number word: articles,
  prepositions, conjunctions, wh-words, auxiliaries, one to ten, first to fifth, last, next.
- Never counted:
  - Filipino lookalikes (at, may, na, pa, no), and "of", which mostly sits inside borrowed terms such as
    "transcript of records".
  - quoted text, catalog names, Title Case names (course titles such as "Microbiology and Parasitology"), and
    all-caps acronyms.
- The original 22 Oct floor (`english_only` to `taglish`) is unchanged.

## Style-prompt trial (not adopted)

- Practice set: 20 fresh questions in workspace `audit-evidence/p11-20261023/style-practice/`. No roster wording;
  labels follow the AGENTS.md register rule.
- Results:

  | Prompt | Taglish (8) | Filipino (8) | English (4) |
  | --- | --- | --- | --- |
  | committed v1 | 1 | 7 | 4 |
  | v2 (register rule) | 1 | 7 (one became `unknown`) | 4 |
  | v3 (quote every English noun) | 0 | 7 | 4 |

- Gemma 4 E4B does not quote English nouns ("class card", "library") in casual Filipino. A likely cause: the
  constrained JSON lets it close `english_fragments` as `[]` before any style reasoning. Not adopted.
- The practice set also caught one floor false positive ("of" in "transcript of records"), fixed in `6abfb40`.

## Counted roster run 16 (same harness and settings as run 15; HEAD `6abfb40`; hosted 39-curriculum release)

| | Run 15 | Run 16 |
| --- | --- | --- |
| Status/decision changes | none | **0 of 63** |
| English replies in English | 21/21 | 21/21 |
| Filipino (`-tl`) replies in Filipino | 21/21 | 21/21 |
| Taglish replies in Taglish | 10/21 | **15/21** |
| Answered | 25 | 25 (23 texts byte-identical) |

- The 5 flips are exactly the ones predicted offline.
- The 2 changed texts keep the same facts and evidence ids, now in Taglish (4.0/INC one-year rule; P50.00
  sticker fee).
- Median outer time: documents 26.2 to 28.9 s, structured 16.3 to 18.8 s. My CPU-bound photo OCR ran during part
  of this run, so the timing is not a clean latency comparison.

## Remaining limit (disclosed)

Six Taglish questions still get Filipino replies. They differ from their owner-accepted Filipino twins by register
only ("pwede/pasado/bagsak" vs "maaari/naipasa"), with English nouns that the Filipino twins also use. Neither a
word list nor the three prompt versions separates them.

This counted rerun is not an independent measure: the floor was checked offline against the same roster. Phase 12's
separate multi-turn and language families are the independent check.
