# Confirmed vehicle and enrollment field bindings — 15 October 2026

Resumed at `857b8db`; recovered owner decisions committed as `196982d`.
The unchanged `50405f5` mappers bind **22 additional confirmed V/E fields**:
14 original-raster fields and eight native-PDF fields, with zero mapper refusals.
Reuse the 66 fee fields and three native E01 headings unchanged: 91 selected
scalar-field bindings in total. This count is not complete source/service coverage.

## Selected coverage

| Groups | New fields | Evidence and limits |
| --- | ---: | --- |
| V01 | 2 raster | P50 application/sticker payment in G2 requirements5 and procedure2, separate regions; never a replacement-price reading. |
| V02 | 1 raster | G2 requirements4 student-permit rejection in lieu of a driver's license. |
| V03/V04 | 2 raster | G4 sectionVII non-transferability/one-year validity and renewal timing/same application requirements, separate complete selected readings. |
| V05 | 1 raster | G3 III.l replacement at owner's expense; price remains unavailable, no invented blank/zero-price span. |
| V06 | 1 raster + 1 native | G2 III.f 15km/hr and handbook physical93 row23 20kph, linked with owner research selection, discrepancy and no institutional supersession. No sanctions mapped. |
| E01 incoming | 2 raster | Incoming first-year audience and first-semester2026–2027 term. Three prior continuing-PDF campus/term/audience spans reused unchanged. |
| E02 | 4 raster | Enrollment dates, CS clinic dates, before-other-step instruction and certificate OR appointment slip. Cross-source dependencies and timing ambiguity retained. Other clinic rows/procedure fields not newly approved. |
| E03 | 1 raster + 1 native | Incoming Original PSA wording and handbook physical31 undergraduate-freshman photocopy wording, linked without a precedence choice. |
| E04 | 6 native | Continuing PDF's printed step-number-column labels1,3,4,5,6,7 with actual glyph coordinates and character ranges. No Step2 span/action or complete-seven-step claim. |

The derivatives retain exact source/version/page, review-event hashes, accepted
full review groups and source limits. Raster boxes use original native pixel
canvases, page1/scale1 with exact original bytes; PDF fields use actual native
character ranges and glyph boxes. Related readings remain explicit dependencies;
these are selected scalar readings, not flattened or admitted complete procedures.
The existing PDF-only service binder was not expanded or invoked. Applicability
stays unknown, all fields inactive, no chunks/embeddings or benchmark tests created.

G03 alone is confirmed as recorded in the G packet. G01/original G02 remain
unconfirmed. Distinct ASG physical23 clause stays outside undergraduate evidence;
eight possible college-source sets are not supplied. F04 amount is still held;
prior fee evidence and its six absent values are unchanged. School verification
remains pending without blocking ordinary authorized provisional work.

## Fresh verification

Ignored evidence root:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-ve-field-bindings-20261015/`.
Existing Python3.13 environment:
`audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
No installs, downloads, model/vector changes, lock/dependency changes or source edits.

- Existing-environment `-B bind_confirmed.py`: 14 raster + eight native fields,
  zero refusals, unknown applicability/inactive flags preserved. Viewed all six
  full original photos, all 11 region sheets covering 14 fields and the existing
  handbook31/93 and continuing-PDF full-page renders. Author geometry QA does
  not extend owner review to surrounding unlisted fields.
- Existing-environment `-B verify_saved.py`: independent saved-artifact/event/value
  checks and exact mapper replay pass for all 22 fields. The two unavailable
  fields (replacement price and Step2label) receive no spans.
  All 62 original source hashes and 47 files in the earlier 22/25 seals match; the
  66 fee bindings and three prior E01 SourceSpan records remain byte-identical.
- Existing-environment `-B -m pytest -q -p no:cacheprovider --basetemp <newroot>/pytest-tmp
  tests/test_reviewed_image_spans.py tests/test_reviewed_native_spans.py
  tests/test_reviewed_policy_preparation.py tests/test_reviewed_policy_chunks.py --tb=short`:
  **112 passed / 157 subtests, 1.37s, exit 0**. Raw log retained.

Initial native-label selection also matched two inline “Proceed to Step” references;
original glyph positions identified the six real number-column labels. A verifier
used an unavailable JPEG frame-count attribute; corrected to the existing reader's
single-frame fallback. Failures/rulings retained in new evidence; no repeated source
partition attempts or new content judgment. No product change or new TDD cycle;
full 5277 suite remains historical 50405f5 evidence, not a fresh run.

Thesis physical 17–18, routingPNG, master 10, active plan/checkpoint, prior complete/
blocked handoffs and dataset/scope/source-gap/service policies consulted; no scope
or architectural discrepancy. GitHub MCP read existing remote commit a6c2c175;
no push/merge or database work performed. Owner artifact changes remain unstaged.

## Next action and benchmark review

All six proposed scenarios and their 18 exact English/Filipino/Taglish wordings and
expected behaviors were presented in this turn, with a focused async acceptance
question. No actual answer has arrived; preserve the original draft wordings and
accepted 12 scenarios / 36 variants. No new queries were encoded or scored.

Await actual wording/behavior acceptance; if accepted, create the versioned offline
development packet only for evidence-ready scenarios. U1 still needs the complete
necessary II/III source context/referral-office review: six confirmed V groups do
not approve the entire application procedure or all its terms. Do not silently
relax the proposal's prerequisite or infer an office-confirmation event. U2's
complete F01/F08/F09 selected example bindings are available, F04 does not block it.
Retain scope/unknown-curriculum safeguards, source limitations and inactive status.
Formal Phase 05 exit remains blocked; no Phase 06, runtime, Prolog or activation.

## Closure evidence

Documentation/phase-ledger checks:466 passed / 11 subtests in 15.13s, exit 0
(`tests/test_docs_hygiene.py` and the handoff skill's `test_phase_state.py`).
Phase-state validate succeeds; can-advance is refused as expected by the blocked
Phase 05 handoff. Whitespace checks pass. No full product-suite rerun needed.

New V/E evidence seal: 27 root files,
SHA256:`d7aa34c13abe115e8fc27f4ba6f8edbc2240ca65f5d93a85f5c0b9ad03549ddc`.
New G03/ASG decision/native-evidence seal: 5 files,
SHA256:`3871c0728d1570fd2bf49bdc4d42bb1e5fa251b8af36b7d203e46de2e13d9a88`.
Image-binding SHA256:`00902ccbbce50ee64dda45ac9ff84aae5a3f8a6eedc07d5dc38a21787a6394e8`.
Native-binding SHA256:`dbc3354aee8c5279b1f63531332476f2746231daf9a0c845a47ab655ece77e1b`.
Both new seals verify read-only. Never rerun their writing scripts in place;
future evidence goes into a separate ignored directory. Test temporary trees
are excluded. Only six explicit curated report/continuity paths enter the next
Conventional Commit; owner artifacts and raw source/evidence stay unstaged.
Checkpoint records parent 196982d; the following documentation commit is
recoverable in Git, not missing implementation. No push or history rewrite.
