# Reviewed oversized record partitions implementation plan

> Execute inline using executing-plans/TDD; one fresh-context final review.

**Goal:** Prepare complete cited field groups for the two remaining oversized
gap-bearing records without dropping fields, resolving policy meaning or raising480cap.

**Spec:** Master10; undergraduate-scope/source-gap/service policies; previous body/
cover/source-limit reports and reviewed-field contracts. Owner says continue.

**Architecture:** A checked preparation helper partitions whole scalar fields in
source order, retains the original row/spans/gaps and binds every part to it.
Mandatory dependencies and a shared record manifest require complete context.
Gap projections keep each located visible fragment and all affected claims; the
consumer reconstructs original gaps and checks their hashes across the group.
For this new group kind only, display compact gap metadata without duplicating
the same visible values already present in fields; stored limits remain complete.

## Constraints and review focus

- Preserve every original field/blank/span/event/word, all original seven gap groups,
  complete source rows and historical packets. Applicability remains unknown.
- No word splitting, invented geometry, policy interpretation, deadline precedence,
  source approval, model/dependency/DB/API/Docker/Prolog/activation/push or new intake.
- Explicit field_groups flatten to original field order exactly once. No empty or
  all-blank parts; each part must have located source content and fit480estimatedtokens.
- A checked original-row binding revalidates exact fields, gap projections, source/
  review/spans/order/scope. Omitting it cannot emit an unverified record group.
- Every part carries its reading identity and shared manifest; required dependencies
  remain mandatory even when caller omits the dependency sidecar.
- Whole-group assembly rejects missing/duplicate/substituted fields, mismatched
  manifests/pages/events/gap metadata, partial citations, wrong original gap hashes
  and insufficient context budget. Pending/default/unknown/excluded branches fail closed.
- Existing service/arrow/body/cover/scalar behavior and wire representations unchanged.
- Existing approved Python3.13; ignored workspace audit-evidence, explicit commits.

## Task — Complete field partition and distributed gaps

Files: new document_ingest/reviewed_record_context.py and
contracts/reviewed_record_groups.py; edits reviewed_policy_chunks.py,
contracts/reviewed_policy_context.py and retrieval/context.py; synthetic
tests/test_reviewed_record_context.py.

Interfaces:
- prepare_reviewed_record_context(bundle, *, reading_id, field_groups, field_spans,
  sources, review_events) -> inactive original_reading/readings/field_spans/
  required_readings/record_bindings.
- Adapter optional record_bindings rechecks exact original-derived projections.
- service_group adds record_manifest only for these parts; manifest contains the
  ordered field parts and original gap field/locator/value-shape/hash declarations.
- validate_record_group(members) reconstructs complete original gaps before rendering.

- [ ] Focused synthetic RED: two/four ordered parts fit480, preserve original row,
  exact fields/spans and reconstructed gap; child-first context contains whole group.
- [ ] Unknown/pending/excluded/default/missing binding/dependency, field/gap/source/
  event/manifest mutation, blanks, JSON/stored shape and exact budget regressions.
- [ ] Smallest helper/codec/adapter/group validation implementation; GREEN and related
  reviewed/retrieval suites; cohesive verified code commit.
- [ ] Actual table row groups: Cause; all four penalty fields (including two blanks).
  Timing groups: one whole field per part. Do not repair malformed cause or pick a deadline.
- [ ] New actual derivative from current73readings ->77parts/readings, retaining all
  267fields/29blanks/235spans and seven logical original gap groups. Multiple projected
  gap-bearing parts are counted separately; actual output remains unknown/0chunks.
- [ ] Fresh original47/87 renders/source hashes, prior seals, default compatibility,
  independent exact field/gap/source/partition/current-adapter checks. No conversion.
- [ ] One final independent review; TDD correction pass if needed. Seal/report/decisions/
  progress/checkpoint/INDEX and ledger validation; formalPhase05 advancement blocked.

## Resume evidence and rulings

Cleanf58e483 reconciles prior body/cover code49e89c6 and documentary closure.
Thesis physical17–18/36, routingPNG, master10, activeplan/blockedhandoff/previous
completePhase04 and standing policies/datasetguide/ingestionREADME freshly consulted.
No scope/routing discrepancy. Newbatch comes later, with organization requested later.

Ruling: compact only redundant limit display for manifest-bound groups; retain full
stored/source originals and require whole-group gap reconstruction — prevents cap
inflation while preserving limitation meaning. Omitting reconstruction could hide
conflicting/partial evidence, so consumer validation is mandatory. No cap increase.
