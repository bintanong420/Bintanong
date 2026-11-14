# Supabase MCP parse-response investigation — 25 October2026

Owner reported "mcp failed to parse server response" and named Supabase. Investigation was read-only;
no credentials/configuration, database grants or source-release state changed.

## Findings

- Supabase app connector `execute_sql` succeeded (`select 1`, checked18:24UTC), security advisors
  succeeded (only the owner-accepted leaked-password WARN), and bounded project-log query succeeded.
  Fifteen-minute window18:15–18:30UTC returned78 pgbouncer events; this count is not a full health audit.
- Both default and Orca-account log databases contain the exact error in OAuth token refresh, before
  direct Supabase tools become ready. Default-home latest matching WARN:23 Oct05:35UTC, "OAuth token
  refresh failed: Failed to parse server response". Account log matching provider WARN20 Oct03:33UTC
  is followed by "OAuth authorization required". These are HISTORICAL entries, not a timestamp match
  to the owner's newest warning. Do not claim a proven current root cause or a completed auth repair.
- Active shell uses an Orca account-specific CODEX_HOME; diagnostics/auth must use that environment.
  CLI0.164.0 `mcp get supabase --json` shows enabled Streamable HTTP at the official MCP endpoint,
  project-scoped to this project. `mcp list --json` reports o_auth; that is stored auth status, not proof
  of a successful direct startup. No secret fields were printed. Root config is not the active account's
  credential store. Direct configured MCP and the connected app are separate paths.
- Unauthenticated urllib endpoint probe returned403/plain text "error code: 1010", not the skill's
  expected401. Its Python client/network path differs from the successful app calls; it cannot establish
  that Supabase itself is down or that OAuth refresh credentials are invalid.

## Interpretation and recovery

The exact logged phrase concerns direct OAuth startup/refresh, not a PostgreSQL query/parser failure.
The newest incident is consistent with that failure class, but current response bytes/status and its
matching timestamp are unavailable. The app connector is usable now; no database repair is indicated
by the evidence. Avoid deleting tokens, changing grants or disabling the server to hide the warning.

After the requested /clear, check direct tool discovery separately from app tools. If the warning
recurs, capture its timestamp and account-local startup error; run `codex mcp login supabase` from the
same Orca account terminal and complete the browser OAuth flow, then restart that session and verify
an authenticated read. Browser consent requires the owner. Login alone is not success evidence.
No need to reauthenticate the working app merely because the direct connection failed.

## Documentation consulted

Context7 resolved `/supabase/mcp` and fetched HTTP transport/authentication troubleshooting references.
Current [Supabase MCP guide](https://supabase.com/docs/guides/ai-tools/mcp) documents OAuth login,
possible client restart and verifying tools with a real query. The required
[observability guide](https://supabase.com/docs/guides/observability) was read before diagnosis.
[Official OpenAI MCP documentation](https://learn.chatgpt.com/docs/extend/mcp) documents separate
`codex mcp login <server-name>` and plugin-bundled servers. None proves this specific transient cause.
