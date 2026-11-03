# Academic Recovery Planner — ingestion and thesis-bounded scope (4 November 2026)

Owner request, 4 Nov 2026: ingest the owner-supplied plan with repository skills, repository and thesis context,
"thesis bounded scope lang muna". This record places the plan against the thesis; it does not start a phase,
authorize implementation, approve a policy reading or change any gate. Nothing here is institutional approval.

## Source and context consulted

| Item | Location | SHA-256 |
| --- | --- | --- |
| Owner plan (verbatim copy) | [`prolog/Bintanong_Academic_Recovery_Planner_Implementation_Plan.md`](prolog/Bintanong_Academic_Recovery_Planner_Implementation_Plan.md) | `ae1efcd3…54b93962` |
| External thesis copy (owner-supplied, newer, 131 pages) | `E:\Hawksprey\Downloads\development_bintanong_thesis (5).pdf` (not copied into Git) | `614f9e21…dfa7f63` |
| Repository thesis copy (88 pages) | `Context/bintanong_thesis_for_context.pdf` | `72965354…e603c81c` |

Pages read (external copy, physical = printed + 1): Scope and Limitations pp. 17–18 (printed 16–17); background
p. 9; Statement of the Problem and Objectives pp. 12–15; Research Implementation pp. 83–87 (printed 82–86).
Repository copy: same Scope pages (physical 17–18). Code inspected at `837646b3` (`p12-evaluation-harness`, which
already contains `feat/memory-eligibility` through `a18398be`, the plan's baseline).

**Discrepancy recorded:** the two thesis copies differ (hash, length). The external copy is the newer draft; the
repository `Context/` copy was not replaced. Replacing it is an owner decision (below).

## What the thesis commits to (and does not)

- Scope (p. 17–18): undergraduate academic affairs only; read-only advisory; no enrollment, COR or grade changes;
  missing institutional information gets clarification, an unavailable-information reply or an office referral.
- Research Implementation (p. 83): for "how to recover after failing a foundational subject such as CC4/L", the
  neural and retrieval layers explain conversationally and **the symbolic layer verifies which subjects are affected
  by the failed prerequisite**. p. 84 names prerequisites, **subject retaking conditions** and academic procedures as
  the policy-bound rules Prolog verifies.
- Background (p. 9): "Students who need to retake courses cannot properly plan their schedules without enough
  information" (Betrand et al., 2023); p. 10 cites credit-hour thresholds as boolean advising logic (Lugones et al., 2026).
- Objectives (pp. 13–15) evaluate policy correctness versus the Bintu-1 baseline, RAG quality, language handling,
  private-file safeguards and usability. **No objective covers multi-term plan generation, ranking or optimization.**

## Placement of the plan's parts

| Plan part | Thesis-bounded verdict | Why / existing basis |
| --- | --- | --- |
| §1 boundaries, exclusions | In scope; already standing rules | Matches Scope/Limitations and `AGENTS.md` |
| Affected courses after a failure | In scope; **exists** | `list_affected_courses` + `dependency_reply.py` (live 4 Nov: DSA → 13 courses) |
| Next-term eligibility given failures | In scope; **exists** for one prescribed term | `assess_term_prerequisites` (`term_assessment.py`) |
| §3 recovery routes from reviewed policy (retake, off-semester class, special-class request, summer, removal of 4.0/INC) | In scope as **Hybrid explanation with citations** | p. 84 "retaking conditions"; sources reviewed in the release (table below) |
| Single-term conditional check of a proposed set incl. unit load (e.g. a 9-unit summer boundary) | In scope as a **bounded extension**, if the load policy is reviewed into structured data | p. 10 credit-hour thresholds; p. 84 policy-bound rules; one term, no ranking |
| WP1 factual vs hypothetical state | In scope; largely **exists** | memory/eligibility what-if assumptions are request-only |
| WP2 enumerate off-term/special-class actions across terms | Partial: explain options, do not schedule | Must not imply availability or approval |
| WP3 multi-term beam-search solver, ranked alternatives, 4–6-term horizon | **Outside thesis scope — future work** | No objective, research question or evaluation measure; would read as an advising/scheduling authority |
| WP4 `plan_academic_recovery` operation | Only for the in-scope parts above | New operation registration follows the existing allowed-operation registry |
| WP5 plan UI (options, scenario toggles) | Outside thesis scope with WP3 | Depends on WP3 |
| WP6 gates | In scope for the in-scope parts | Reuse `evaluation/memory_eligibility` gates; report per-curriculum numerators |
| §6 four-period BSCS simulation, §7 ARP-01…10 | Keep as **acceptance scenarios for explanations and single-term checks**, not for generated schedules | ARP cases remain useful regression cases |

## Policy evidence already reviewed in the release (`p12-research-faqsplit-20261030`)

| Plan claim | Reviewed topic | Release page |
| --- | --- | --- |
| Prerequisites mandatory; waiver only "in meritorious…" cases | `handbook_prerequisite_policy` | 31 |
| Summer normal load nine (9) units; graduating-student exception | `handbook_summer_load` | 35 |
| No overload with scholastic delinquency in the preceding semester; 28-unit ceiling | `handbook_overload` | 36 |
| Off-semester regular class minimum enrollment; special class maximum fifteen (15) students, assessment fee | `handbook_class_types` | 37 |
| Scholastic delinquency / retention | `handbook_standing` | 39 |
| Removal of "INC" | `grade_completion` | 47 |

The plan's printed page numbers run 1–2 below these release pages (printed versus physical). Applicability to
2026–2027 and any later supersession remain unreviewed; a structured load rule must be reviewed before it is executed.

## Corrections to the plan's baseline notes

- Baseline commit: `a18398be` is now merged into `p12-evaluation-harness` (`d6d3e3ae` on origin; local `b63f2dc3`).
- Gate figures on this machine (branch alone, 4 Nov): offline 14/14, scenarios 12/12, curricula 103/117,
  recorded 56/75 (75 of 113 questions ran; cause not yet established). Fixes since then are not yet re-gated.
- Blank prerequisite cell = no prerequisite is recorded in the owner ledger (4 Nov) and implemented (`1376e0e5`).

## Open owner decisions (not decided here)

1. Approve the thesis-bounded MVP above (affected courses, next-term eligibility, cited recovery routes, single-term
   conditional and load check), with the multi-term solver and plan UI recorded as future work.
2. Whether the unit-load clauses (summer 9 units, overload, delinquency) may be reviewed into a structured rule.
3. Whether to replace `Context/bintanong_thesis_for_context.pdf` with the newer external copy.
4. Whether this becomes a numbered phase; if so, AGENTS.md requires a pre-phase research record first.

## Next action

Owner answers decision 1. No implementation starts before it.
