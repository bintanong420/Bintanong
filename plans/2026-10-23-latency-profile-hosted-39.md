# Latency profile: hosted 39-curriculum release, router v15 (23 October 2026)

Uncounted diagnostic at `14cb53e` (run 12 code). Six accepted questions once each, warm backend,
model container just restarted, `HOSTED=1`. Script: workspace
`audit-evidence/p09-real-data-20261021/latency_profile11.py`; raw `latency11/profile.json`.
Excludes browser, API, network, queueing and cold start (student end-to-end is unmeasured).

| Question | Total s | Routing call (prompt tok / out tok / wall s) | Style s | Answer draft s | Answer check s | Retrieval / Prolog s |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| grade-excellent-en | 35.9 | 3964 / 176 / 15.5 | 4.2 | 9.1 | 4.2 | 1.17 |
| grade-excellent-tl | 35.7 | 3988 / 181 / 14.1 | 4.7 | 9.3 | 4.2 | 1.79 |
| cheating-first-offense-taglish | 32.3 | 3954 / 159 / 12.1 | 4.0 | 9.3 | 4.2 | 0.88 |
| overload-conditions-en | 36.4 | 3960 / 171 / 12.8 | 4.2 | 12.3 | 4.5 | 0.84 |
| cs-cc5-failed-cc4-tl (Prolog) | 23.4 | 3977 / 237 / 17.7 | 4.2 | - | - | 0.42 |
| architecture-...-en (Prolog) | 26.7 | 4000 / 317 / 20.5 | 4.5 | - | - | 0.51 |

Findings: output decoding runs at about 18-23 tokens/s and prompt processing at about 1,000
tokens/s; `cached_n` is 0 on every call because `cache_prompt=false` (profile
`p07-greedy-no-prefix-cache-v1`, chosen 19 Oct for reproducible evaluation). The router call
dominates (12-20 s): about 4 s re-reading the same ~3,900-token prompt and 8-16 s writing 160-320
tokens of JSON. Style call ~4 s, answer draft 9-12 s, answer check ~4 s, ~0.5 s HTTP overhead per
call; retrieval and Prolog together about 1 s. Not a latency distribution (one sample each).
