# Supabase MCP connection check —26 October2026

Owner requested this check before continuing hosted-chunk review. Read-only diagnostics only.
Current result: RECHECK PASSED, authenticated reads verified at26Oct2026 00:15:50 Manila.
Earlier unavailable-tool findings below are preserved as history, superseded by recheck.

- Available tool catalogue currently contains zero Supabase tools (direct MCP and app connector
  both absent); therefore no authenticated project identity/SELECT1/releases read could be run.
- Unauthenticated curl GET https://mcp.supabase.com/mcp returned HTTP401: endpoint reachable,
  authentication required. This is not evidence of authenticated connectivity or database health.
- Same active Orca-account CODEX_HOME: codex mcp get supabase --json confirms enabled
  streamable_http at official endpoint, project_ref=jyrudbiuajahsucsorco. Header/token environment
  references absent. No secrets printed or read from credential storage.
- codex mcp list --json reports enabled/auth_status=o_auth; stored auth classification is not a
  successful connection test. No startup_error field result establishes a successful handshake.
- Read-only account-local logs2 SQLite inspection found latest matching WARN at
  2026-10-19T16:55:45Z: "MCP server startup failed" / "failed to refresh OAuth tokens for server
  supabase: OAuth authorization required". Historical, not proof of current root cause/new incident.
- Current conclusion: MCP unavailable in this session; network endpoint reachable/config points
  correctly. Authenticated access/database health NOT verified. No current parse-error response
  captured, login repair claimed, database/config/credential/grant changes or model runs.

Recovery: same-account terminal `codex mcp login supabase`, complete owner browser authorization,
then restart/reload session and verify Supabase tools plus authenticated SELECT1/release membership.
Do not reset credentials, change grants or use cached snapshot as a new hosted read to hide the issue.
Owner authentication/reload is needed before verification can finish; don't resume chunk review first.
Review cursor remains48–49 NOT displayed;41approved/6corrections/0held/33pending.

Docs checked: Context7 /supabase/mcp transport/auth references;
https://supabase.com/docs/guides/ai-tools/mcp (authenticate/restart/query verification),
https://supabase.com/docs/guides/observability (read-only diagnostic methods),
https://learn.chatgpt.com/docs/extend/mcp (OAuth login command; local CLI help also checked).

## Authenticated recheck —26 October2026 00:15:50 Manila

Supabase direct MCP tools reappeared. All3 calls succeeded without errors:
- get_project_url: https://jyrudbiuajahsucsorco.supabase.co (correct project).
- execute_sql: SELECT1 returned connection_ok=1; server checked_at2026-10-25T16:15:50.618082Z.
- Release query: p09-research-selected-20261022 active19; p11-research-expanded-20261025 draft80.

This verifies current MCP authentication, SQL access and release status/count reads. It is not a full
health/security/function/write-path audit, membership-ID/hash comparison, or proof of root cause.
No credentials/config/database content changed by agent. User's intervening recovery steps unknown;
no specific login/restart fix credited without evidence. Raw3-call results ignored at audit-evidence/
p11-hosted-80-review-20261025/connection-recheck-20261026.json. Connection check gate satisfied;
review can resume48–49,not yet displayed. Counts41approved/6corrections/0held/33pending unchanged.
