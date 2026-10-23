# Requirement: conversational follow-ups (session context), 23 October 2026

Status: thesis-derived requirement recorded at the owner's request; not designed or implemented.
Not in the master plan's Phase 10/11 deliverables, so it must be added explicitly when planned.

## Thesis evidence (Context/bintanong_thesis_for_context.pdf)

- Physical p.7: existing systems "may not adequately handle differently worded, ambiguous,
  multi-step, or conversational inquiries"; the LLM is "for conversational response generation".
- Physical p.65 (ethics): "Each student's conversation with Bintanong will be stored and processed
  independently within an isolated user chat context. No student will be able to access or
  influence another student's chat session." Same page: no personal academic records retained.
- Research question 6 (usability/user acceptability): students will naturally ask follow-ups.
The thesis does not specify how follow-ups are resolved.

## Current behaviour (verified in code, 23 Oct 2026)

Each request is answered alone. `RequestContext` carries only session id, program, curriculum and
stated facts; router and generator never see earlier turns. "What are its prerequisites?" or
"What is step 1?" after an earlier question has nothing to resolve against and clarifies (safe).

## Proposed shape (owner discussion, to be designed before coding)

- Carry structured context only: the previous turn's resolved topic/subject, course and curriculum,
  in session memory with expiry (Phase 10 session store, proposed 30-minute idle lifetime); never
  the full transcript, never persisted to Supabase; cleared on deletion/expiry.
- Router receives that context; host checks a follow-up reference points to a real earlier entity;
  ambiguous references or topic switches ask instead of guessing. Retrieval/Prolog run as normal.
- Cost estimate: a few identifiers per session; ~50-150 extra prompt tokens (~0.1-0.2 s with reuse).
- Effort estimate (not measured): code ~1-2 days; new multi-turn en/fil/Taglish cases (follow-ups,
  topic switches, ambiguous "it") and a counted accuracy run take longer. Prompt changes can shift
  other outputs (router v15 lesson), so a full roster rerun is required.
- Placement: session store Phase 10, `POST /chat` wiring Phase 11; the backend core and evaluation
  can be built first. Owner decision needed on timing.
