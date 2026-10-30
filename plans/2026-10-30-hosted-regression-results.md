---
title: Hosted-parity 50-case regression results
date: 2026-10-30
worktree: p12
branch: p12-evaluation-harness
code_commit: 63b9653
---

# Hosted-parity 50-case regression (30 Oct 2026)

Owner-approved plan: measure the 50 benchmark cases on what students get from the hosted research backend.

## Procedure

- Runner (ignored evidence): `audit-evidence/p12-hosted-regression-20261030/run_hosted_regression.py`. It composes
  like `backend/bintanong_api/research_app.py` `load_research_app`: the hosted pin/seal from
  `hosted-research-api-config.json`, documents (560 chunks) and 39 curricula from hosted release
  `p12-research-faqsplit-20261030`, and `ResearchProvider.pin()` verifying the hosted chunk set and curriculum digests
  before every case. Same cases, judge, Gemma :18088 and short reference profiles as the local runner. The HTTP API,
  browser and sign-in are not exercised.
- The local runner (`p12-regression-20261030/run_regression.py`, 559-chunk local package) is unchanged and stays the
  comparison for the frozen Phase 12 benchmark.
- Owner-run in their own PowerShell, suffix `-hosted2-b1..3`. The first attempt (`-hosted1`) is void: Docker Desktop
  stopped after 3 cases and every later case failed with `model_connection_error`.

## Result

**47/50 on hosted** (single run, post-fix development data, about ±1 run-to-run). No exceptions.

Compared with the last local run (`-owner2`, 44/50, older commits 31064fb/1dc5adb/648c4b5), three cases were gained,
all from the fixes on HEAD: cc5-failed-cc4-en (now Symbolic, ineligible, CC 4/L), disc-smoking-en (II.20 only),
leave-length-taglish ("one (1) academic year"). No case was lost, and none changed because of the document source.

Remaining failures:

| Case | Status | Cause |
| --- | --- | --- |
| summer-load-en | answered, missing "Dean" | Drafting omits the Dean-approval condition of the 12-unit exception |
| grad-residence-taglish | answered, wrong rule | Selector/router chose handbook_residence (1.5x maximum stay) over graduation |
| disc-uniform-taglish | insufficient_evidence | Router chose the II.13 discourtesy row instead of I. Improper Uniform |

Median warm inner time: hosted 29.3 s, local 28.1 s (includes hosted retrieval, about 1.4 s against 0.5 s locally).
These are not student-visible end-to-end times.

## Limits

These 50 cases have been used to develop the fixes, so the score is biased upward and is not the frozen Phase 12 score
(38/50) or a held-out result. Single author and single runs. This is not institutional validation or deployment approval.
