# Handoff: two owner-reported chat failures (4 November 2026)

**Status, 4 Nov (later the same day): fixed on `feat/memory-eligibility` at the owner's request.**

| Item | Commit |
| --- | --- |
| 2: the named-course term slip | `adf20ca` |
| Blank cells mean no prerequisite | `1376e0e` |
| 1: the dependency answer (year standing names no course) | `671ad26` |
| "under that assumption" wording | (this branch, after `671ad26`) |

Live check with Gemma, replaying one chat in the friend's order:
- The CS 13/L what-if answers "Walang course … may CS 13/L bilang prerequisite …" with one note on CS 20's "70% of
  units" condition.
- The CS 17/L question that followed answers "Not yet. You need to pass CS 11/L …".
- "Can I take GE-PS?" answers "Yes. The reviewed prospectus lists no prerequisite …".
- The offline gate passes 15/15 on the real ledgers.

Still open: generic clarifies without a named question. The sections below are the original analysis.

Reported by the owner from the live site, which runs the `feat/memory-eligibility` backend (BSCS 2018–2019). They are
not fixed: the owner assigned them to another developer. Follow the repository workflow: write a failing regression
first, then fix. Background: [results](2026-11-03-memory-eligibility-results.md),
[gate runner](../evaluation/memory_eligibility/README.md).

## 1. "What can't I take if I fail X?" dumps every unresolved course

**Question:** "what if bagsak ako sa CS 13/L, ano 'yong mga subject na hindi ko ma-ttake?"

**Got:** `clarification_needed` with the generic "Paki-clarify muna ang missing information…". After it comes a
"Missing information:" line listing about 25 courses (GE-Elect: ES, GE-CW, CC 1/L, GE-MDS, …), each marked "hindi pa
fully reviewed ang prerequisite rule nito". The UI adds "No specific clarification question was provided."

**Expected (owner):** no reviewed rule in BSCS 2018–2019 requires CS 13/L, so the answer is "no subject". That
conclusion must keep its limitation (source-gap and unknown-versus-unmet rules). A blank or unreviewed cell cannot
prove the course does not depend on CS 13/L. Suggested wording:

> None of the reviewed prerequisite rules in BSCS 2018–2019 require CS 13/L, so failing it does not block another
> course in this prospectus. N courses have a prerequisite that isn't verified in the system yet (mostly blank
> cells), so please confirm with your program adviser if you need to be sure.

**Cause (traced in code; not yet confirmed with a regression test):**
- `dependencies/4` in `backend/algorithms/curriculum_runtime.pl` (lines 83–95) marks the result `partial` whenever
  any course in the whole ledger has an unresolved or unreviewed rule. That holds for every real ledger, whether or
  not those courses relate to the target.
- `assemble` in `backend/bintanong_orchestration/integration.py` (line 55) maps `partial` to status `unknown`.
- `render_text` in `backend/bintanong_generation/render.py` (the `pack.dependencies` block) then prints the generic
  clarification. The student view turns every `rule_unresolved:` code into that "Missing information" list.
- The router's operation is `list_affected_courses`. The "what if" is a request-only premise and does not change
  the listing.

**Owner decision, 4 Nov 2026 (settles most of this):** a blank prerequisite cell means no prerequisite
("those blank literally means no prerequisites… I've reviewed all of the prospectus"). It applies everywhere, not
only to this listing; see the owner decisions ledger and AGENTS.md. Implement it as below. Blank cells then stop
making the listing partial, and this question answers "no subject" with no limitation line. Only the remaining
non-blank unresolved rules (about 89 across the release: printed but unverified conditions, year standing,
self-references) can still make a listing partial.

**Implementing the blank-cell decision:**
- **Where blanks live:** in the ledgers, a blank cell is an `unresolved` rule node whose `reason` starts
  "Printed prerequisite cell is blank". It is matched today in `render.py`'s `unresolved_rule_text` and in
  `term_reply.py`.
- **Map it at bundle preparation or compilation** (`backend/bintanong_symbolic/bundle.py` or `compiler.py`): such a
  node becomes no prerequisite. Keep a distinct marker (for example `verified_none` with an origin `printed_blank`)
  so answers can say "the prospectus lists no prerequisite" and evidence stays traceable to the blank cell. Do not
  edit the stored ledgers or their review digests, and leave every other `unresolved` reason as it is.
- **The effects to verify, each with a regression test written first:**
  - `check_prerequisite_eligibility` on a blank-cell course is eligible.
  - `dependencies/4` no longer counts it under `rule_unresolved`.
  - `assess_term_prerequisites` lists it under "Prerequisites met".
  - The 2 Nov "not listed, confirm with your adviser" wording is retired for blank cells.
- **Tests and checks that will need updating:** these encode the old rule.
  - `tests/test_term_prerequisite_advising.py` (SYN 290 "blank", needs information).
  - The `GE-PS` expectation in `evaluation/memory_eligibility/gates.py` (offline term case) and the
    plan's "GE-PS must remain unresolved".
  - `unresolved_rule_text`/blank wording tests in `tests/test_generation_*`.
  - Grep for `Printed prerequisite cell is blank` and `rule_unresolved`.

**Suggested fix for the listing, smallest first:**
- Answer a `partial` listing with the courses found (here none) plus one limitation sentence that gives the count
  of unresolved courses. Don't list them all, and don't ask a question.
- Keep `complete` versus `partial` in the evidence so the limitation is never dropped.
- Don't make Prolog report `complete` by ignoring unresolved rules.
- Optionally pass the result to Bintu's post-Prolog explanation (`decision_reply.py`), as the term check does.
- Test with a synthetic ledger (one target, one unrelated unresolved course) in English and Taglish, and with the
  hypothetical form.

**Not verified:** the owner recalls this question being answered before. The recorded 3 Nov run
(`Context/sample-query-results-20261103.md`) has no dependency question. On the base branch a "what if" premise
used to end in a generic clarify (`nonasserted_facts`). So check `git show 395079c:` behavior before treating this
as a regression.

## 2. "Can I take CS 17/L next semester? I haven't taken CS 11/L yet." gets a generic clarify in an ongoing chat

**Got (owner's chat):** "Please clarify the missing information before a conclusion can be given." plus "No specific
clarification question was provided." The recorded 3 Nov run passed this question (not eligible).

**Fresh session, 4 Nov, same live server:** correct. "Not yet. You need to pass CS 11/L before you can take
CS 17/L." Rule shown. The router (offline harness) reads it correctly: target CS 17/L, `not_taken` CS 11/L,
asserted, `validated`.

**So it depends on chat state.** Suspects, in order:
1. **The previous turn's conversation context** (for example the CS 13/L question above). With a stored course, the
   router schema offers `previous_course_quote`, which can change the model's output. Look for a
   back-reference/`unresolved_entity`, `model_control` or `model_ambiguity` diagnostic. All of these render the
   generic text.
2. **Session facts from earlier turns** that conflict, or a `taken_unknown` fact for CS 11/L, if the owner stated
   something about it earlier.
3. **A pending check** (`PendingCheck`) is unlikely, because the message has a "?" and names courses.

**Reproduce:** in one chat ask question 1, then question 2. Then try question 2 after an unrelated turn. Log
`routed.diagnostic`, `routed.decision.missing_facts` and `routed.proposed`. In
`backend/bintanong_api/chat.py`, `ChatTurns.run` receives the routing result through `routed_sink`, so that is the
place to inspect it. A diagnostic-only log must not record the question text or results (privacy contract).

**Related gap:** every generic `clarify` without a named missing field reaches the student as "Please clarify the
missing information…" with no question. Any fix should give each diagnostic its own question, or fall back to a
useful reply.

## Minor, seen while checking

In the fresh-session CS 17/L answer, Bintu's explanation said "under that assumption" although the student stated a
real result, not a what-if. The validator only blocks "your record" for what-ifs (`_RECORD` in `decision_reply.py`).
Consider also blocking assumption wording when `pack.assumptions` is empty.
