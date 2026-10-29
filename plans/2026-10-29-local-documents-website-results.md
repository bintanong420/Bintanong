# Website on the local 560-chunk package — results, 29 October 2026

Owner option A ("lets do the A ... prioritize MVP"): the website backend answers from the gate-tested local
560-chunk FAQ-split package instead of hosted Supabase's 78 chunks. Hosted activation of the 560 package is
deferred (about 2-4 hours of governed staging); the hosted release stays `p11-research-corrected-20261026`.

## Finding

The research app (`research_app.py`) searched hosted chunks, accepted only a 78-chunk package, and did not enable
topic selection, routing context or short review references. The 91-case gate therefore measured a composition the
website did not run.

## Change (`d1a2d53`, test-first)

RED 3 fail / 14 pass -> GREEN 17 pass; related API/runtime/orchestration 356 pass. A pin with `documents: local`
serves its sealed package locally with routing context, topic selection and the pin's review reference profile.
Hosted pins keep the 78-chunk check and hosted chunk comparison. Curricula and links stay hosted and checked.

## Live HTTP check (guest, single uvicorn worker, Gemma :18088)

Evidence: ignored `audit-evidence/p11-local-documents-20261029` (pin, config, sealed runtime package, smokes).
Startup 120 s (curricula 16 s, encoder, resources 53 s); `/health/ready` 200.

| Path | Question | Result | Seconds |
| --- | --- | --- | ---: |
| Document | Honors residence | answered: two years, 75% of units; cited | 38.2 |
| Structured | CC 5 after failing CC 4 | unmet condition; CC 3/L unknown | 27.5 |
| Hybrid | CC 5 after passing CC 4 + how to drop | clarification for CC 3/L; drop part not reached | 31.8 |
| Upload | synthetic grade PDF -> confirm -> "Can I take CC 5 now?" | 2 rows, 2 facts; conditions satisfied | — |
| Deletion | upload delete, repeat, session delete | 204, 404, 204 | — |

Times are one warm backend request each (API/stream included; browser, network and queueing excluded).

## Remaining

- Student text shows short evidence aliases such as "(e2)"; plan task 3 (student render profile) is not done.
- Hybrid asks the curriculum clarification before answering the procedure part.
- Browser (Next.js) check on this backend not yet run; hosted activation deferred.

## Browser check (owner: "Browser check, then close", 29 Oct)

Playwright MCP, guest, Next.js dev on :3216 (run from the `p11-frontend-integration` worktree: same app code, its
installed packages; this worktree lacks `@supabase/ssr` in `node_modules`, no install made), backend on the local
560 config, Gemma :18088. Evidence: ignored `audit-evidence/p11-local-documents-20261029/browser`.

| Step | Result |
| --- | --- |
| Landing, chat, curriculum picker | 39 curricula load; BSCS 2018-2019 selected |
| Honors residence (document) | two years / 75% of units; Sources (1): PSU Student Handbook.pdf p.53; no "(e2)" alias |
| CC 5 after failing CC 4 (prerequisite) | documented condition unmet; CC 3/L asked; Sources (4) |
| Upload synthetic PDF, mark both rows Passed, save | 2 rows with printed marks; "Selected course details saved" |
| Follow-up "Can I take CC 5 now?" | conditions satisfied (CC 4/L, CC 3/L passed) |
| Remove file, ask again | file list empty; asks which of CC 3/L and CC 4/L were passed |
| Console | 0 errors |

Prerequisite answers took about 60-70 s in the browser (single observation; not a latency measurement).
