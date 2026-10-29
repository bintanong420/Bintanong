# Hosted 560 activation results — activated; website smoke pending

Codex resumed Claude's [executor handoff](2026-10-30-hosted-560-codex-handoff.md) at `76d5a92`.
Checked 29 October 2026, 23:13 +08:00 (machine local date; preserve the inherited 30 Oct release names).
**Activation passed:** owner supplied both settings in p12/.env. Codex assembled the PostgreSQL URI privately,
using the supplied pooler host, port 5432, expected project username and percent-encoded password.
The initial read-only psql connection test rejected authentication. Owner corrected the password; the rebuilt
URI passed `SELECT 1`. Inactive staging PASSED in 106.11 s (exit 0); activation PASSED in 121.08 s (exit 0); website smoke pending.
.env is ignored and untracked, and is never staged.

## Fresh evidence

- `hosted.py activate`: exit 0, 121.08 s; active `p12-research-faqsplit-20261030`, anonymous visibility
  560 chunks / 39 curriculum links; retrieval status `ok`, target hit; no rollback required, preexisting rows preserved.
  Fresh read-only MCP confirms corrected78 `superseded` and new release `active`.
  Evidence: `hosted-activation-result.json`, `hosted-activate.log`, `hosted-activate.exit`, `hosted-activate-timing.json`.

- `hosted.py stage`: exit 0, 106.11 s. Exact readback: 560 chunks/vectors, 39 curriculum links, draft research
  release with selected scope `17e11149...`; corrected78 still active, 78 runtime-visible chunks, all existing rows preserved.
  Loaded 381 new chunks, four supplementary receipts and 560 vectors in 25-row batches; recorded/bound selected review
  and designated research release through existing functions. Evidence: `hosted-staging-result.json`,
  `hosted-stage.log`, `hosted-stage.exit`, `hosted-stage-timing.json`.

- Connection probe: `docker exec` to the existing database container, URI passed as an environment variable,
  `psql -X -A -t -q -v ON_ERROR_STOP=1 -c "select 1"`; initially failed password authentication, then passed after the owner corrected the password.
  Scheme, project username, pooler host, port and password percent-encoding checked without displaying secrets.
  Password is neither an API key nor a literal placeholder. Sanitized outcome: `hosted-connection-check.json`.

- Post-stage Supabase MCP (before activation): `p11-research-corrected-20261026` active, 78 chunk members / 39 curriculum links;
  `p12-research-faqsplit-20261030` draft with 560 chunk members / 39 curriculum links (fresh post-stage MCP).
- Saved local rehearsal read and checked: `passed: true`, exit 0; 560 chunks/vectors, 39 links,
  replay no-op, anon/authenticated visibility, probe hit, rollback 78 and existing rows preserved.
- Ignored `codex-preflight-result.json`: all 560 runtime chunk-ID/content-hash pairs equal
  `bound-chunks.json`; every runtime seal member verifies; protected receipt/event/snapshot hashes unchanged.
- Shared-venv Python loaded `ResearchApiConfig.model_validate_json` and `_package`: PASS,
  560 chunks/vectors, new release/auth reference and hosted `composition: gate`; `documents` removed.
  This validates local configuration, not hosted readiness or answer quality.

## Prepared configuration

All paths below use `A = C:/Coding-projects/bintanong_workspace/audit-evidence/`.

| Artifact | SHA-256 |
| --- | --- |
| `p12-hosted-560-activation-20261030/hosted-research-pin.json` | `8ba58463233bb51e67c1d42a4b218cd3c98d446edbebb08def20dd196d220a96` |
| `p12-hosted-560-activation-20261030/hosted-research-api-config.json` | `ca215550d0d130f27570cd9b6332696666283f9e3e266625b4a1aaa36dedd9fa` |
| Existing package `runtime-seal.json` | `954d376e3c47e55856f2e7c959f4dd9b98f5195a2fb25242807e6081e4cabb8e` |

The original local-documents pin/config and all bound review artifacts remain unchanged.
Hosted pin uses release `p12-research-faqsplit-20261030`, authorization `research-owner-20261029`.
It retains the evaluated topic selection and routing context through `composition: gate`.

## Executed staging command

After the connection probe passed, ran from p12 through a hidden background launcher:

```powershell
$activationEvidence = 'C:/Coding-projects/bintanong_workspace/audit-evidence/p12-hosted-560-activation-20261030'
$activationPython = 'C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe'
& $activationPython "$activationEvidence/hosted.py" stage *> "$activationEvidence/hosted-stage.log"
```

Launch long steps in the background, inspect logs/readbacks, then follow handoff steps 4–6.
Slow release RPCs use existing `hosted.py` psql transactions because the saved rehearsal exceeded hosted REST's
8-second limit (review 35.73 s, bind 34.33 s, activate up to 123.3 s). No role/global timeout changes.
Supabase documents [session-mode connections](https://supabase.com/docs/guides/database/connecting-to-postgres)
and [connection-local timeouts](https://supabase.com/docs/guides/database/postgres/timeouts).

## Outstanding gates

Hosted staging and activation readbacks passed. Website smoke and console check remain pending.
Keep corrected78 as rollback. No complete Phase 12 handoff or advancement yet.
SQL flowchart validation was delivered before this session; no new SQL changes/checks made here.
The inherited boundary remains: Python verifies geometry/span digests; do not claim SQL independently checks them.
Research build only; source gaps, undergraduate scope, privacy and institutional-release limits remain.
