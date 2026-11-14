# Original native grading-field mappings — 13 October 2026

Delivered at `ba8aae4` with review fix `b9e614d`, after plan `5e8eab1`: 45 exact native PDF field spans and
nine literal blank mappings across 18 undergraduate grading rows. The retained
handbook text and union character boxes match the saved original evidence. The
pending adapter still emits zero actual chunks; all 66 applicability declarations
remain unknown. Formal Phase 05 and institutional source/retrieval gates stay open.

## Mapping and evidence boundaries

[Plan](2026-10-13-reviewed-native-field-spans-plan.md) and
[decision record](../docs/decisions/phase-05-reviewed-native-field-spans.md) describe
the pure native mapper. It reconstructs the preparation from original source/event
bytes, matches pending source versions, and checks accepted/corrected scalar fields
with native ranges against an injected original reader. Excluded/unknown review
audiences are withheld before reading source ranges; declared undergraduate review
may proceed while institutional applicability remains unknown.

Each nonblank field retains end-exclusive native character indices, exact native
text, PDF point box and page dimensions. Explicit left/bottom/right/top coordinates
become SourceSpan left/top/right/bottom with BOTTOMLEFT origin. Text-item IDs use
`native-pdf:p46:chars<start>-<end>`, naming actual native PDF characters. No Docling
cell/text item or image-pixel geometry is invented. The mapper rejects text,
field/page/geometry/source mismatches and preserves unavailable evidence.

Nine blank percentages retain empty span lists and explicit original blank
evidence, with no glyph box, zero or other default. Raw column errors for rows3–9
remain in the unchanged sidecar; the mapping uses confirmed original fields.
The shared undergraduate/Law heading remains provenance and grants no Law support.
No source-register transition, canonical candidate overwrite, embedding, runtime,
database, rule execution or activation occurred.

## Actual outputs and preservation

Ignored packet:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-reviewed-native-field-spans-20261013/`.
Start with its README, then `native-field-mapping.json` and
`pending-chunk-result.json`. The one-time producer refuses to overwrite completed
output; earlier normalization/conversions/page reviews were reused intact.

| Measurement | Observed result |
| --- | --- |
| Supplied reading coverage | 66 readings/267 fields, exact earlier preparation retained |
| Native mapping | 45 nonblank fields + nine blanks, 18 undergraduate grading rows |
| Remaining fields for this native mapper | 213 fields lack supported native range evidence; image/raw/structured evidence retained |
| Pending scalar mappings | 225 before, 180 after; 18 grading rows now need applicability evidence only in the pending adapter |
| Actual chunks | Zero emitted; 66 withheld for unknown applicability |
| Other carried requirements | 13 structured/null field mappings; seven source-gap groups unchanged |
| Prior evidence | 595 earlier unique files unchanged, including PDFs, candidate bundles, registers, review events and prior seals |
| Independent saved check | 45 exact native text/geometry comparisons, nine blanks, seven retained raw association errors and all prior hashes pass |

These are selected mapping counts, not an exhaustive corpus audit. Missing native
mapping evidence is not missing institutional content. Source acquisition/authority,
effectivity, three unresolved interpretations and actual policy-retrieval calibration
retain their earlier states. The original reader/caller supplies trusted technical
evidence; consistency checks cannot establish university approval.

## Verification actually run

- System Python3.13.7 `python -B -m unittest discover -s tests -p
  test_reviewed_native_spans.py -v`: initial14absent-moduleRED/GREEN; audience
  exclusion guard reproduced RED then fixed; final15passed0.070s.
- Reviewer reproduced PdfiumError escaping the native reader failure handler;
  installed exception inheritance is RuntimeError. Focused regression RED then
  explicit field-level catch GREEN16passed0.066s. Final independent review:
  actual PDFium failure now yields native_reader_failure, no residual findings;
  16 focused tests pass0.065s.
- Existing approved Python3.13 environment `-B -m pytest` on native/preparation/
  pending-chunk mappers, policy chunks/candidate bundle, source/governance contracts
  and docs hygiene, `-q -p no:cacheprovider --basetemp <packet>/temp/pytest-relevant-final`:
  **1008 passed, one existing Windows symlink skip, 51 subtests, 29.38s**.
- Final review-fix rerun of the same relevant set:
  **1010 passed, one skip, 51 subtests, 21.11s**.
- Approved Python `-B <packet>/map_actual.py` and `<packet>/verify_readonly.py`:
  original native text/boxes, saved mappings/blank flags, exact original sidecar,
  pending withholding and595priorfile hashes match. Independent verifier imports
  neither the mapper nor its producer.
- Phase ledger:19passed10.805s. Final independent reviewer confirms saved/fresh
  mapper and pending-result equivalence, all45native fields/nineblanks/595hashes.
  Final documentation/diff/phase checks are recorded before closure.
- Final docs365passed0.87s; diff/elevenfileseal/595priorhashchecks pass. Phase
  validationexit0; can-advanceexit1expected for the blockedPhase05handoff.

No full repository suite or formal Phase05 exit-gate claim. Python environment,
dependencies/locks and models unchanged. pytest9.1.1 and pypdfium2 5.14.0 reused;
TEMP/TMP and basetemp external, no pytest cache. Models remain under
`C:/Coding-projects/MODELS`; no model execution/download/copy/digest refresh.

On resume, consulted thesisphysical17–18/36, runtime routing PNG and master10,
scope/source-gap policies, grading native evidence and current pending contracts.
No scope discrepancy. Context7 fetched official pypdfium2 character-box/range
documentation before original reads: native boxes are in PDF canvas units;
range counts address the native character array, not Python string length.
[Official native text API](https://pypdfium2.readthedocs.io/en/stable/_modules/pypdfium2/_helpers/textpage.html).
GitHub MCP read remote branch `f10d5cd`; no fetch/merge/push or external write.

## Digests and next action

| Artifact | SHA256 |
| --- | --- |
| Native mapper | `ce2162a2827c8d4009f3ffba36b1323c65c05acbd4aeee606133e957feacb837` |
| Synthetic tests | `a1b4d7d98ed9a34bcf97846a8c48ca5cfd34016ac82c269bd30b479d9bd56a51` |
| Actual mapping | `9621641ca6032f90b5d4fa40f38b767e37b7bb07961a0211c05939df35f063ef` |
| Pending result with mapped grading fields | `823eeb751960a6584ca1f581c54f84294244fa4c7438fea71ea106510dba5a01` |
| Eleven-file evidence seal | `37031433c67495c09d2d5ef2575c51cb779079777efce320c377f48d0fea98b9` |

Next bounded technical step: define original-layout field mappings for confirmed
overload/cross-enrollment rows and arrows, retaining image/native/raw provenance
and explicit scale evidence. Establish scalar/structured associations under focused
TDD; never fabricate native character ranges for image-only fields. Keep unknown
applicability withheld and source defects unresolved. Later structured logical-step
and gap/field-association context propagation remain required before approved
retrieval. Do not repeat grading/page reviews, original conversion or normalization.
