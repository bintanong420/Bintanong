# Actual wiring on dev 5342587c

The implemented candidate library path is connected. The ingestion CLI creates and checks a candidate bundle; generating inactive rule review JSON is a separate explicit library call. No automatic CLI, API, UI or runtime invocation of that bridge exists in the production caller search. This is the Task 3 library boundary described in docs/decisions/phase-02-unified-ingestion.md, not evidence of runtime activation.

| Boundary | Actual code on dev | Observed behavior |
| --- | --- | --- |
| CLI -> prospectus producer | backend/bintanong_tools/document_ingest/__main__.py:31 | prospectus_candidate dispatch calls run_prospectus_ingestion |
| Producer -> captured extraction/audit and governed chunks | backend/bintanong_tools/document_ingest/prospectus.py:224 | registered snapshot conversion, current parser/audit, source/version binding, external completion manifest |
| CLI -> checked bundle | backend/bintanong_tools/document_ingest/__main__.py:35; bundle.py:44 | reloads bundle and prints candidate accounting/counts |
| Explicit library handoff -> checked bundle | backend/bintanong_tools/document_ingest/prospectus_rules.py:181 | prepare_rule_candidates(bundle_path) reloads and checks prospectus bundle |
| Field evidence -> pure compiler | backend/bintanong_tools/document_ingest/prospectus_rules.py:223; prospectus_extractor/rule_candidates.py:152 | complete owned field spans, checked source/version and review evidence passed to build_rule_candidates; inactive artifact returned in memory |
| Real combined acceptance | tests/test_prospectus_rule_handoff.py:128 | synthetic snapshot/converter -> real parser/audit -> producer -> checked loader -> bridge -> compiler; not a production runtime caller |

Recorded independent evidence is 525 frozen candidate tests passed, exit 0, including the combined acceptance and actual conversion-status refusals; integrated dev smoke recorded 18 passed, exit 0. Logs and exit records were inspected again; passing suites were not rerun on this resume because the reviewed code is unchanged. Original-document accuracy and measured OCR are not established by synthetic conversion tests.

Read the saved earlier plaintext conversation completely (457 lines); the original conditional push instruction and the precise one-shot Standards approval are retained. Current AUTHORIZATION/CHECKPOINT/DEV_PUSH_RESULT record the later owner “just push it na” instruction and the actual dev push while the remaining whole-branch inspection was explicitly deferred. Fresh Git reflogs and actual ls-remote independently agree with that push record: dev and remote are 5342587c56dd3dcb3cc1201bd8f7a1561b8c2f88. This resume finishes the outstanding inspection; it does not repeat the integration or push.

Original-source validation, Handbook/Charter coverage, measured OCR, human/domain review and later runtime/API phases remain separate. No institutional approval follows from a consistent bundle or this candidate handoff.
