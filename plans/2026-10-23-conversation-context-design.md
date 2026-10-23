# Conversation-context design (Phase 10 task 4; master 23)

23 October 2026. Implements the backend part of [the requirement](2026-10-23-conversation-context-requirement.md).
Design choices are technical. Owner-level boundaries (session-only, no transcripts, clarify instead of guessing)
come from master 23 and are unchanged.

## Stored context (session memory only)

`ConversationContext`: `program_id`, `curriculum_id`, `course_id | None`, `subject_id | None`. It holds ids only:
no text, no grades, no transcript. It is captured after a validated turn from the ids the turn actually used.

The course kept is the target of the turn's eligibility/prerequisite check. This rule was revised 23 Oct
after the uncounted live precheck, with the owner's approval. "Can I take CC 5? I passed CC 4." keeps CC 5. The
first rule, "only when exactly one course was mentioned", kept nothing there, so natural follow-ups failed.

Without a check, a course is kept only when the turn mentioned exactly one. Two mentioned courses with no check
keep nothing, so a later "its" clarifies instead of choosing. The context lives in the `SessionStore` slot and
expires or is deleted with the session.

## Router input

- No stored context: the messages and schema are byte-identical to today's (wire v4). Single-turn behaviour
  cannot shift from this change.
- With stored context, three additions:
  1. The user JSON gains `previous_turn`, holding the printed course label and/or subject id.
  2. One instruction says that if the message refers back to that course without naming it ("its",
     "that subject", "niya"), quote those words in `previous_course_quote`, and otherwise leave it null.
  3. The schema gains that optional quote field.
  These add about 50-100 tokens.

## Host checks (deterministic)

- The quoted words must occur in the message. They become a course mention whose entity comes from the stored
  `course_id`, never from the model, and must still be a catalog entry in the request's program/curriculum.
  Otherwise the result is `unresolved_entity`, which leads to a clarification.
- A reference without a stored course also leads to clarification.
- Most turns are new, unrelated questions (owner, 23 Oct). The previous turn rides along as context only.
  Its program/curriculum fill scope only when the new message has a course check or a back-reference and
  names no other program. A newly named program wins, and a document-only question keeps its own
  (unscoped) retrieval. The router instruction says to ignore `previous_turn` unless the message clearly
  refers back.
- Retrieval and Prolog still run fresh. A carried course never becomes a fact or a grade. Unknown versus unmet
  is unchanged. Reply language follows the current message, because the style call sees only the current text.

## Evaluation

Multi-turn synthetic tests cover resolution, no stored course, two antecedents, out-of-scope carry, topic
switch, cross-session isolation, expiry and delete. Exit still needs multi-turn en/fil/Taglish cases and the
counted roster rerun on the live model (master 23.4).
