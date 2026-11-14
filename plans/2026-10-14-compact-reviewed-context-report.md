# Compact reviewed context — 14 October 2026

Implementation `03f757f` and correction `2437f28`, after plan `5b5c14b`, removes repeated validation metadata
from an opt-in v2 display format. All 77 selected inactive previews now fit the
pinned 512-token encoder without changing source wording or partitioning records.
This continues Phase 05; source-governance and approved retrieval gates remain open.

| Selected preview | Previous exact tokens | Compact exact tokens |
| --- | ---: | ---: |
| Charter page103 step3 | 563 | 466 |
| Complete handbook approval footer | 389 | 292 |
| Largest of all77selected previews | 563 | 466 |

Exact counts include special tokens, use the unchanged empty document prompt and
disable truncation. All77counts range111..466; zero overflows. This measures the
selected reviewed previews, not the whole source corpus or assembled query context.
No document vectors, ranking observations, retrieval scores or LLM answers produced.

## Compatible representation and validation

`build_reviewed_policy_chunks(..., include_source_limits=True, compact_context=True)`
selects paired `reviewed-policy-fields-v2` and
`palsu-reviewed-policy-context-chunker-v2` markers. Both flags require booleans;
compact mode requires source-limit context. Default/plain and v1 output is unchanged.
The renderer still accepts v1 and checks that each format/chunker pair agrees.

v2 displayed limits omit only duplicate `visible_text`, `source_sha256`, `version_id`
and `span_indexes`. Fields already retain the complete visible source values;
resolved citations retain source/version/page/locator identity. Gap IDs, issue,
affected claims, fixed unresolved messages, locators and extra evidence remain
displayed. Group display omits the validation-only original record manifest.
A compact `evidence_sha256` binds the canonical full stored source_limits and
service_group whenever either exists. This retains exact integrity of omitted
metadata, including original visible fragments and manifest presence, without
repeating their full contents. It is an integrity binding, not source authorization.

Complete source limits, field associations, spans and group manifests remain in
stored metadata. Before accepting context, the consumer rechecks source text,
content hashes, ordered complete field/span bindings and regenerated full limits,
then compares exact serialized text under the declared codec. Record groups still
reconstruct original gap hashes across complete mandatory members. Missing/tampered
metadata or incompatible markers withhold evidence; there is no plain-text fallback
for a marked invalid record. Whole-group order and exact context budgets remain.

The opt-in representation preserves immutable v1 chunks and default adapter results.
It supplies no governance transition or new interpretation. This implements the
owner's technical continuation without reopening settled source-content decisions.

## Actual evidence and preservation

Ignored packet:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-compact-reviewed-context-20261014/`.
`replay_actual.py` reads the unchanged owner-selected77-reading bundle and its
232span map. Original source hashes, all16review events, pending registers and
original bindings are checked through the existing adapter. A temporary profile
hook captures serializer return values without changing unknown applicability or
emitting chunks. Saved plain and v1 outputs compare exactly with their prior files.

All77v2previews retain identical source_text, every full association/span/source
limit/group, and every displayed source field. The original Charter step3 and its
cutoff after "for" remain unchanged. Its limitation is still displayed. The full
owner-selected approval footer and printed2021metadata/history remain unchanged.
264selectedfields,29sourceblanks,232spans, seven logical gap groups and ten projected
gap-bearing parts remain. All77applicability declarations stay unknown: zero chunks,
activationfalse. No original conversion or source-content review repeated.

The prior21-file owner packet/seal is immutable. Of921recorded dependencies,
917files still have their recorded hashes; four tracked code files intentionally
change in this increment. Their exact old checkout bytes are saved separately and
matched to the prior hashes and Git845abff (explicit LF/CRLF representations).
Earlier seals are not rewritten. The previously documented historical guide drift
remains an observed baseline, not a claim that the older original hash now matches.

Original handbook SHA256:
`4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8`.
Original Charter SHA256:
`42a93994e1467df0f32c7038d1c21f638c23ac0f1dee984463acf56caf526529`.
External SEA-LION weights/revision SHA256:
`df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1`.
Existing model/configuration asset hashes and package pins are in model-binding.json.
Strict QueryEncoder verifies those assets before counting; no fallback estimation
or network/model/dependency change. MODELS remains external at C:/Coding-projects/MODELS.

## Verification and review

- Seven new synthetic tests: RED14reported failures including subcases from the
  missing option,0.95s; GREEN7tests/19subtests,0.54s. Fixture helper corrected to keep
  explicit extra gap evidence. Fields/warnings/full stored limits, strict flags,
  unknown scope, version mismatch, stripped markers, tampered full limits, stored
  spans, complete group manifests, child-first order and budget withholding covered.
- Relevant reviewed/retrieval regressions:100passed/125subtests,2.01s,exit0.
- Initial actual plain/v1/v2 replay: PASS26.802s; preliminary111..412counts retained
  separately from the corrected outputs.
- One fresh reviewer found two Important, no Critical/Minor: deleting all stored
  manifests bypassed reconstruction, and a valid contained-substring visible_text
  change was not bound to v2 text. Root reproduced both:9tests RED2failures/7pass,
  0.74s; integrity binding correction ->9GREEN/19subtests,0.56s. Related final:
  102passed/125subtests,1.96s. One correction pass, no second review/deferred findings.
- Reviewer independent pre-fix replay:917stable hashes/four historical snapshots,
  21prior sealed files, two original PDFs/16events, all77counts/full evidence and
  exact default/v1 compatibility;10other negative probes reject. Focused42tests/
  59subtests pass1.28s. Trust limited to selected inactive preparation and caller
  annotations; hashes authenticate neither institutional authority nor coordinated
  replacement of both stored data and text.
- Corrected replay PASS24.08s under separate `post-fix/` outputs:111..466exacttokens,
  Charter466/footer292, zerooverflows. All full stored evidence remains equal to
  original input; only evidence_sha256 is added to preliminary v2 payloads. Every
  digest independently recomputed from full limits/groups; default/v1 equal saved.
- Pre-correction full suite:5162passed/377subtests/6skips/6warnings320.68s,exit0,
  retained as history. Final corrected full suite:5165passed/377subtests,
  6skipped/6warnings,308.86s,exit0; phase-ledger19passed11.410s. Skips include
  unavailable Windows symlink privileges; warnings remain existing upstream/test
  warnings. Raw full logs/exit files are retained without rewriting the first run.
- Evidence manifest seals47files and seven current code digests; SHA256
  `ea1e2a7acb40a704df7cf1ddab207449c41baf1eefdda1ee193d651d39f7bf5d`. Both original sources,
 917stable input hashes and historical exact code snapshots are preserved.
  Final documentary/phase/seal checks follow below.


Existing approved Python3.13.7 venv:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
Full command: `python -B -m pytest tests -q -p no:cacheprovider --basetemp
<packet>/pytest-full`; existing offline HF/Docling assets, workspace TEMP/TMP,
OMP/MKL8threads. No shared/hosted database changes; existing disposable fixtures only.

Thesis physical17–18/36, routingPNG, master10, active/prior handoffs and scope/gap
policies consulted; no discrepancy. Human-in-the-loop rule remains inAGENTS. No
incoming collegeCharter/memo/miscellaneous batch processing or source acquisition.

## Next action

The bounded sizing/validation correction is complete. Continue actual source governance and approved development-case evidence recovery, then retrieval
calibration, using available authorizing decisions rather than inferred approval.
Preserve unknown authority/currentness/applicability and known source limitations.
No repeated transcription reviews, missing-ending reconstruction or new intake.
Preview sizing and synthetic tests do not authorize activation or Phase06.

Final documentary checks:400passed1.31s; phasevalidateexit0/can-advanceexit1(expectedblocked). All47sealed file hashes/sizes, seven code digests and manifest hash match; gitdiffcheck passes. Seven curated paths only; documentary commit follows inGit.
