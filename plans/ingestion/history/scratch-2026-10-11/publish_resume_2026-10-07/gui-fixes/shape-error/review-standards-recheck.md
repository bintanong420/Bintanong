# Scoped independent standards recheck

Committed range: `41fe3c3241c7fdbbab66e50d805454488fbac656..2d22e2fa6c15186aaf794b735c20bb00a6abb02c`.
Worktree: `C:\Users\Hawksprey\source\repos\Bintanong-wt\gui-fixes`.

Scope: the original P2 in `gui-fixes/review-standards.md` (present-but-invalid response values escaping client recovery), its direct malformed-success/error regressions, and compatibility controls. This was not a new audit of unrelated behavior.

## Original finding: resolved

The shared `api()` boundary now validates consumer-required shapes before returning a usable response. Both original payloads were rerun through the existing actual-client Node VM harness:

- HTTP 200 answer `{written: 1, state: {}, next: null}`: no exception; no Saved announcement; answer-error reports `Save status unknown. The server may have completed this request. Check the connection and inspect the ledger or corrected file before submitting again.` Current question, Other choice, typed correction and reason remain intact.
- HTTP 200 queue `{queue: {}, all: []}`: no exception; status reports `The requested data could not be loaded. Check the connection and reload when the server is available.`

The original report's reproducer was used with only its observation expression adapted to tolerate the now-absent status node (`nodes.status ? nodes.status.textContent : ''`). The malformed payloads and submit/loadQueue calls were unchanged. This does not alter production behavior or bypass a failing consumer.

Typed native predicates cover state, question, queue, twin, write-result and error envelopes before consumer state replacement. Direct regressions exercise malformed nested display values and preserve entered answers, current view and previous display state; malformed POST replies remain unknown with one request and no retry. Valid supported primitives, optional flag fields, successful consumers, unavailable-twin/PDF fallbacks and genuine 4xx validation errors remain compatible. Error responses with unusable errors/error types are rejected before `.join()` or text rendering. This change adds no dependency, ledger/source approval behavior or generic schema framework.

## Independently rerun evidence

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
py -3.13 -m pytest -q -p no:cacheprovider --basetemp 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\gui-fixes\shape-error\standards-recheck-temp' tests/test_review_gui_client.py tests/test_review_gui_api.py
```

Result: **166 passed in 12.04 seconds**, exit 0. The original two malformed payloads were additionally executed directly using the existing client harness, with the observed outcomes above.

HEAD verified as `2d22e2fa6c15186aaf794b735c20bb00a6abb02c`; worktree status clean before and after checks. No tracked edits, staging, commits, pushes, installations, broad gates, new agents or owner-checkout writes. Root's full suite/self-test and the implementer's actual-server probe are separate evidence, not reruns claimed here. Browser/Lighthouse, human trial and Linux/macOS checks remain outside this recheck; Tasks 12/13 and institutional approval are not completed by this report.

APPROVED/NONE — original P2 resolved; no remaining confirmed finding in the scoped fix or its direct regressions.
