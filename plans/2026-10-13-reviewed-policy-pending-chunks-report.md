# Reviewed policy pending-chunk adapter — 13 October 2026

The separate pending adapter is delivered at `21833d8`, following plan commit
`83b17b2`. It converts explicitly applicable, confirmed scalar readings with exact
source spans into pending Chunk contracts. The actual sealed policy preparation
correctly emits zero chunks: all 66 supplied readings retain unknown applicability.
Formal Phase 05 remains active; this delivery grants no institutional approval.

## Implementation and limits

[Interface plan](2026-10-13-reviewed-policy-pending-chunks-plan.md) and
[implementation decision](../docs/decisions/phase-05-reviewed-policy-pending-chunks.md)
describe the new pure `build_reviewed_policy_chunks` adapter. It reconstructs the
preparation from original source/event bytes, verifies byte-derived pending source
registers, checks exact source/version/pages/text/geometry and preserves named
fields, joint roles and literal blanks in one structured display. Original span
text stays separate. Source verification and content review remain pending.

Unknown/mixed/excluded applicability, partial field review, missing/invalid spans,
source gaps, unmapped structured/null fields, duplicate spans and oversized rows
are withheld explicitly. Complete required context must survive from the same
source version; transitive dependencies and cycles remain atomic. Chunk identities
include the entire required context so a changed exception invalidates its parent.
The token cap measures both source and structured display using honest estimates.

Source-gap readings are withheld while context propagation of their limits is
absent. Current runtime context renders span text; structured row-display handling
requires a later explicit integration and tests before approved retrieval. No
runtime/API/Docker, database, embedding, Prolog or publication behavior changed.
The adapter's caller mappings remain trusted declarations; structural checks and
byte hashes cannot establish university authority or human approval of new text.

## Actual sealed-source check

Private packet:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-reviewed-policy-pending-chunks-20261013/`.
Start with README; `pending-chunk-result.json` includes exact earlier preparation
as a sidecar and accounts for every withheld reading. One-time scripts refuse to
overwrite completed output. The earlier consolidation/normalization was reused.

| Check | Observed result |
| --- | --- |
| Supplied review coverage | 66 reading groups, 267 fields, 29 literal blanks, 15 exact owner events, two pending source registers |
| Emission | Zero chunks; 66 withheld; every reading requires undergraduate applicability evidence |
| Additional mapping requirements | 225 scalar fields need explicit canonical spans in this call; 13 structured/null fields need a defined mapping |
| Source limits | Seven gap groups retained unchanged, including clipped process text, malformed condition, timing conflict and unknown effectivity |
| Preservation | 585 earlier unique file paths unchanged, including original PDFs, canonical candidate files, source records, review history and ten-file preparation seal |
| Independent saved-output check | All 66 exact withholding reason lists and the full 267-field sidecar match inputs; no adapter/script import |

No original field anchors were supplied for this readiness call. Counts of missing
mappings describe this supplied set/call, not unavailable original evidence or an
exhaustive corpus audit. Existing native/image/raw evidence can support subsequent
explicit mapping without repeating completed owner page comparisons. Source sheet
and three unresolved interpretations retain their earlier states.

## Fresh verification

- System Python3.13.7: `python -B -m unittest discover -s tests -p
  test_reviewed_policy_chunks.py -v`, 17 passed, 0.124s.
- Initial 15-case RED: adapter module absent; initial GREEN15. The additional
  changed-required-exception test failed because the initial parent hash included
  dependency names only. Full transitive base-digest closure fixes it; final17GREEN.
- Existing approved Python3.13 environment: `-B -m pytest` on new adapter/preparation,
  candidate bundle, policy text/chunks, procedure text, ingestion reports, source
  manifests/source/governance contracts, retrieval context/engine and docs hygiene;
  `-q -p no:cacheprovider --basetemp <packet>/temp/pytest-relevant`:
  **1323 passed, one existing Windows symlink skip, 28 subtests, 29.15s**.
- `python -B <packet>/check_actual.py` and `<packet>/verify_readonly.py`: saved
  coverage/reasons/gaps, exact sidecar and all 585 earlier hashes pass.
- Independent read-only reviewer: no actionable findings; 17 focused tests pass
  0.132s; fresh in-memory actual build equals saved result and all 585 preservation
  hashes match. No scope/routing discrepancy.
- `python -B -m unittest discover -s
  .agents/skills/bintanong-phase-handoff/tests -p test_phase_state.py`:
  19 passed, 10.001s. Final documentation/diff/phase checks are recorded in the
  active checkpoint. Full repository suite/formal Phase 05 exit gate NOT RUN.
- Final docs hygiene362passed0.93s with external basetemp/no cache; diff check,
  nine-file output seal and585earlierfile hashes pass. Phase validationexit0;
  can-advanceexit1expected for the existing blocked Phase05handoff.

Environment unchanged: installed pytest9.1.1 and pypdfium2 5.14.0 reused; external
TEMP/TMP/basetemp/no cache. No installs/downloads, lock/dependency changes, fresh
conversion, model execution or weight copying. Models remain in
`C:/Coding-projects/MODELS`; model digests were not refreshed by this work.
Thesis physical17–18/36, runtime routing PNG and master section10 reconsulted.
GitHub MCP read the remote branch head `f10d5cd`; no fetch/merge/push or remote write.

## Exact artifacts and next action

| Artifact | SHA256 |
| --- | --- |
| Pending adapter | `f35d2123603ffa7b48735446a26ad5b0612472eb71a674ba9d9743416a88ae0c` |
| Synthetic tests | `84ca4720628a6aa9010d3bd7d7a8b3759ee6f5974b2fc317201409d07a1ce20d` |
| Actual pending-chunk result | `3d0ee1eaf81ab5cb2ca3636ce1cb6111d73d960cecd68ea920a534ead2e30205` |
| Nine-file output seal | `f1b3f9bb3c048306ba4545392a795ef9c89619d4cc46e70db9094251a25093d2` |

Next: map the existing source-backed scalar review evidence to exact field spans,
starting with the 45 nonblank undergraduate grading fields/nine blank percentages.
Use explicit original coordinate orders and retain raw association corrections;
do not fabricate Docling cells or convert pixel image boxes without actual scale
evidence. Continue unknown-applicability withholding. Define structured logical-step
mapping and gap/row-association context propagation under their own focused TDD
before approved retrieval. Source authority/effectivity and real policy-retrieval
calibration remain formal gates. Preserve originals and all completed reviews.
