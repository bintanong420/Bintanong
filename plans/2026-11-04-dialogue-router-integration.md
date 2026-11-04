# Dialogue router integration — 4 November 2026

Owner directed implementation of the next stabilization priority: connect the
committed ephemeral ledger, then verify clarification recovery and topic switching,
including shifting-office referrals. Existing audit slices 2–4 govern; no numbered
phase, dependency/model change, durable storage or institutional activation.

Consulted current Git/index/progress, stabilization plan/checkpoint, owner ledger,
master routing architecture, thesis physical 17–18 and 39–44, and runtime routing
PNG on this resume. Undergraduate advisory and source/privacy boundaries remain.

Implementation: one server-owned compiler projects up to four same-scope exchanges
under 16 KiB of dialogue text, including the unresolved origin when retained.
The routing payload marks old user/assistant text as untrusted interpretive context.
Typed semantic acts select an actual owned turn and reviewed course candidate;
the saved operation is checked again. A self-contained topic switch drops course
focus while retaining separately scoped facts. No exact repair-phrase detector,
new feature-specific pending type, assistant-derived grades or old-answer evidence.
The existing router call interprets the act; there is no separate dialogue classifier.
Partially assigned documentary requests may use the existing bounded repair attempt.

Chat now passes the actual utterance to routing rather than the pending-check
question rewrite. Existing short-reply fact grounding remains scoped and separate.
Default/separate and combined routing paths support owned dialogue references.

TDD: missing ledger projection, absent prompt history, semantic repair returning
generic clarification, and hidden short-reply reconstruction each reproduced RED.
Focused component gate: **186 passed in 6.99s**, covering projection, raw chat turns,
router/wire/combined contracts, semantic recovery, forged references, old assistant
injection and new shifting-topic routing. This is protocol/host evidence, not model
accuracy or a whole conversation acceptance result.

Live first run: initial BSIT eligibility asks correctly, but follow-up/why/repair
returned insufficient evidence within about one second despite the result being
remembered. Same under compiler OFF/ON. Exact routing trace is being collected;
the student capability is still open. Ignored evidence:
`audit-evidence/stabilization-20261104/dialogue-{live,trace}.{json,log}`.

The failures below were diagnosed and corrected; this first-run evidence is retained
for comparison rather than presented as current behavior.

## Follow-up corrections

Live trace identified three distinct failures, each covered RED/GREEN:

- Topic selection was 7,679 input tokens plus its 768-token output reservation in
  an 8,192-token window. Selector context now contains only relevant document
  questions, not course-only history, assistant responses or fact/session metadata.
  Main routing retains the bounded dialogue. Overflow is a system failure, never
  a source-absence response. No model context or output budget was reduced.
- The model selected the correct owned request but quoted its old target from
  outside the current utterance. The host now binds the typed goal to current
  reference words while grounding the grade entity separately. The optional
  structural compiler does not reinterpret an already validated owned reference.
- An explanation incorrectly checked the prerequisite itself. Explain/repair/
  correction retain the saved goal; only refinement changes the target.

Semantic acts are required and decoded before request shape when history exists;
fresh-turn schema remains compatible. Document references retain original claim
IDs, revalidate current-menu availability and retrieve anew. Effective selected
context reaches orchestration so companion procedure evidence is not lost.
Unresolved origin exchanges stay pinned under the existing bounded retention.

Live BSIT, compiler OFF/ON: initial unknown, supplied pass -> eligible, Why -> same
eligible goal, redundant-clarification repair -> same eligible goal: **8/8**.
Observed backend times 9.6–26.1s with concurrent probes; not browser latency or an
SLA/speed comparison. Ignored evidence `dialogue-goal-final.{json,log}`.

Broader routing/private-context/orchestration/API gate: **1,133 passed / 2 xfailed**
(27.52s). Fresh-schema regressions corrected; two version assertions updated and
the old normative empty-clarification -> source-absence expectation retired.
Source-backed fresh shifting answers name OSAS, College Guidance Practitioner,
Dean/Department Head and Registrar from reviewed Handbook physical 45/58. The
after-course run exposed a second document part left without a topic. A bounded
semantic retry now re-evaluates unassigned document parts, without copying a
source assignment or claiming coverage. Retry positive/negative gate **151 passed**;
the subsequent source-backed results are recorded below. No source content/approval changed.

System Python's existing Transformers/Hub versions prevented encoder loading.
The existing Python 3.13 audit venv loads the pinned local CPU encoder; no install,
dependency upgrade, model download or duplicated weight directory was performed.


## Final delivery and handoff

Commits: `ae26589d` owned dialogue integration; `4c10094c` goal/document-context
corrections; `86f869d8` bounded topic repair. The last live failure showed the repair
changing a valid new-topic act or documentary path into an unrelated clarification.
Repair now retains validated acts and quoted part inventory; only unresolved topic
assignments are reconsidered. An unknown sibling may be classified on retry.
Absent/unsupported coverage still fails closed; no office/topic is copied by host.
Synthetic positive, unavailable, act-drift and evidence-path regressions are green.
Topic relevance is explicitly separated from downstream source/answer coverage.

Final integrated gate, system Python 3.13:

```powershell
$dialogueTestFiles = @(rg --files tests -g 'test_routing*.py' -g 'test_private_context*.py' -g 'test_orchestration*.py')
py -3.13 -B -m pytest @dialogueTestFiles tests/test_api_chat_turns.py tests/test_dialogue_context.py tests/test_dialogue_ledger.py -q -p no:cacheprovider --basetemp C:/Coding-projects/bintanong_workspace/audit-evidence/dialogue-final-current-20261104
```

**1,139 passed / 2 xfailed in 47.28s**; `git diff --check` clean. Latest focused
repair gate **155 passed in 3.60s**. Logs: `dialogue-final-current.log` and the
live JSON/log files below, under ignored workspace `audit-evidence/stabilization-20261104/`.

Actual-model/reviewed-source shifting evidence across successive corrections:

- `dialogue-shifting-venv`: fresh question answered in BSCS and BSIT, compiler OFF/ON (4/4).
- `dialogue-shifting-after`: after-course switch answered in BSIT OFF/ON and BSCS ON (3/4);
  BSCS OFF failed and motivated the final repair-preservation change.
- `dialogue-shifting-verified`: that BSCS OFF case now routes RAG and answers (1/1, 25.3s).
  This is a targeted rerun, not one clean eight-case run on the final commit.
- All eight successful scenario rows contain OSAS, Registrar and Dean; actual source
  retrieval/coverage checks also retain College Guidance Practitioner and conditional
  Department Head/current/receiving Dean roles. No course-result fact was added by
  the shifting reply. Handbook physical 45/58: shifting compact clause plus FAQ 8,
  pinned source version `4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8`.

The four-turn BSIT recovery sequence remains 8/8 across OFF/ON: unknown target,
supplied prerequisite pass, explanation, repair. Synthetic tests cover scope,
ownership, ambiguity, old-text injection, compiler paths and unavailable sources.
This demonstrates these scenarios, not all programs or general conversational accuracy.
CPU encoder cold load is separate (last 32.87s); warm observations use local cached
reviewed source/embedding records, Prolog and actual model, excluding HTTP/browser
and hosted database latency. No latency improvement or achieved SLA is claimed.

Not done: browser/frontend thread parity; durable history/privacy design; wider
held-out English/Taglish conversations and remaining audit/planner acceptance.
No serving API/model restart, push, deployment, source edit or dependency/model
change. Serving API identity was not verified against these commits. The system
Python encoder incompatibility remains; the existing compatible audit venv was used.
Next: validate frontend-to-backend dialogue parity with these exact sequences,
then expand held-out conversations without reopening reviewed source decisions.
