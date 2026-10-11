# Independent Standards recheck — publication fixes

**APPROVED — confirmed defects: NONE.**

Approval attaches to frozen code `54f31f9113dddfb942b35022d40e38267a4daaaf`, scoped to `407813c..54f31f9` (`ad931c4` ledger/authority and `54f31f9` semantic capture). The only observed dirty file is the progress document. Read the original Standards findings, implementer report, changed production owners/callers, regression additions and decision updates. No broad review reopening or repository edits.

All three P2 findings are resolved:

- Ledger completion and old-value applicability both reuse `placement.unclaimed_items`, matching persisted sheet/verifier obligations and covered-anomaly exclusions. Undecided, unresolved, wrong-PDF and stale anomaly decisions block completed review; accepted current decisions count. PDF-only decisions retain their prior applicability policy.
- Materialisation rebuilds authority with reclassified courses and current ledger evidence. Top-level `content_review`, authority detail and review detail agree; source/hash/identity gates are preserved conservatively. Every materialised candidate, including unchanged candidates, stays non-executable with `derived_sections_stale`; authority and extraction audit are explicitly listed stale. No source approval is manufactured.
- Pipeline parses captured semantic-map bytes once through the existing metadata parser; the same `InputSnapshot` supplies the identity digest. It passes the parsed map explicitly, including an empty map, so loading cannot trigger a later map reopen. Prepublication byte/absence checks reject changed, deleted or newly appeared maps. Transient edit/restore cannot alter metadata under the original digest because parsing already used the capture.

## Independent evidence

Executed `py -3.13 -m pytest tests/test_prospectus_ledger.py tests/test_prospectus_materialise.py tests/test_prospectus_input_snapshot.py -k 'persisted_anomalies or stale_authority or top_level_review_status or semantic' -q -p no:cacheprovider --basetemp <external scratch>/standards-recheck-temp`, with `PYTHONDONTWRITEBYTECODE=1`: **16 passed, 30 deselected**, exit 0. Log: `standards-recheck-tests.log` in the parent scratch folder.

Executed 11 additional Python assertions independently: mixed/covered anomaly obligations; wrong-PDF decisions; empty/new ledger evidence; hash mismatch; repeated materialisation without duplicate stale blockers; status coherence; stale status declarations; parser using supplied text without a file read; and explicit empty semantic-map behavior. **11 passed**, exit 0. All writes stayed in external scratch.

Root reports full suite 1013 passed/13 subtests/five warnings and self-test 80/80; not independently rerun here. Root's final comparer was still running at assignment; no new comparer success claimed. Prior markup-hash and prerequisite-annotation fixes remain present. Suspicions requiring further investigation: NONE. Human B2 trials and institutional/source approval remain pending.

**APPROVED — NONE.**