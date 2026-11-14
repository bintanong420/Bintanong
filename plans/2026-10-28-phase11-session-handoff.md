---
artifact: session-handoff
phase: 11
status: ready_to_resume
verified_code: 04e6d38
verified_delivery: 2112d62
date: 2026-10-28
---

# Phase 11 session handoff (28 October 2026)

Resume p11 / `feat/p11-backend-api`. Phase 11 stays active and Phase 12 is not permitted. This is a session snapshot,
not phase completion, school approval or activation. Nothing has been pushed. Supersedes the
[27 Oct CLI handoff](2026-10-27-phase11-cli-handoff.md) as the resume point.

## Resume order

1. Read `AGENTS.md`, the two Bintanong skills, [INDEX](INDEX.md), [progress](plan_current_progress/current_progress.md),
   [checkpoint](phase-11-checkpoint.md); run `python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .`.
2. Read the [simple-question gate results](2026-10-28-simple-question-gate-results.md) and the
   [workstream split](2026-10-28-phase11-model-workstream-split.md) (Claude lane: answer quality, review and merge).
3. Resume the next action below. Tests: shared venv
   `audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe -X utf8 -B -m pytest -q -p no:cacheprovider`
   with basetemp under workspace `audit-evidence` (system Python has no pytest). Model: Docker container
   `bintanong-p09-cuda-latency` on `:18088` (`docker start` after laptop sleep).

## Delivered this session (all committed, local only)

| Area | Commits | Evidence |
| --- | --- | --- |
| All-of wording guard ("must be met", "and e)") | d49aa27 | live cross-enroll lists a)–e) as printed |
| Shifting clarify, option A (fictional destination example) | 04e913f, 12ac411 | two grammar attempts reverted (8cce770, eedbc07) |
| Codex lanes merged: A Charter layouts 41/44 | e574d67 | B frontend/auth/sessions 307a2bd, df3811a |
| Guest mode (owner: full features incl. temporary PDF upload, login kept) | 04e6d38 | master 25.1 amended 23e83aa; reviews a137696, 3eb411b |
| Answer only the detail asked (requirements/fees/processing_time/specific/whole) | 5ed4c98, 6961e64, 84ef585, 2112d62 | all 41 parsed services render each detail in en/Taglish |
| Router v24: not yet passed / not taken = failed claim | 289cf4b | gate C 7/7 fixed |
| Single-detail parts skip whole-procedure coverage | a6bc52a | substitution deadline passes en/Taglish |
| Owner-resolved source limits (year-level overlap, no note) | 2189faf | second-year (en) answers as printed |

Full suite on merged head `04e6d38`: 7198 passed, 1608 subtests, 6 skipped, 2 xfailed, exit 0 (2021.94 s).
Later code commits `a6bc52a`, `2189faf`, `2112d62`: wide focused runs pass (1287, 1478, 1618) and the affected
live cases were checked. **The full suite has not run since `04e6d38`; run it first.**

## Simple-question gate (owner-accepted coverage, 91 cases)

Run 1: 58/91 (61 adjusted). Run 2 (`e193093`): 67/91 (70 adjusted). Three expectations are over-strict, not
system errors (summer load answers the asked normal load; Taglish leave says "isang (1) academic year").
Builder/runner/cases: workspace `audit-evidence/p11-simple-gate-20261028` (`build_cases.py`, `cases.json`, `run_gate.py`;
`GATE_ONLY=id1,id2 GATE_SUFFIX=-x` runs a subset). Mark `LIVE RUN` in current progress while using the model.

Remaining failures:
- **Group A, about 18 cases: wrong topic or claim.** Drop subject goes to DAC policy, not the drop/shift FAQ;
  probation goes to discipline, not standing; certification fee goes to TOR copy; transfer goes to the Handbook,
  not the Charter table; diploma, DAC and overdue fine pick a not-stated/limit claim instead of printed fields;
  honors residence picks general residence; refund requirements go to the Handbook clause, not the Charter
  checklist; Law admission is answered as general admission instead of the undergraduate-scope notice;
  2 transient `temporarily_unavailable`.
- Taglish "Kailan ako considered second year?": empty router clarify (same family as the old shifting case);
  not retried further under the stop rule.
- Grad residence: the question matches two clauses (graduation 1.4 one year vs general residence period).

## Owner decisions this session (recorded in the owner ledger)

Answer only the asked detail, whole when asked how/everything. No program given means ask program and curriculum,
and the frontend asks up front. Students type a code or a title ("CS6 (title)" not handled). Keep login, add guest
mode with full features. Year-level overlap shown as printed without a note. Gate coverage accepted in principle,
with prerequisites diversified across 14 curricula.

## Next action

1. Full suite on the current head (≈34 min, exclusive slot).
2. Group A, test-first: diagnose each wrong pick (selector vs router claim choice), fix the shared cause, then a
   full gate rerun (≈50 min, model slot). Target 91/91. Do not tune on gate wording (evaluation stays separate).

## Boundaries

559 package stays inactive; active corrected78/39 unchanged; no hosted writes, pushes, dependency or model changes.
Real PSU sign-in verification is owner-deferred. Codex lanes are idle; coordinate slots per the split plan.
