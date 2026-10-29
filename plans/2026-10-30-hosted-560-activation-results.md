# Hosted 560 activation results — preflight only

Codex resumed Claude's [executor handoff](2026-10-30-hosted-560-codex-handoff.md) at `76d5a92`.
Checked 29 October 2026, 23:13 +08:00 (machine local date; preserve the inherited 30 Oct release names).
**Activation pending:** `SUPABASE_HOSTED_DB_URL` is absent from p12/.env. Owner supplied pooler hostname
`aws-0-ap-southeast-1.pooler.supabase.com` and asked Codex to assemble the URI. Hosted database password is
unavailable in the existing settings (the existing database URL is local). Owner asked to add
`SUPABASE_HOSTED_DB_PASSWORD` privately to p12/.env; Codex can then construct the URI without displaying it.
No hosted writes, staging, activation or hosted website smoke performed in this session.

## Fresh evidence

- Read-only Supabase MCP: `p11-research-corrected-20261026` active, 78 chunk members / 39 curriculum links;
  `p12-research-faqsplit-20261030` not present.
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

## Resume command

After the owner supplies the expected project's Session pooler URI in p12/.env, run from p12:

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

Hosted staging/readback, activation/readback, website smoke and console check are pending.
Keep corrected78 as rollback. No complete Phase 12 handoff or advancement yet.
SQL flowchart validation was delivered before this session; no new SQL changes/checks made here.
The inherited boundary remains: Python verifies geometry/span digests; do not claim SQL independently checks them.
Research build only; source gaps, undergraduate scope, privacy and institutional-release limits remain.
