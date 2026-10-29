# Hosted 560 activation — Codex handoff (30 October 2026)

Owner 30 Oct: hand the remaining mechanical steps to Codex. Worktree `p12`, branch `p12-evaluation-harness`.
Evidence folder (ignored): `A = C:/Coding-projects/bintanong_workspace/audit-evidence/p12-hosted-560-activation-20261030`.
Python: `PY = C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
Run every script from the p12 worktree root. Read `AGENTS.md` first; owner decisions are the last five 29–30 Oct
entries of `plans/owner-decisions-ledger.md`. Do not re-ask them.

## Done (do not repeat)

- Receipts: `A/prepare_receipts.py` -> 4 cumulative supplementary receipts, 26 event envelopes, selected review
  over all 560 chunks (scope `17e11149…`). The 257 re-authored records are labelled as validated by the owner's
  29 Oct activation directive, with no per-chunk human approval (ledger).
- Migration `5739bee`/`222d9ab`: selected review accepts `flow_manifest` groups. **Already applied to hosted**
  (version 20261029145841; service_role execute only).
- Backend `48330f7`: the pin names `release_id` / `research_authorization_ref`; `"composition": "gate"` gives a
  hosted pin topic selection and routing context. Tests: related 108 pass.
- Local rehearsal PASSED (`A/rehearsal-result.json`): 560 chunks/vectors, 39 links, replay no-op, anon and
  authenticated 560 visible, probe hit, rollback 78, existing rows preserved. Slow RPCs: record review 36 s,
  bind 34 s, activate ~122 s. Hosted REST has an 8 s statement timeout, so `A/hosted.py` sends those release RPCs
  over psql (`SUPABASE_HOSTED_DB_URL`, same functions, `service_role`, 1800 s timeout).
- Hosted snapshot `A/hosted-before.json` (active corrected78, 479 chunks). Hosted data otherwise unchanged.

## Steps

1. **Prerequisite:** the owner adds `SUPABASE_HOSTED_DB_URL=` (Session pooler URI) to `p12/.env`. Never print,
   log or stage it. `hosted.py` refuses a URL that does not name project `jyrudbiuajahsucsorco`.
2. **Stage** (inactive; nothing becomes visible): `$PY A/hosted.py stage > A/hosted-stage.log 2>&1`.
   Expect `A/hosted-staging-result.json` with `staged.chunks == 560`, `runtime_visible == 78`. Each step reads
   hosted state first and skips only exact earlier results. On any assertion: stop and inspect; never blind-retry.
3. **Hosted pin/config** (before activation): copy `audit-evidence/p11-local-documents-20261029/local-research-pin.json`
   to `A/hosted-research-pin.json`, remove `documents`, set `release_id: p12-research-faqsplit-20261030`,
   `research_authorization_ref: research-owner-20261029`, `composition: gate`. Copy its `research-api-config.json`
   to `A/hosted-research-api-config.json` with the new `pin_path`/`pin_sha256` (seal unchanged). First verify that
   package's chunk_id->content_hash map equals `A/bound-chunks.json` (readiness compares it with hosted).
4. **Activate:** `$PY A/hosted.py activate > A/hosted-activate.log 2>&1` (several minutes). It checks: active =
   new release, anon REST sees 560 chunks and 39 links, retrieval probe hit; otherwise it rolls back to corrected78
   automatically and exits non-zero. Manual rollback: `$PY A/hosted.py rollback`.
5. **Website smoke on hosted:** start the backend with `BINTANONG_RESEARCH_CONFIG=A/hosted-research-api-config.json`
   (precedent `p11-local-documents-20261029/start_research_api.py`, `http_smoke.py`): document, structured, hybrid
   questions answer with citations. Note: after activation the old local-documents config stops at startup
   (its pin defaults to corrected78), so switch to the hosted config, or give the local pin the new release fields.
   Answer-quality validation (benchmark on the hosted composition) is the owner's/Claude's follow-up, not this handoff.
6. **Docs:** write `plans/2026-10-30-hosted-560-activation-results.md` (the selected review's `decision_document`
   path; it must exist): commands, results, timings, the psql path and its reason, the flowchart SQL check's scope
   (geometry/span digests remain Python-checked), the hosted composition change. Update report section 8
   (`docs/evaluation/phase12-evaluation-report.md`), then the Phase 12 handoff, supersede the checkpoint,
   `phase_state.py validate` / `can-advance`, INDEX and current progress (compact snapshots).

Commit small units with Conventional Commits and no attribution trailers. No dependency/model changes. Research
build only: no institutional approval or public deployment is implied.
