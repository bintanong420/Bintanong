# Conversation test set (follow-ups and clarification)

Fixed multi-turn conversations for the thesis leader's "conversationality" and "follow-up clarification" testing:
term, course and detail follow-ups, stated results, corrections, topic switches, transfer, shifting, bare program
names, track switch, the DSA failure question, out-of-scope notices (Law/Medicine/graduate), a greeting and the
recovery Ask mode. `cases.json` holds 35 conversations of 1-3 turns in English, Filipino and Taglish.

## Run (the coordinator, against a live GUI)

```powershell
python evaluation/conversations/run_conversations.py                       # all, GUI on http://127.0.0.1:3216
python evaluation/conversations/run_conversations.py --base http://127.0.0.1:3216 --out <ignored dir> dsa-failed term-bscs-2y1s-3y
```

Standard library only. Each conversation uses a fresh session cookie, so one conversation never spends another's
rate-limit budget; a 429 is retried after `Retry-After`. `--out` must be outside the repository or an ignored folder
(default `C:\Coding-projects\bintanong_workspace\audit-evidence\p12ct-conversations`). It writes
`conversations-<stamp>.json`, a `.md` report and a `-partial.json` that survives an interrupted run. Exit code 1 means a
non-pending conversation failed.

## What a turn checks

`expect.status` (`answered` / `clarification_needed`, or null = not checked), `required` (all substrings, e.g. course
codes, "Php 100.00"), `required_any` (at least one), `forbidden` (plus the global defaults "temporarily unavailable" and
"Paki-clarify muna ang missing information"). Matching ignores case, spacing and curly apostrophes. A reply must be
non-empty. A conversation passes only if every turn passes.

Cases with `"pending": "<track>"` expect behaviour that is not implemented yet (bare program name, track switch,
shifting referral, recovery Ask mode). They are reported in their own section and do not affect the exit code.

## Limits

- Facts (codes, prerequisites, "Php 100.00") come from `Context/sample-query-results-20261103.md` and the
  memory/eligibility results; transfer cases assert no institutional fact and only check the forbidden strings.
- The runner sends the program and curriculum like the GUI picker; the program id is derived from the curriculum id.
- Passing is research evidence for this build. It is not school validation, institutional approval or a currentness claim.
- Offline structure check: `python -m pytest tests/test_conversation_cases.py -p no:cacheprovider`.
