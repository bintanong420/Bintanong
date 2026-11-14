# Memory and eligibility gates

These scripts check the memory/eligibility branch against the owner plan
(`plans/prolog/Bintanong_Backend_Memory_and_Eligibility_Plan.md`). Results so far are in
`plans/2026-11-03-memory-eligibility-results.md`. Every gate sends a question through the same chat turn path as
`POST /chat`: chat memory, the Gemma router, Prolog on the release's reviewed ledgers, Bintu's explanation, then host
validation. Two parts are left out: the HTTP stream, and document retrieval (no encoder is loaded). So only
structured questions are asked.

## Setup (on the machine that runs them)

PowerShell, from the repository root, with the project venv (Python 3.13):

```powershell
$env:BINTANONG_RESEARCH_CONFIG = "<path>\hosted-research-api-config.json"   # same file the hosted API starter uses
$env:BINTANONG_LEDGER_CACHE    = "<ignored dir>\ledgers"                     # filled once, read-only
$env:SUPABASE_URL      = "..."   # only needed the first time, to fill the ledger cache (anon key, read-only)
$env:SUPABASE_ANON_KEY = "..."
$env:MODELS_DIR        = "C:/Coding-projects/bintanong_workspace/MODELS"
```

Start the Gemma server named by the config's `model_url` (for example
`docker start bintanong-p09-cuda-latency`, then check `/health`). Results go to `--out`; use an ignored folder under
`audit-evidence`, never a tracked path.

## Gates

| Command | What it checks | Time |
| --- | --- | --- |
| `python -m evaluation.memory_eligibility.gates offline --out <dir>` | The plan's 14 source-backed cases, through Prolog only (no model) | < 1 min |
| `python -m evaluation.memory_eligibility.gates scenarios --out <dir>` | The plan's demos: BSCS two-turn plus memory, fresh chat, proposed BSCS, Lawrence what-if, Civil vs Mechanical Phy 11/L, term follow-up, BusEco | ~12 turns |
| `python -m evaluation.memory_eligibility.gates curricula --out <dir>` | Every release member: ask, then a bare "yes" gives eligible; a fresh-chat "not yet passed" gives unmet. Languages rotate (en/fil/taglish) | 39 × 3 turns |
| `python -m evaluation.memory_eligibility.gates recorded --out <dir>` | The 113 recorded prerequisite questions in `Context/sample-query-results-20261103.md`, single-turn | 113 turns |

Pass scenario names or curriculum ids after the gate to run a subset, for example `curricula bsce-2018-2019`.
On a 4 GB laptop GPU a turn took 20–35 s. `curricula` and `recorded` each run about an hour there. They write a
`*-partial` JSON after each curriculum or question, so an interrupted run keeps its results.

## Reading the results

`python -m evaluation.memory_eligibility.dependency_offline --out <ignored-dir>/dependencies.json`
checks every curriculum in the existing ledger cache without model calls or database access. It selects
a course referenced by other courses and a terminal course where available; replays four dependency
phrasings with code/compact-code/unique-title aliases against two incorrect model operation types;
then compares actual Prolog dependencies with the reviewed ledger graph and checks neutral English/Taglish prose.
It writes per-curriculum counts and failures after each curriculum. This is compiler/rule verification,
not an end-to-end model benchmark or an independent review of original prospectuses. Live language
accuracy, history/thread behavior, browser rendering and unsupported curricula need separate evidence.

Each row records `ok`, `status`, `outcome` and `seconds`. It also records `explanation_check` (accepted, rejected,
unavailable or skipped), the validator's `explanation_errors` codes and what the chat `remembered`.

Expectations come from the plan and the reviewed ledgers, not from an independent reading of each prospectus.

Report the results per curriculum with the numerator and denominator. A curriculum that was skipped or limited
cannot count as passing.

Timings are warm backend turn times only. They exclude the browser, network, queueing and Supabase.
