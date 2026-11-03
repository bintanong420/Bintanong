# Memory and eligibility: implementation plan (3 November 2026)

Source requirements: [owner plan](prolog/Bintanong_Backend_Memory_and_Eligibility_Plan.md) (Tasks 1–4 + addendum).
Branch `feat/memory-eligibility` (worktree `p12-memory-eligibility`), from `395079c`. The owner asked to
implement the plan on another branch, so it is the approved baseline; this is not a numbered phase and authorizes no
release, activation or scope change. Undergraduate scope, source-gap and unknown-versus-unmet rules apply unchanged.

Context consulted: owner plan, AGENTS.md, current progress (3 Nov), chat/session/routing/orchestration/generation
code at `395079c`, and arXiv 2602.17999 "Aurora". Aurora uses the same next-term design as Task 4: a lookup lists the
candidate courses, Prolog checks each one, and the LLM only phrases the answer from checked evidence. Its
unlock-weight roadmap planner is out of scope (YAGNI; the plan separates prerequisite results from recommendations).

## Design

| Task | Change |
| --- | --- |
| 1 Capture | Claim states gain `not_passed`, `not_taken` and `taken_unknown`. Enrollment stays a separate dimension. A host check (`routing/claim_evidence.py`) reads each course's own clause in en/fil/Taglish. It only keeps a state the student's words support. A `passed` claim without pass words becomes `taken_unknown` or is dropped. A negated course is never stored as passed. Hypothetical claims apply only to that check and are labeled as assumptions. Reported claims contribute no fact. A message that only states results is acknowledged as a noted fact. |
| 1 Projection | `passed` satisfies a completion check. `failed`, `not_passed` and `not_taken` are noncompletion. `taken_unknown` supplies nothing. An enrollment fact counts only when its period (`current`/`next`) matches the period the question asks about. |
| 2 Memory | `ScopedFact` carries `source` (`user_statement`/`private_upload`), an opaque turn `ref` and an enrollment `period`. A turn's accepted asserted facts and its pending check are committed together with turn completion, under the session lock. A failed or cancelled turn commits nothing. A newer self-report replaces an older one for the same course and dimension. A disagreement with a confirmed upload stays a conflict, and the student is asked to clarify. |
| 2 Pending | When a checked answer is missing exactly one student result, the session keeps a `PendingCheck`: scope, operation, target, the missing course and its dimension, and the printed codes. A bare reply ("Oo, pasado", "not yet") in the same scope becomes that fact. The host then re-asks the original check in the reply's language. Any other completed turn retires the pending check, and so does a scope change. |
| 3 Answer | The host writes the conclusion first. It uses both/either/same-term wording, keeps blank, missing and reviewed-"None" rules apart, and asks a targeted question for a missing result. A bounded post-Prolog Bintu call adds an explanation. The validator rejects drafts that use another course code, a reversed verdict or an enrollment promise. On failure or timeout the host text stands alone. |
| 4 Term | New router operation `assess_term_prerequisites` (term target). The adapter lists reviewed term courses and runs `check_prerequisite_eligibility` on each with the same facts and release. A term with no ledger rows is reported as not covered, never as empty. Results are grouped as met, blocked, or needs information, with already-passed courses kept separate. |

## Verification

TDD per task with synthetic fixtures, plus the release ledgers where existing tests already use them. Run the plan's
PowerShell suite and the full default `tests/` suite before completion. Live `POST /chat` runs over the 39 curricula
need the model stack, which is stopped on this machine; until someone runs them, those gates stay open and are
reported as such.
