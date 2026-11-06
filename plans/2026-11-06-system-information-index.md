# Chat system-information index

Owner approved 6 November: "As long it can be called within the chat."

## Design

Students can ask about Bintanong's capabilities, research scope and limitations in chat.
Use a host-owned index, selected by the existing semantic router through the
`system_information` control. Render reviewed project descriptions in English/Taglish;
do not embed them in the institutional-policy corpus or invent university citations.
The alternative of institutional document ingestion would confuse project and policy authority.
The index describes implemented paths with coverage limitations, not accuracy guarantees.
No new dependencies, source edits, institutional activation or deferred audit work.

## Implementation plan

Goal: expose accurate self-information through the existing chat answer path.
Architecture: extend terminal routing controls, integration and candidate/public answer
statuses; render a fixed bilingual index without a generation call. Existing academic
answers retain their evidence and complete-ledger requirements.
Tech stack: existing Python/Pydantic, Next.js/Zod and test runners.

- [x] Add a failing synthetic regression for router -> orchestration -> generation,
  English/Filipino/Taglish styles, no retrieval/Prolog calls and no invented citations.
- [x] Add the bounded capability/scope/limitation index and closed control/status wiring
  in routing contracts/prompt/compile/wire, orchestration contracts/reasons, generation
  contracts/generator/render and frontend student contracts/notice handling.
- [x] Verify terminal controls reject embedded academic parts/actions; preserve normal
  academic routes and answer-ledger enforcement. Test frontend transport acceptance.
- [x] Run focused Python and frontend checks, review the diff, commit and update progress.

Review focus: mixed academic requests must not be silently dropped; questions about
excluded audiences as system coverage differ from requests for their procedures;
unknown language remains unavailable; user text cannot change the index; no claim of
official approval, complete curriculum coverage, photo support or administrative action.

Runtime reload/live semantic checks will be announced separately; offline fixtures do
not prove real-model intent recognition. Wider audit proposal remains deferred.

## Verification and delivery

- RED: six new control/terminal tests failed before implementation. Two program-mention
  regressions and one mixed-request regression failed before their corrections.
- Existing Python3.13 environment; pytest cache disabled, basetemp under ignored
  `audit-evidence/benchmark-fixes-20261106/system-info-*`. Gates: 337 pass, 266 pass,
  final router/compile/orchestration guard gate 319 pass (overlapping selections).
- Frontend workspace/transport tests: 22 pass. Existing TypeScript `tsc --noEmit`: pass.
- Local model with real reviewed topic menu: four standalone questions select self-info
  with correct EN/Taglish style; mixed capability+INC question finally returns
  `clarify`/`compound_request`. An earlier outage and two incorrect mixed outcomes
  were observed and corrected; no full benchmark or universal intent-accuracy claim.
- Reviewer found program-name resolution and policy-topic repair could override these
  controls; focused regressions now protect both. Normal academic ledgers were not relaxed.
- Dev API reloaded only after offline verification; Luna confirmed ready200 and all
  five service endpoints HTTP200. Keepalive PID72532, API root6780/child30848.
- Context consulted: thesis physical17–18, runtime routing PNG, master architecture,
  undergraduate scope policy. Capability claims checked against routing registry,
  About page and private-PDF confirmation path. USG/CSG are intended source scope,
  not a claim that their full corpus is active. No original-source or release changes.
- Ignored evidence: `system-info-live.json`, `system-info-live-final.json`,
  `system-info-chat-live.json`; HTTP observations are not browser end-to-end metrics.
