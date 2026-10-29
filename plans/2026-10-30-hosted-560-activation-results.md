# Hosted 560 activation results

Completed 29 October 2026 (machine local date; inherited 30 October release names retained).
Followed [Claude's executor handoff](2026-10-30-hosted-560-codex-handoff.md). Research build only.
**PASS:** staged and activated `p12-research-faqsplit-20261030`; hosted HTTP and browser smoke passed.
Corrected78 is superseded and retained as rollback. No institutional approval or public deployment implied.

## Evidence and commands

`A = C:/Coding-projects/bintanong_workspace/audit-evidence/p12-hosted-560-activation-20261030`.
`PY = C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
Commands ran from p12, in hidden background launchers with output redirected to ignored logs.

| Command/check | Result | Evidence under A |
| --- | --- | --- |
| Hosted psql `select 1` | PASS after owner corrected password; URI assembled privately with percent-encoding | `hosted-connection-check.json` |
| `PY A/hosted.py stage` | exit 0, 106.11 s; 560 chunks/vectors, 39 links, bound selected review, draft research release; existing rows preserved; corrected78 still active/78 visible | `hosted-staging-result.json`, `hosted-stage.log`, `.exit`, `hosted-stage-timing.json` |
| `PY A/hosted.py activate` | exit 0, 121.08 s; new release active, anon sees 560 chunks/39 links; retrieval target hit; rows preserved; no rollback required | `hosted-activation-result.json`, `hosted-activate.log`, `.exit`, `hosted-activate-timing.json` |
| Read-only Supabase MCP | new release active, 560 members/39 links; corrected78 superseded | independently checked after activation and smoke |
| `PY A/start_hosted_research_api.py` | backend :8021 constructed in 110.88 s; live/ready HTTP 200 | `backend.log`, `backend-error.log`, `backend-readiness.json` |
| `PY A/http_smoke_hosted.py A/http-smoke.json` | exit 0, 3/3 answered with citations; no stream errors | `http-smoke.json`, `http-smoke.log`, `.exit` |
| Browser :3216/chat, guest | smoking penalty rendered with Handbook p.93 citation; source panel works; 0 console errors/warnings | `browser-smoke-result.json`, `browser-artifacts/hosted-smoking-sources.png`, `hosted-smoke-console-errors.txt` |

Stage appended 381 new chunks, recorded four cumulative supplementary receipts and loaded 560 vectors in
25-row batches. Existing chunks/spans/vectors and source-register states were preserved; no hand-written rows,
new migrations, function/grant/RLS changes, global timeouts, dependencies or models.
All writes used the existing `hosted.py` path. The saved local rehearsal, receipts, events and snapshot were not regenerated.

## HTTP smoke scope and timings

| Case | Answer | Source cards | Outer API request |
| --- | --- | ---: | ---: |
| Honors residence | cited residence clause | 1 | 51.0 s |
| CC 5 after failed CC 4 (BSCS 2018–2019) | documented unmet condition; CC 3 remains unknown | 4 | 26.7 s |
| CC 5 after passed CC 3/failed CC 4, and dropping procedure | unmet condition plus printed dropping procedure/source limitation | 5 | 49.5 s |

The Hybrid probe supplies both prerequisite facts, unlike the earlier local smoke which asked for missing
CC 3 completion. This is smoke evidence, not a benchmark rerun. Browser smoke separately checked the smoking
penalty and citation panel. API timings include hosted/network and request processing, exclude backend/encoder
startup and browser work, and are single observations. Startup is reported separately; no student-visible SLA claim.

## Bound configuration and preservation

The runtime chunk-ID/content-hash map equals the bound review for all 560 records; every sealed package file
verifies. Backend `ResearchApiConfig` and `_package` accepted the new hosted config. The pin removes `documents`,
sets release `p12-research-faqsplit-20261030`, authorization `research-owner-20261029`, and `composition: gate`
(topic selection/routing context). Original local-documents pin/config unchanged; the old config requires
corrected78 active and cannot be used after this switch. Current backend uses `A/hosted-research-api-config.json`.

| Artifact | SHA-256 |
| --- | --- |
| `hosted-research-pin.json` | `8ba58463233bb51e67c1d42a4b218cd3c98d446edbebb08def20dd196d220a96` |
| `hosted-research-api-config.json` | `ca215550d0d130f27570cd9b6332696666283f9e3e266625b4a1aaa36dedd9fa` |
| Existing runtime seal | `954d376e3c47e55856f2e7c959f4dd9b98f5195a2fb25242807e6081e4cabb8e` |

Selected scope: `17e11149b93c5f0e29fb43f29ea23d2aa87b6b4a602280fb8c53c402ce61d2a1`.
`codex-preflight-result.json` records protected artifact hashes, rechecked unchanged after smoke.
The 257 re-authored records use the owner's activation directive, with no per-chunk human approval; source
states were not promoted. Private inputs remain separate. .env is ignored/untracked and never staged.

## Connection path, SQL scope and recovery

Slow release RPCs used existing psql transactions through the Session pooler because the rehearsal exceeded
REST's 8-second statement limit (review 35.73 s, bind 34.33 s, activate up to 123.3 s). Existing functions execute
as service_role with a transaction-local 1800 s timeout. No role/global timeout changes.
Supabase documents [session connections](https://supabase.com/docs/guides/database/connecting-to-postgres)
and [local timeouts](https://supabase.com/docs/guides/database/postgres/timeouts).

The already-applied flowchart migration `20261029145841` checks selected-review SQL structure; geometry/span
digests remain Python-checked. No new SQL implementation claim. Manual rollback remains `PY A/hosted.py rollback`,
then restore the corrected78 backend config. No rollback was needed. Original source gaps, undergraduate scope,
unknown-versus-unmet safeguards and institutional-release limits remain.

Commits: `acbb0b9` preflight, `0b4aef9` staging, `62ecb96` activation. Answer-quality benchmarking on hosted
composition remains the owner's/Claude's follow-up; existing evaluation scores still describe the original local runs.
