# Compact reviewed context implementation plan

> Execute inline with executing-plans/TDD, followed by one fresh independent review.

**Goal:** Fit the unchanged Charter step 3 within the pinned 512-token encoder by
removing repeated validation metadata from displayed text, while preserving full
stored evidence and all source wording/limitations.

**Spec:** Master section10; scope/source-gap/service policies; owner decisions in
2026-10-14-owner-source-handling-decisions.md. Owner says proceed. The footer remains
the selected full paragraph, with printed2021metadata. Charter original cutoff stays.

**Architecture:** Add an explicit opt-in v2 codec; retain v1 as the default and keep
its serialized output unchanged. The adapter chooses paired format/chunker markers.
The renderer checks that pair and revalidates full stored fields/spans/gaps before
accepting either version. v2 omits duplicate visible_text/hash/version/span-index
data from displayed limits, and validation-only record manifests from displayed
group metadata. Fields, warnings, affected claims, locators and other gap evidence
remain displayed; complete limits/manifests stay stored and checked.

**Environment:** Existing Python3.13.7/pytest/offline SEA-LION assets; no library or
dependency changes. Business-logic codec work, not library-specific API changes.

## Constraints and review focus

- Default/plain/v1 saved results remain unchanged; both old and new codecs validate.
- `compact_context=True` requires `include_source_limits=True`; strict bool flags.
- v2 markers: `reviewed-policy-fields-v2`, `palsu-reviewed-policy-context-chunker-v2`.
- All source text, literal blanks, accepted field associations, source cuts, currentness
  warnings, claims and original bindings remain. No field partition/selection change.
- New format never supplies governance, applicability, policy interpretation or
  activation. Actual77unknown readings remain zero chunks.
- Tampered/missing full stored gaps, incompatible format/version markers, incomplete
  groups/spans and insufficient context budgets fail closed without raw-text fallback.
- No original edits/conversions, repeat owner questions, new incoming data, installs,
  downloads, model duplication, shared DB/API/Docker/Prolog/deployment/push or Phase06.
- Ignored raw evidence under workspace `audit-evidence/p05-compact-reviewed-context-20261014`.
  Explicit staging and small verified Conventional Commits; retain old seals/history.

## Task — Versioned compact codec and consumer

Files: contracts/reviewed_policy_context.py; document_ingest/reviewed_policy_chunks.py;
retrieval/context.py; existing synthetic test_reviewed_policy_chunks.py and
test_reviewed_record_context.py. No new production module or storage schema.

- [x] RED: synthetic scalar v2 displays complete fields/warnings, stores identical
  full limits, keeps v1 unchanged; version/type mismatches and malformed metadata fail.
- [x] RED: v2 complete record groups omit displayed manifests but preserve and check
  them in storage; child-first order, exact budget, missing parts and altered hashes.
- [x] Implement minimal serializer format selector, paired chunker markers and adapter
  `compact_context=False` option; consumer supports both version markers. GREEN plus
  relevant context/adapter/regression tests, checkpoint and cohesive code commit.
- [x] Unchanged owner-selected77-reading input replay: default and v1 equal old saved
  outputs. Capture inactive v2 previews without changing unknown scope; compare every
  source field/span/event/limit/group and inspect displayed warnings/metadata omission.
- [x] Strict offline exact count all77previews, including special tokens/no truncation;
  verify Charter nowfits512, fullfooter/yearmetadata/sourcecuts/history unchanged.
  Preserve raw proof and original bytes; no actual context/retrieval accuracy claim.
- [x] One final independent review, one TDD correction pass if required, full product
  verification with existing offline assets, seal/report/decision/progress/checkpoint/
  INDEX/handoff closure. Phasevalidate passes; can-advance remains blocked.

Ruling: add a compatible opt-in representation rather than silently rewriting v1;
existing immutable chunks keep their validation rules. Removing only repeated
display metadata is a technical correction authorized by continuation, not a new
source-content decision. Wrong compaction could hide a limitation, so unchanged
full stored evidence and consumer regeneration are required regression targets.

Resume evidence: clean845abff, prior workflow06f6eef; thesis physical17–18/36,
routing PNG, master10, active checkpoint/plan/blocked handoff, previous complete
Phase04 and scope/gap policies consulted. No discrepancy; owner human-review rule
governs any future content decision, and answered source choices stay settled.

## Review correction ruling

Fresh review at03f757f found two Important omitted-metadata integrity cases. Bind
canonical full stored source_limits/service_group to v2 displayed text using one
evidence_sha256 when limits/group exist. This closes missing-manifest and valid
substring substitutions without retaining their full encoder overhead. Both regressions
observed RED and pass GREEN; corrected exact range111..466 (Charter466/footer292).
Hashes preserve the old text-to-metadata binding, not institutional authority.
One correction pass; preliminary evidence retained separately, no source choices.

## Final verified outcome

Compact context closed — 14 October2026. Plan5b5c14b, code03f757f/fix2437f28:
opt-in pairedv2markers, defaultv1 savedoutputs unchanged, fullstored fields/limits/
manifests preserved and bound by evidence_sha256. Full5165passed/377subtests/
6skips/6warnings308.86s,exit0; related102/125subtests1.96s; ledger19/11.410s.
One finalreview2Important/noCriticalorMinor; both reproducedRED andfixed inonepass,
9GREEN/19subtests0.56s, no secondreview/deferredfindings. Correctedactualreplay24.08s:
all77previews111..466tokens, Charter466/footer292, nooverflows/truncation/vectors.
264fields/29blanks/232spans/sevenlogicalgaps/tenprojectedparts unchanged,77unknown/
0chunks; originalChartercutoff/footer/yearmetadata choices remain.917inputhashes
unchanged; four intentionalcode revisions retain exacthistorical snapshots.
47files/sevencode digests sealed:
ea1e2a7acb40a704df7cf1ddab207449c41baf1eefdda1ee193d651d39f7bf5d.
Next actualsource-governance/approveddevelopment-case evidence and retrieval
calibration, preserving unknowns and existing approval boundaries. Do not repeat
answered source reviews, unavailable-ending reconstruction, equivalent partitions,
completedmetadatafix or originalconversions. No incomingprocessing/activation/Phase06.

[Report](2026-10-14-compact-reviewed-context-report.md) records exact evidence and limits.

Final documentary checks:400passed1.31s; phasevalidateexit0/can-advanceexit1(expectedblocked). All47sealed file hashes/sizes, seven code digests and manifest hash match; gitdiffcheck passes. Seven curated paths only; documentary commit follows inGit.
