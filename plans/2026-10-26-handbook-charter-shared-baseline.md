# Verified shared source/package baseline — Phase 11

26 October 2026. The bounded Handbook/Charter catalogue verification is delivered
through reviews [01](2026-10-26-handbook-charter-expansion-review-01.md),
[02](2026-10-26-handbook-charter-expansion-review-02.md),
[03](2026-10-26-handbook-charter-expansion-review-03.md),
[04](2026-10-26-handbook-charter-expansion-review-04.md),
[05](2026-10-26-handbook-charter-expansion-review-05.md),
[06](2026-10-26-handbook-charter-expansion-review-06.md),
[07](2026-10-26-handbook-charter-expansion-review-07.md),
[08](2026-10-26-handbook-charter-expansion-review-08.md), and
[09](2026-10-26-handbook-charter-expansion-review-09.md).
All **89 catalogue groups** have a review-record mapping. Literal clear-field
readings, supporting/historical selections, exclusions and holds are distinguished.

This is the shared preparation baseline requested by the owner. It is **not**
whole-document approval, exhaustive topic discovery, currentness verification,
institutional permission or activation of expansion content. Deferred source
interpretations and ambiguous field associations remain held, not silently passed.

## Fixed identities and review boundary

Use the full Git SHA of the commit delivering this record and reviews07–09 as the
fork point; the dedicated ingestion task's start receipt will record that SHA
after commit. Never fork implicitly from the later moving primary HEAD.

- Handbook original: `4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8`.
- Charter original: `42a93994e1467df0f32c7038d1c21f638c23ac0f1dee984463acf56caf526529`.
- Existing corrected78 comparison manifest:
  `bfd2a4993ece9212e297a0ee47592fe8debcf6f9435a908ba2ec8103811cc011`.
- Runtime seal: `22ceaa15c300a5fc2d8778062a9f19ebb175bee34700f68267ec651a07b34c0a`.
- Primary pin: `5dd2d9c95c3cc96181bdd11d3a24481f1c18a4a5c71284a55316c7d60acecc74`.
- Last-known research release: `p11-research-corrected-20261026`,78chunks/39curricula;
  root `release-offline-research-set-95fe326cf31a4439`. No fresh hosted reads/writes.

Byte-verified copies of both PDFs/seven sealed package files/seal/pin are in
workspace `audit-evidence/p11-two-developer-baseline-20261026/comparison-baseline-78/`.
These 11 files were verified against the originals again after review and never
rewritten. Its earlier manifest truthfully says expansion review was incomplete
when copied; preserve that historical receipt. This record and its commit supply
the subsequent review boundary. The copied pin remains **evidence only**, not
ingestion configuration. It points to the primary's package; do not run it there.

Source review uses 102distinct Handbook and62Charter catalogue page locators.
**152 original pages inspected this session**; reuse12previously reviewed pages:
H46/H62/H87–95 and C102. The rest of C102–103's complete previously reviewed
service is reused without new interpretations. Native-text/hash accounting for
all511pages from earlier audit is retained; it is not511visual field reviews.
Review accounting (`catalogue-review-accounting.json`) records all89ID mappings,
fresh/reused locators and unchanged baseline copies in ignored workspace evidence.

## Holds travel with the baseline

- Owner-confirmed H26 enrollment/payment/exemption discrepancy and H30 unresolved
  academic-deficiency undergraduate applicability; unchanged datasets/wording.
- Missing H27/H29 program lists; H47 timing conflicts; H60 incomplete diamond;
  H64 cutoff; established discipline numbering/overlap; C102–103 discrepancy; F04.
- H53 shorter-than-four-year honors paragraph applicability; source-specific
  curriculum/year/credit/fee clauses; no inferred equivalence/eligibility or new rules.
- Ambiguous first-row Registrar time/person associations C9 and C16–17 remain held.
  Literal fields elsewhere do not approve the entire step or service automatically.
- Original fee/checklist/form/total/role differences in records, DAC, library,
  finance and health services stay as printed, with unresolved interpretation.
- Mixed cash/check claims, international internship, CARMA/CCRD certification meaning,
  broad academic-related requests and library requisition selection remain held.
  Supporting/historical services/directories/forms do not become runtime subjects.

No new chunk IDs, vectors, topic/claim metadata, database receipts, Prolog rules,
release membership or runtime package was authored from the review notes. Existing
active knowledge stays at the sealed78; additions require separate candidate
authoring, exact review binding, compatibility verification and authorized activation.

## Fresh verification

Shared Python3.13, `-X utf8 -B -m pytest -q -p no:cacheprovider`, external basetemps:

| Check | Result |
| --- | --- |
| `test_ingestion_report`, `test_reviewed_policy_preparation`, `test_reviewed_policy_chunks`, `test_storage_selected_release_review` |77passed/110subtests,15.27s,exit0 |
| `test_runtime_package_storage`, `test_runtime_research_catalog`, `test_runtime_hosted_storage`, `test_runtime_composition` |65passed,2.18s,exit0 |
| Source/package/pin byte checks |11copies unchanged,7runtime seals valid,both original hashes match |
| Catalogue/review mapping |89/89IDs,102H/62Cpages,152fresh/12reused |

Logs/exits/receipts are in the workspace baseline evidence directory. Tests use
synthetic/local fakes, no hosted writes. Full suite was not repeated for this
documentation/source-review-only change: historical6896+1595subtests belongs to
unchanged production commit706d3c6; two natural grading failures remain unfixed.
No new model calls, embeddings, dependency/model downloads or browser accuracy claim.

## Next workstream boundary

Create the other developer's branch from this fixed delivery commit in a separate
worktree with a separate generated-output directory. Avoid the shared Orca setup
that copies ignored.env/installs dependencies; do not copy credentials/pin. Require
an explicitly identified disposable local database before mutation. No hosted writes.
Primary continues frontend/runtime and owns shared interfaces per
[workflow](2026-10-26-phase11-two-developer-workflow.md); merging tooling publishes no data.
