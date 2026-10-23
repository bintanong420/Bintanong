# Multi-turn follow-up observation (Phase 10 task 4), 23 October 2026

Stack: hosted research release (old BSCS curriculum for course cases), real SEA-LION-E5 encoder, Gemma 4 E4B
(`bintanong-p09-cuda-latency`, :18088), SWI-Prolog. One attempt per turn. Session store, `capture` and
`follow_up_context` are as built in Phase 10. Runner: workspace
`audit-evidence/p10-20261023/multiturn.py`; raw output in `multiturn{1..5}/results.jsonl`.

These are author readings, not an accuracy rate. Cases F1-F7 were owner-accepted on 23 Oct. F4 was revised
and F4b added with owner approval after precheck 1. D1-D4 were added at the owner's request. Precheck runs
1-4 drove fixes. Run 5 is the counted run at `ea64ead`.

## Counted run 5

| Case | Turn 2 | Result |
| --- | --- | --- |
| F1 en / F2 fil / F3 taglish | "What else is missing for it?" and variants | CC 5/L (reference resolved by the host); missing-prerequisite check |
| F4 | "What are its prerequisites?" after "If I failed CC 3, can I take CC 5?" | CC 5/L |
| F4b | "What are its prerequisites?" after a two-course comparison | clarification (no course stored) |
| F5 | "What about CC 4?" | CC 4/L (named course wins) |
| F6 / F7 | unrelated document questions after a CC 5 turn | answered, no course carried |
| D1 en / D2 fil | "How about a grade of 3.0?" / "Saan ako magbabayad niyan?" | same topic kept; the detail is not in the reviewed facts, so the answer is withheld (no invention) |
| D3 taglish | "Eh pag second offense na?" | clarification |
| D4 | an unrelated document question after the vehicle fee | answered on the new topic (overload) |

Outcome: 12/12 resolve or clarify, and there are **0 wrong carry-overs**. The single-turn system prompt
(`6a9c2e7e...`) and schema (`7cde5320...`) are unchanged. The single-turn roster rerun is reported separately.

## What the prechecks found and fixed

1. Run 1: "Can I take CC 5? I passed CC 4." stored no course under the exactly-one-course rule. Fixed by
   storing the check target (owner-approved).
2. Owner direction: most messages are new questions. Carried scope now only fills an unnamed scope for a
   course check or back-reference. Document questions keep their own scope, and the instruction says to
   ignore the previous turn unless the message clearly refers back.
3. Run 2: an unscoped follow-up hid the stored course from the router. Fixed so the shown course follows
   the same gap-fill rule.
4. Runs 3-4:
   - Gemma copied a shown course code instead of the student's "it". The fix signals `course_available`
     without the code and makes the field required, decided before mentions.
   - A single operation now repairs an out-of-range part index.
   - Gemma marked "CC 4" itself as the reference, a wrong carry-over in run 4. The fix: words that name a
     course are never a back-reference.

## Limits (disclosed)

- Turn-1 statements ("I passed CC 4") are not carried, by design (master 23: a carried course never
  becomes a fact). So F1-F4 ask for completion information the student just gave. Carrying stated facts
  would be a separate owner decision.
- Topic carry only keeps the subject. D1/D2 follow-ups asked for details outside the reviewed facts.
- Taglish follow-up host lines came out mostly in Filipino, the known Phase 09 Taglish style limit.
- Twelve cases, one attempt each. This is not a multi-turn accuracy rate. The Phase 12 evaluation family
  (separate from prompt examples) is still required.
