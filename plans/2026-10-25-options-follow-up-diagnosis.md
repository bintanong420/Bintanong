# Options follow-up: read-only diagnosis

25 October 2026. Owner requires frontend focus and no backend changes for this issue.
No application code, prompt, runtime configuration or institutional source was changed.

## Intended behavior

After listing CC5/L prerequisites and supplying CC4/L not passed/CC3/L passed,
the owner asks: "What choices do I have to pass it?" The owner clarified that this
means both documented options for the unmet course and ways to become eligible
for the target course, grounded in institutional data. Do not invent alternatives.

## Reproduction

Reused the existing full research-composition probe with one isolated session and
synthetic completion premises in BSCS2018–2019. Current v22, same active19-chunk
release and actual model/Prolog. Three turns:

1. "What's the pre-req of CC5/L": prerequisite list and completion clarification,
   PASS,61.19s.
2. Original question plus CC4/L not passed and CC3/L passed: answered, documented
   condition unmet, PASS,74.70s. First interpretation failed counted-parts validation;
   the existing repair corrected it. No new repair was added.
3. "What choices do I have to pass it?": exact generic clarification reproduced,
   FAIL,30.11s. Probe assertion exited1 as expected for the reported defect.

Ignored evidence under workspace audit-evidence/p11-20261025/clarification-loop/:
choices-cases.json; choices-v22/results.json and *-captured.json. Command: set
BINTANONG_PROBE_CASES/OUTPUT to these paths, then system Python3.13 -X utf8 -B
try_three_prompt_lines.py. This uses ChatTurns/ResearchPipeline directly, not owner auth.

## Where it stops

- Frontend sendStudentMessage sends the current text, scope and same-origin session
  credentials. The backend's previous course context is present in the captured
  third-turn prompt: previous_turn.course_available=true. No transcript is sent.
- The interpreter recognizes the intent as seeking options to pass a course and
  supplies previous_course_quote="it", but emits no course mention/operation and
  marks the requested part evidence_need="unknown", with no ambiguity question.
- Router validation returns unknown_requirement/control=clarify, route=null,
  missing_facts=[]. Orchestration returns immediately, before document retrieval.
- Generation renders the fixed generic clarification. The API supplies no concrete
  course/scope clarification fields; the frontend displays the response as received.
- Offline replay through current Router confirms unknown_requirement, empty missing
  facts and no resolved course entity. Command: py -3.13 -X utf8 -B
  <workspace>/clarification-loop/replay-choices.py; output offline-diagnostic.json.

The prior course exists in session context, but that does not give the interpreter
the prior answer's unmet-course explanation. ConversationContext stores identifiers,
not the answer or inline completion assertions. Carrying CC5/L does not authorize
guessing that "it" means CC4/L, nor does a prerequisite result prove a retake exception.

## Boundary and remaining work

This exact clarification is reproducible without the frontend. No transport patch
is justified by this trace. A frontend can help a student phrase an explicit next
question; it cannot provide verified institutional options when retrieval never ran.
Per owner direction, do not change the backend interpretation or invent policy in UI.
The options follow-up remains unresolved. Source coverage for retake/alternative
options has not been assessed by this run, and an explicit rewrite is not a proven fix.
No new tests/build are necessary for this documentation-only diagnosis. Existing
production preview stays running; no restart, push, DB write or source activation.
