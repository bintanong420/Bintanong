# Prospectus status separation (Phase C)

Date: 4 October 2026. Branch `feat/prospectus-phase-c-status-separation`, created from `6846da4` (the tip of the unmerged Phase B2 branch, not `dev`). Plan: `plans/2026-10-03-prospectus-phase-c-status-separation.md`. Schema version `palsu-prospectus-v3.1`; the compact essentials file is `palsu-prospectus-essentials-v2`; the batch manifest version is unchanged.

## The three states

A machine audit of `ok` or `warn` can no longer be read as approval. The payload carries three separate strings:

| Field | Set by | Values the extractor can produce |
| --- | --- | --- |
| `extraction_audit` | The extractor's own checks (`audit.status`) | `ok`, `warn`, `error` |
| `content_review` | `ledger.content_review_state` when a decision ledger and a source hash are passed; otherwise a constant | `pending`, `partially_reviewed`, `reviewed` |
| `source_verification` | The source record (`ProvisionalSource.source_verification`) | `pending` (the record is fixed to `pending`; with no record the field is `pending` too) |

`audit.promotion_status` keeps its old values (`VERIFIED` for `ok` and `warn`, `REVIEW_REQUIRED` for `error`) because existing readers use it. It means only that the extractor's checks found no error. It is not approval of the curriculum, the source, or any eligibility result. The code comment at the label, the package docstring, and `authority.note` in every payload say so.

The `authority` block holds the source record (`pdf_sha256`, `source_locator`, `pdf_hash_check` of `not_checked` or `matched`), the identity check, the ledger summary when one was used (`content_review_detail`), `eligibility_executable`, the list `blocked_by`, and a count of courses whose prerequisite rule is incomplete. `eligibility_executable` is true only when `blocked_by` is empty. Because `ProvisionalSource` never leaves `pending`, it is false for everything the extractor produces today.

`content_review` reads the Phase B2 ledger only when `review_entries` and a `source` (for its `pdf_sha256`) are both passed to `build_payload` or `process_prospectus`. Entries recorded against a different PDF hash do not count. `reviewed` removes only the content-review blocker. It still means a person decided every row, not that the content is right.

## Source and identity

`source=` and `approved_scope=` are keyword-only and optional on `build_payload` and `process_prospectus`, so existing callers are unchanged. The source is duck-typed (`pdf_sha256`, `source_locator`, `source_verification`, `verify_pdf`) because the package must keep running when started by path and cannot import the tools adapter. For a PDF input `process_prospectus` calls `source.verify_pdf` before any output is touched. A hash mismatch raises `ValueError`, so nothing is deleted or overwritten. For a cached Docling JSON input no hash can be checked and `pdf_hash_check` stays `not_checked`.

`approved_scope` is a mapping of metadata names to approved values (for example `campus`). With none supplied, identity is `pending`, which is a state and not an audit error. A difference gives `mismatch` and the blocker `identity_mismatch`.

Metadata keeps every old key and value, including the hardcoded campus `Tiniguiban - Main`. `metadata["observations"]` adds, for campus, college code, program name, and school year, the value, the basis it came from, the evidence text, and the status `candidate`. The campus is labelled `extractor_default` with no evidence, so it reads as an assumption.

## Prerequisite state

Every course gains `prerequisite_state`. The parser cannot tell a printed-blank cell from a missing cell from an unread one: `sections._field_at` returns `None` for all three and `_candidate_to_raw_course` turns that into an empty string. So the extractor can never prove "reviewed empty". It emits:

| State | Meaning |
| --- | --- |
| `resolved` | Text present and every token resolved to a course code. |
| `stated_none` | The cell literally says none, a dash, or n/a. Printed evidence of an empty rule. |
| `blank_unreviewed` | No text. Printed blank, missing cell, or unread; indistinguishable. |
| `standing_condition` | A standing, percentage, consent or similar rule is present. |
| `unresolved_reference` | A token was left over after resolution. |
| `alternative_or_exception` | The wording has or, either, except, unless, equivalent, provided, or if. Caught by wording because the parser folds `or` into the unresolved list and would otherwise execute it as AND. |
| `unreadable` | The audit flagged the cell as an ambiguous fragment, or text is present and nothing in it was recognised. |
| `reviewed_empty` | Reserved for a human decision. Never emitted by the extractor. |

Only `resolved`, `stated_none` and `reviewed_empty` are executable. A printed none is source evidence of an empty rule; a blank is not. Delete `stated_none` from `EXECUTABLE_PREREQUISITE_STATES` to be stricter. Consequence: with extractor output alone almost every first-year course (blank cell) is `blank_unreviewed`, so `eligible/2` offers little until a reviewer confirms the blanks. That is the point.

The Prolog gains `prerequisite_state/2` and `rule_complete/1`, and `eligible/2` requires `rule_complete/1`. Before this phase `eligible/2` ignored standing requirements and unresolved prerequisite tokens: a course with prerequisites `CS 9, CC 1` and `CS 9` unresolved counted as eligible once `CC 1` was passed. A test runs `next_eligible/2` under SWI-Prolog and skips when `swipl` is absent.

## Blocked audits

When the audit is `error`, `build_payload` already replaced Prolog with an empty `blocked` object and RAG with empty lists. Phase C adds a regression test and adds the two new relation keys to the empty object so its shape matches. Courses, the term tree and the prerequisite edges stay in blocked payloads as extraction candidates.

## Other changes

`audit.py` listed detected terms and years from a set sorted by index alone, so Summer and Mid-Year (same index) could swap with the hash seed. The sort now breaks ties on the year and semester text.

## Review fixes (4 October 2026)

The classifier now accounts for all of `prerequisites_raw`: after the resolved codes (spacing, a leading zero and a lab marker may differ), recognised standing rules and separators are removed, any leftover text makes the state non-executable (a units or grade condition with a number is `standing_condition`, `|` or `/` between codes is `alternative_or_exception`, anything else `unreadable`). Extracted course values are unchanged. `source_verification` must be exactly `verified` and `pdf_hash_check` exactly `matched`; anything else blocks (`source_not_verified`, `pdf_hash_not_checked`). A positive test shows `eligibility_executable` is true when every gate is satisfied. An approved field whose observation basis is `extractor_default` gives identity `unverified` (blocker `identity_unverified`), never `consistent`. A ledger passed without a source is recorded in `content_review_detail` as ignored. The status-field report is now `--status-report` on `scripts/prospectus_course_compare.py`.

## Known limits

Blank cells cannot be told from missing ones. `unreadable` in a payload whose audit is not `error` only comes from "text present, nothing recognised". The review CSV does not show `prerequisite_state`. The batch manifest does not carry the three states.

## Regression result

Run on 4 October 2026 over the 44 cached Docling JSON files (`task2b_standing_isolated_2026-09-29`), old side `6846da4` against this branch, with `scripts/prospectus_course_compare.py --base-ref 6846da4 --jobs 4` (semantic map `palsu_main_undergrad_program_college_meaning.md`). That comparer checks course fields, audit counts and exit codes, and the markup cell ids: `44/44 identical`. A second field-level diff over every payload key (a scratch script, not committed) gave exactly the expected table; nothing else changed, removed or moved, and the old and new `terms_detected` are equal:

```
changed      6  prolog.clauses            (the 6 non-error audits: 1 ok, 5 warn)
changed     44  schema_version
added       44  authority, content_review, extraction_audit, source_verification, metadata.observations,
                prolog.relations.prerequisite_states, prolog.relations.rule_complete
added     2031  courses.[].prerequisite_state
added     2031  curriculum_by_term.*.*.[].prerequisite_state
```

38 payloads still have `prolog.status = blocked`. Audit and label mix: 38 `error`/`REVIEW_REQUIRED`, 5 `warn`/`VERIFIED`, 1 `ok`/`VERIFIED`; all 44 have `content_review` and `source_verification` of `pending` and `eligibility_executable` false. Prerequisite states over 2031 courses (after the review fixes below): blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, alternative_or_exception 3, stated_none 2. The first run of this phase had resolved 696, standing_condition 58, unreadable 14: seven courses moved out of resolved because the parser had silently dropped text from their cell (ENTRE 15 "ENTRE 14 units: 159", CLJ 5 "3rd year CLJ 4", TPS 1 and 2 "THC-Mktg & GE Elect: ...", NCM 15-113 "GE- Elect: ES", BES 7 "GE-Elect: EM", AMR 2 "GE: MMW").
