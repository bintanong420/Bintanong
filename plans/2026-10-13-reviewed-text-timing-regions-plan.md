# Reviewed handbook text and timing mappings implementation plan

> Execute inline using executing-plans and test-driven-development; retain the
> isolated worktree and use one final independent review.

**Goal:** Map four confirmed programme body readings and four timing statements,
keeping page furniture separate and the applicable completion deadline unresolved.

**Architecture:** Add a pure reviewed_body_partition validator for the exact recorded
body/segmentation correction. It checks complete ordered raw provenance, original
raw text/character spans, confirmed segmentation roles/text and matching review
events; only programme_name segments supply body pages. A separate original-image
mapper checks retained raw BOTTOMLEFT PDF boxes against hash-matched full-page
renders, preserving all furniture provenance and emitting only body spans. Reuse
existing region bindings for timing statements. The pending adapter derives body
page checks from this validated partition instead of requiring page25 furniture
in a page24 body span; structured segmentation remains unsupported/withheld.

**Spec:** Source-gap/undergraduate policies and the Charter delivery's next action.
Owner already confirmed these body/furniture separations and all four statements.

**Stack:** Python3.13.7, existing pypdfium2 5.14.0/pytest9.1.1.

## Constraints and review focus

- Preserve originals/raw/register/preparation/decisions/seals byte-for-byte. No
  repeated conversion/review, dependency/install/download/model/DB/runtime work.
- Character spans here index retained raw item text, not native PDF glyph arrays.
  Do not label them native character ranges or fabricate Docling cells.
- Require exact source/version/raw provenance and confirmed linked body/segmentation
  reviews. Reject missing/reordered/overlapping/changed segments, bad text/ranges/
  roles/pages/coordinates, partial review and excluded review audiences.
- Only canonical whitespace normalization is allowed for raw segment slices;
  no inferred correction, omitted content, offering/applicability or policy meaning.
- Furniture remains separate evidence; do not discard raw fragments or map them
  into programme text. Page24 body/page25 furniture is explicitly retained.
- Timing original wording and unresolved one-term/one-year interpretation stay
  unchanged. No selected deadline or executable rule; all seven gap groups persist.
- All66 applicability declarations unknown, zero chunks/activation. Structured
  segmentation, fee/null/graph contexts and source gaps remain separate gates.
- Tracked tests synthetic only; original-derived maps/annotations/logs/temp/seals
  ignored under workspace audit-evidence; models stay C:/Coding-projects/MODELS.

## Task 1: Reviewed raw partition and body page mapping

Add reviewed_text_segments.py and tests/test_reviewed_text_segments.py;
modify reviewed_policy_chunks.py and its tests as needed for verified body pages.

- [x] RED for exact body/furniture partition, raw character/provenance agreement,
  page24-only body without page25 furniture, partial review, source/render/geometry
  mismatch, source gap/input invariance and independent adapter page validation.
- [x] Smallest GREEN; image/native/service/preparation/pending/source/governance
  regressions and phase ledger checks. Record commands/results and cohesive commit.

## Task 2: Additive actual body and timing evidence

- [ ] New ignored p05-reviewed-text-timing-regions-20261013 packet. Verify prior
  Charter seal/652priorfiles+15files+seal, actual text/timing events and original
  images19/21/23/24/25/47. Preserve body/furniture and ETEEAP/campus context.
- [ ] Eight scalar mappings; expected combined195spans/29blanks, scalar requirements
 38to30, zero chunks/66unknown applicability/seven gaps. Parent fee remains separate.
- [ ] Independent original/raw/event/region/partition/gap/preservation verifier,
  one final review and new evidence seal. Original wordings are not reinterpreted.
- [ ] Curated report/decision/index/checkpoint/progress, final docs/diff/phase checks,
  local commit and exact next action (pre-enrollment source-gap field mapping).

## Pre-flight ruling

The recorded body locator includes every raw item's page, including furniture.
Ruling: derive effective scalar body pages only from the exact confirmed complete
partition, preserving the original locator and discarded-from-body segments as
evidence. The pending adapter independently uses the same bounded validation;
no arbitrary page override or skipped furniture review is permitted. Cost: only
this explicit reviewed partition contract is supported; other mixed fragments
remain unresolved until separately reviewed/mapped. Body snippets are historical
source statements, not approval of current programme offerings.

Incoming collection remains incomplete; exact placement instructions at intake
after complete-batch notice and before final calibration including new sources.

Implementation verification:10 focused tests GREEN0.047s after observed interface/
malformed-type/furniture-geometry REDs; relevant1375passed/1skip/173subtests25.60s.
Actual eight source fields mapped,195combinedspans/29blanks and scalar38to30;
668earlierfiles unchanged. Structured segmentation and timing/source gaps remain
withheld; no original locator or review/history changed. Final review/closure next.
