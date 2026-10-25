# Review of pre-Phase11 notes: conversational follow-ups

25 October 2026; documentation/code-history review only, requested by the owner.
Current options-follow-up diagnosis remains [separate](2026-10-25-options-follow-up-diagnosis.md).

## Notes reviewed and their meaning

- [Phase07 handoff](phase-07-handoff.md): routing contracts and validation were
  delivered, with semantic/style limits. Passing structural tests did not establish
  general interpretation accuracy or final student-response quality.
- [Phase08 handoff](phase-08-handoff.md): evidence routes and explicit failure states;
  synthetic integration, no actual-model end-to-end accuracy claim or student API.
- [Phase09 handoff](phase-09-handoff.md): last roster63 had25 answered,19 clarification,
  19 insufficient. Router over-reading, prompt sensitivity and all-or-nothing answers
  remained disclosed. Earlier failed observation candidates are historical evidence,
  not the final selected runtime's current score.
- [Conversation requirement](2026-10-23-conversation-context-requirement.md): explains
  the initial lack of follow-ups before Phase10. Its "not implemented yet" status is
  historical and superseded by the design, implementation and final handoff.
- [Conversation design](2026-10-23-conversation-context-design.md): context stores
  program/curriculum/course/topic IDs, no transcript or grades. A prerequisite check
  stores its target, e.g. CC5, even when the student also mentioned CC4. Ambiguous
  antecedents clarify. Retrieval and Prolog must run fresh.
- [Multi-turn results](2026-10-23-multi-turn-observation-results.md): final precheck
  changed printed-course input to course_available=true because the model copied
  the printed code as a quote. This supersedes the design's older printed-label text.
  Twelve cases/one attempt each passed resolve-or-clarify with zero wrong carry-over;
  clarifications and withheld unsupported details are included as successful outcomes.
- [Phase10 handoff](phase-10-handoff.md): explicitly discloses that inline earlier
  completion statements are not carried, repeated grade questions are possible, and
  the12 cases establish no accuracy rate. HTTP/session wiring belongs to Phase11.
- [Owner ledger](owner-decisions-ledger.md):23Oct requires conversational behavior,
  session-only structured context, and remembers the check target with owner approval.

Supporting review:20Oct fast-reply session handoff and router-understanding/question-
parts results;21Oct task-first results. These distinguish software contract success
from actual-model quality, reject failed candidates, and preserve unknown safeguards.

## Checked against Git

Phase10 counted-run commit ea64ead versus current tree: conversation.py byte-equivalent
after newline normalization; FOLLOW_UP_INSTRUCTION equal; previous_turn function AST
equal. This confirms those mechanisms were inherited. Other router instructions,
operations and validation have changed since Phase10; model behavior may therefore
differ. No old-version inference was run, and no first-bad-commit claim is justified.

The earlier case roster covers prerequisite references, named-course changes, topic
switches, ambiguous antecedents and unavailable documentary details. It does not
cover "What choices do I have to pass it?" after an unmet-prerequisite result.
Not carrying inline grades is a disclosed design limit; it is not proven to be the
cause of the current unknown_requirement. That interpretation failure remains open.

## Consequence for current work

Phase10 completion did not certify general recovery/alternative-options dialogue.
Phase11 wiring should preserve the existing boundaries. No frontend transport fix
is established by these notes; no prompt, guard, fact-persistence or backend change
is authorized by this review. Keep the failed current trace as the regression case.
No model calls, application edits, server restarts, dependency changes or DB writes.
