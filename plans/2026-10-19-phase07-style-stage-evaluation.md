# Phase07 independent response-style evaluation

Product ac00ac9 separates evidence routing and response-style interpretation into
two structured calls to the same supplied Gemma/Bintu model. No classifier,
language dictionary, final answer generator or institutional executor is added.
The routing prompt/messages/schema remain exactly those verified at d019318.
The retained candidate gets15/15routes/meaning and13/15styles. Phase07 remains
open for two Taglish failures; selected fresh two-stage checks are in progress.

## Change and evidence trail

The [earlier followup](2026-10-19-phase07-interpretation-followup.md) reports
15/15routes/meaning but10/15style labels; all five Taglish labels were fil.
The [style design](2026-10-19-phase07-response-style-design.md) records rejected
combined-call prototypes:style improved, but route/operation semantics regressed.
Do not adopt those prototypes or the unsuccessful native-thinking configuration.

Style contracts3ec6238 and independent-stage integration ac00ac9 preserve routing
input, expose immutable literal style evidence and share one format-repair budget.
Normal requests use two model calls; at most three after one repair. Grounding
failures do not get semantic retries. Style output cannot supply audience, facts,
routes, operations or policy. Accepted style metadata is distinct from the raw
routing proposal's language. Unknown style clarifies in-scope queries; explicit
excluded scope retains precedence. All source/registry/activation holds remain.

Initial independent-stage full evaluation:15/15proposed/effective routes, entities,
claims and operations; five consistent families;13/15styles. The two errors quote
whole mixed utterances as Filipino with no English evidence. A focused instruction
change still gets3/5styles on the same two failures/three controls; it is retired.
Label-first prompt/schema614e3c3 then gets5/5routes/meaning/styles on those fixed
five cases, but its full15-case evaluation regresses four pure-English/Filipino
course queries to taglish:11/15styles overall. It labels English fragments as
Filipino and vice versa while still satisfying literal containment. Both label-first
prompt/schema614e3c3 and instruction-v2 are retired. Restore exact ac00ac9 product
bytes/style-v1, the stronger13/15candidate. No gold/wording changed.

Literal containment establishes provenance, not a fragment's language. For example,
a model may still put a mixed sentence in the Filipino array while correctly
quoting an English fragment separately. The host never relabels fragment language.

## Fixed evaluation and reuse protocol

Reuse the existing five generic synthetic families, each with English, Filipino
and Taglish variants:procedure, prerequisite, affected-course-plus-procedure,
greeting and excluded graduate procedure. A1/B1 and program/curriculum identities
are fictional. These15cases are separate from the75accepted institutional cases
and sealed final benchmark. No expected labels/family IDs enter model messages.
Nine variants need RAG/Symbolic/Hybrid; six have substantive operation/claim
expectations and nine have empty expected collections. Empty matches do not prove
substantive extraction. No retrieval or Prolog is executed by the evaluation.

Raw root:workspace/audit-evidence/p07-implementation-20261019/.

- interpretation-v6-full/:original actual routing captures from d019318.
- style-stages-full/:15exact routing captures reused,15fresh style-v1 calls;
  scores15/15route/meaning,13/15style,30logical calls,zero repairs.
- style-stages-v2-bounded/:same fixed five cases,5/5route/meaning,3/5style;
  failed instruction variant retained with exact product.patch over ac00ac9.
- style-stages-label-first/:same five cases,5/5all dimensions;5routing captures
  reused/5fresh style calls. Exact product.patch over ac00ac9 matches614e3c3.
- style-stages-final-full/:retired label-first15-case composition. Reuses15routing
  captures/five exactly matching label-first style captures;10fresh style calls.
  Proposed/effective routes/entities/claims/operations15/15; five consistent
  families;styles11/15 (English3/5,Filipino3/5,Taglish5/5). Zero repairs.

Capture reuse asserts exact message arrays and schema objects, temperature0/seed0,
output768/schema decoding and model/build/context/template identity. Reused files
record source path and byte SHA256. Full reports identify fresh versus logical
calls. Composition durations include replay and are not live inference latency.
Every source inference remains an actual model output; nothing is a mock or gold
replacement. Do not report this as15fresh complete two-stage requests.

Commands use existing Python3.13 readiness venv, -B and ignored raw script:
run-style-stages.py --label style-stages-final-full
--reuse-style style-stages-label-first.
The script and report remain ignored; hashes are sealed in the final manifest.

## Versions and pinned identities

Python3.13.7/Pydantic2.13.5/HTTPX0.28.1/pytest9.1.1; inherited Janus1.5.2/SWI10.1.15.
No package/lock changes. Existing model is mounted read-only at owner-corrected
C:/Coding-projects/bintanong_workspace/MODELS/GEMMA_4_E4B/
gemma-4-E4B-it-UD-Q4_K_XL.gguf,5,126,306,944bytes. Gemma supplies the Bintu role;
no separate fine-tuned Bintu-1 identity is established.

Model SHA256:3cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80.
Official image:sha256:4b7be0376002b4450a357a109bab804093ff9251193cc75ed4ce0cb39953ff5c.
llama.cpp:b11718-547208dca. Template SHA256:
74a88f94c57c14e22dcdbe08e94127f42b87c6f584cb73838e73e32126f3f6b3.
CPU8threads/context8192/one slot/output768/temperature0/seed0/constrained JSON;
reasoning_effort=none consistently in template preflight and generation.
Timeout240s per call. Tokenizer/template endpoints validate the full message budget
with768output+8reserved; no SEA-LION tokenizer substitutes for model input limits.

Routing prompt:version p07-v6, SHA256
e84c54ce7dce6f4cba0e39c02d7388a06caf3048714aa86f49c08cce95abe65f.
Routing schema SHA256:92e0be47d46963fc9042f1c9018c8deb1d70a3be64a1bcf1cdf43d8d0dd97c14.
Retired label-first style prompt:bintanong-response-style-p07-v3, SHA256
ded4789b15c0e05ab2c2b56620ec8fb7b3dfc409257422b177c21f7e4d698537.
Retired label-first style schema:bintanong-response-style-v1, SHA256
ef880cc53530bd0b0c7820e325f2d818fa99f8221b41993b6a599e89b0b248b2.
Case-set SHA256:f0f85d8308d341970b6e6d051dcb735d10e1042b8e3cea84df538f4689aa236e.
Catalog SHA256:2207f062dce8dc42483dfd0993e7e1f5d08330294673c37f293e1a2a8180ce0a.

## Software verification

Stage integration RED35failed/18passed ->GREEN127routing tests1.34s.
Independent review of ac00ac9 integration:no P1/P2;127passed1.30s.
Broad24-file gate:1555passed/11subtests179.81s,exit0; exact command in ignored
verify-style-stages.ps1/style-stages-regressions.log. Label-first focused gate:
127passed3.38s,exit0;label-first-unit.log. Retired label-first broad gate:
1555passed/11subtests141.12s,exit0;final-style-regressions.log.
Restored code is byte-identical to ac00ac9 backend/tests, verified by Git diff.
Fresh restored routing/docs/phase-state gate:696passed/11subtests12.37s,exit0;
restored-style-docs.log. It runs six routing suites, tests/test_docs_hygiene.py
and the handoff skill's tests/test_phase_state.py with -B -p no:cacheprovider
and external --basetemp=raw-root/restored-style-docs in the existing readiness venv.

Coverage includes false/missing/repeated quotes, conflicting assertions, unknown
scope/curriculum, hypothetical/reported facts, unsupported signatures, compounds,
absent components, malformed/duplicate JSON, token overflow, timeouts and shared
repair exhaustion. Invalid outputs do not yield an unchecked PredicateRequest;
no executor exists here. EMPTY_REGISTRY/institutional execution guards stay closed.
Two inherited Docling failures remain disclosed by Phase06; no whole-project-green
claim. No dependencies, weights, private artifacts or institutional sources changed.

## Retained candidate results and unresolved question

Retained style-v1 full report:style-stages-full/report.json (ac00ac9). Its route
and effective-route confusion matrices both have only diagonal entries:

| Expected | RAG | Symbolic | Hybrid | greeting | unsupported_scope |
| --- | ---: | ---: | ---: | ---: | ---: |
| RAG | 3 | 0 | 0 | 0 | 0 |
| Symbolic | 0 | 3 | 0 | 0 | 0 |
| Hybrid | 0 | 0 | 3 | 0 | 0 |
| greeting | 0 | 0 | 0 | 3 | 0 |
| unsupported_scope | 0 | 0 | 0 | 0 | 3 |

| Language | Routes/effective | Entity/claim/operation collections | Style |
| --- | --- | --- | --- |
| English | 5/5 | 5/5 each | 5/5 |
| Filipino | 5/5 | 5/5 each | 5/5 |
| Taglish | 5/5 | 5/5 each | 3/5 |

Five equivalent families preserve route and entity/claim/operation meaning.
18literal offset corrections across nine cases; zero format repairs.
Style errors:procedure-taglish and excluded-taglish both select fil. All15actual
routing captures are reused exactly;15fresh style calls/30logical total. This is
an improvement over10/15style at d019318, but does not fulfill the owner's language
preference for those two queries. Do not call it solved or activate student output.

Only Gemma and SEA-LION embedding folders exist in the owner-supplied model root;
no distinct Bintu LLM checkpoint is available there. Further unchanged prompt
trials or a host keyword override are not a justified next action. Preserve this
bounded result for an explicit model/design decision; no download is authorized.
Selected fresh two-stage verification remains pending. Phase07 has no final
handoff and Phase08 cannot begin under the current language-style exit decision.
