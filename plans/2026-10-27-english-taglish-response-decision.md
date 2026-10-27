# Owner decision — English and Taglish replies

**Accepted27October2026.** Owner explicitly retires exclusive Tagalog/Filipino
replies while retaining Tagalog input. The owner clarifies the purpose:
“this is to lessen the burden and to improve the response time”.
This supersedes the earlier Filipino-question -> Filipino-reply requirement;
the owner has already authorized this product requirement change.

## Required behavior

| Student input | Default reply |
| --- | --- |
| English | English |
| Filipino/Tagalog | Taglish |
| Taglish | Taglish |

Supported replies are English and Taglish. Filipino/Tagalog remains supported
input;retain its recognition,routing and accepted question families. Keep English
policy terms,course titles,office names and exact source quotations where needed
for fidelity. Match casual/formal register naturally. Internal input/legacy evidence
labels may still use `fil`;that does not authorize a new exclusive-Filipino reply.

## Rationale and limits

The owner wants less effort maintaining a separate exclusive-Filipino response
target and better response time with mainly English sources. This is a product
choice;accurate Filipino translation is not established to be technically impossible.
Latency improvement is intended,not measured or a new SLA. Reuse the existing
accuracy-first latency contract and15–20s warm student-visible proposal;required
retrieval,Prolog,evidence/privacy guards and answer validation remain. Removing
an output target alone does not prove fewer model calls or faster full answers.

## Acceptance criteria and migration

- English input -> English;Filipino/Taglish input -> Taglish across RAG,Symbolic,
  Hybrid,clarification,greetings and fixed host notices.
- Prompts/schemas,generation/checker instructions and host result lines consistently
  use two reply targets. Keep style evidence literal;do not invent English fragments
  in a Tagalog-only question merely because its reply will be Taglish.
- Preserve accepted question wordings and Filipino comprehension. Version current
  expected reply styles under this new policy;keep historical runs,raw labels,
  traces and approvals unchanged. Report changed targets explicitly.
- Evaluate routing/claim/status correctness separately from reply style by input
  language,and measure latency using the existing stage/end-to-end boundaries.
- Reflect revised input/output scope in later methodology/UI guidance. Original
  thesis/source files,undergraduate scope,source holds and privacy gates remain.

## Current implementation state

Implemented in28edea4underTDD;[migration results](2026-10-27-english-taglish-migration-results.md)
separate input family and reply targets,retain legacy raw records,and report actual
observations/remaining limitations. Full suite6974passed/1595subtests,6skip/2xfail.
The style prompt is95tokens smaller on matched probes;latency benefit remains
unproven. No expanded-corpus activation,frontend integration or phase advance.
