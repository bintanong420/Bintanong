# Bounded correction after the frozen router gate

Owner approved20October2026 ("ye i approve");Phase09. Extends the approved
[prompt/validation direction](2026-10-19-prompt-engineering-and-validation-decision.md)
and [router design](2026-10-20-router-question-understanding-recovery-design.md).
No product changes or model inference in this investigation. One focused builder
check returned "nothing important left";no repeat review. The conditional-answer
boundary is a separate pending owner question. Execute the
[implementation plan](2026-10-20-router-quoted-reference-implementation-plan.md).

## Capability and evidence

Student capability:identify the requested course and every requested document
detail,retain supplied student conditions,and explain the applicable scoped Prolog
result in the requested language. Phase09 requires correct evidence-backed answers;
a structurally valid decision for another course fails that requirement.
Evidence path:LLM interpretation -> grounded host plan -> reviewed structured facts/
actual Janus and RAG documents -> canonical decision plus supported explanation.
Unresolved question:can a simpler interpreter interface preserve meaning while
removing unnecessary position/index work,without removing evidence or reasoning?

The [sealed8case observation](2026-10-20-router-understanding-observation-results.md)
remains3/8 against its fixed response references. Do not rewrite its labels/results
or represent these known failure families as independent final evaluation.
All55sealed observation files and product hashes verified unchanged. New raw:
workspace/audit-evidence/p09-router-correction-design-20261020/;zero inference.

## Diagnosis from existing evidence and pinned sources

- Wrong target:s-tl names ZX201 as the requested course but emits operation target1,
  which refers to ZX101. Host executes that supplied target correctly. Its part
  quotes both courses,so containment and performed-operation checks cannot detect
  the semantic error. Ledger/Prolog consistency is necessary but not an intent oracle.
- Missing condition:s-fil/h-en emit no failed-course claim. Host correctly preserves
  unknown;it must not infer failure from an absent fact. s-en emits failed as reported;
  its English conditional wording is not proof of an actual student record.
- All3document replies are complete,but the interpreter merges separately requested
  details into one part. Whole-question quoting weakens the intended coverage ledger.
- Raw offsets need host repair in7usable plans. Saved model output shows attempted
  position calculation;the host already has a deterministic unique-quote anchor.
  Removing model offset arithmetic is a hypothesis for reducing work/errors,not a
  measured speed or semantic-accuracy improvement.
- All8saved rendered interpreter prompts lack the Gemma thinking trigger,while7
  actual responses contain reasoning. The exact server build is b11723 at
  31288c9c66e59377f7788d920678a565bb89dd37. Its
  [request parser](https://github.com/ggml-org/llama.cpp/blob/31288c9c66e59377f7788d920678a565bb89dd37/tools/server/server-common.cpp#L1421)
  already sets thinking false for reasoning_effort=none. Its
  [Gemma parser](https://github.com/ggml-org/llama.cpp/blob/31288c9c66e59377f7788d920678a565bb89dd37/common/parsers/gemma4.cpp#L196)
  still permits an optional thought block before schema-constrained JSON without
  conditioning that grammar branch on enable_thinking. This explains permission,
  not why this quantized model chooses that branch or its total latency effect.
- Current [server documentation](https://github.com/ggml-org/llama.cpp/blob/31288c9c66e59377f7788d920678a565bb89dd37/tools/server/README.md)
  distinguishes thinking settings from reasoning-output parsing. Setting
  reasoning_format=none would hide/relocate thoughts,not prove generation stopped.
  A zero reasoning budget forces a thinking boundary;its quality effect here is
  untested. Do not select it merely to reduce time. Google's
  [format guide](https://ai.google.dev/gemma/docs/core/prompt-formatting-gemma4)
  describes trigger removal and notes unexpected thought channels for larger
  variants;that note is not proof about this E4B artifact.

Context7 resolved /ggml-org/llama.cpp and queried thinking controls and request
budgets separately. Source inspection above pins the actual running build rather
than assuming current master equals the installed runtime. No service/model changes.

## Options and selected bounded change

1. Add more prompt instructions to the present offset/index schema. Smallest code
   change,but retains positional arithmetic and fragile numeric course references.
2. **Selected design:quoted references at the model boundary,host normalization.**
   Keep semantic interpretation in the existing LLM call;make host work explicit.
3. Force zero reasoning budget or increase output/context limits. Does not correct
   course/fact meaning;changes another variable and risks quality or longer waits.
   Neither is selected. Keep existing reasoning,model,seed,cache and deadlines.

Add one strict interpreter wire contract,version bintanong-interpretation-wire-v1.
Each quote is {text,occurrence};occurrence is zero-based among exact,case-sensitive
matches in the ORIGINAL question. Each mention has kind and that quoted reference.
Each claim has statement quote,entity quoted reference,state and original mode.
Each operation has name and target quoted reference,instead of a mention-array index.
Each part has part_id,quote,evidence_need and existing operation_indices. Preserve
the current1-8part/0-4operation/32mention-and-claim limits and route/control fields.
Model outputs contain no character offsets or source/session IDs. No free Prolog.

One normalizer validates quote occurrences,computes exact Python spans and resolves
operation targets/claim entities to an existing mention with the IDENTICAL quoted
reference and course kind. Missing/out-of-range occurrences,duplicate mention
references,non-course targets,invented text and mismatched claim/part containment
reject;no fuzzy match,new mention insertion or silent first-occurrence choice.
Normalize to the existing Interpretation v2,then use existing alias/scope/claim-mode/
capability/operation and downstream binding validation. The quoted target can still
be semantically wrong;do not claim this representation change eliminates that risk.

Router separate remains selected. Its existing one shared format repair and total
deadline remain. Migrate the explicit combined experiment's nested interpreter wire
contract and version as needed;normalize through the SAME function. Do not select or
benchmark combined routing. Keep normalized Integration/CandidateAnswer contracts
unchanged for this independent representation change;no second interpretation call.

Revise only the interpreter's versioned task guidance for exact target identity,
complete stated conditions and separate independently answerable details. Retain
scope/privacy/source-gap/unknown rules. Distinguish asserted,hypothetical and reported
claims;never force every conditional into asserted. At most one short fictional
worked contrast using other course identities,kept outside evaluation references;
mark the failure families known. No growing example bank or keyword router.
Keep the separate style call;its Taglish error stays a separately reported limit.

## Conditional-answer decision

Owner question pending:answer an explicitly conditional eligibility question under
its stated assumptions,or ask for confirmation of actual failure? The frozen8case
reference fixes failure as a scenario condition,but the runtime currently rejects
all nonasserted claims. Do not weaken that guard or silently relabel hypothetical/
reported information as actual. The quote interface can be built independently;
conditional execution and any answer-schema change need their own explicit design
after the answer. No conditional execution is included in the selected wire change.

## Verification and stopping boundary

Focused TDD must cover wrong index/reference conversion,reordered mentions,repeated
literal occurrences,invented/out-of-range quotes,claim containment and unchanged
mode rejection,plus separate/shared repair and combined compatibility. Use short
synthetic parser examples;do not add redundant parameter combinations or institutional
benchmark wordings. Migrate runtime model mocks centrally where appropriate;keep
normalized-contract tests testing the existing v2 contracts.

Before any inference,freeze final code/prompt/schema and exact input/bundle/release
hashes,server/template/settings,expected outcomes and call/time limits. Separate
software schema success,semantic extraction,course target,fact fidelity,document
coverage/support and requested language. Wrong-course answers block promotion;
safe unknown/clarification is distinct from a complete capability answer.
The conditional decision must be resolved before binding expectations for that
family;do not change labels after seeing outputs. Reused developer questions remain
known cases;accepted75institutional variants and school/source holds unchanged.

No inference in this design task,no rescue probe or repetition of the sealed run.
After a bounded implementation/software gate,define ONE separately sealed candidate
observation and stop on failure;no prompt/model/seed/budget sweep. If meaning still
fails,discuss capability/model limits rather than adding another guard/classifier.
Actual latency must retain the [measurement boundary](2026-10-20-response-time-measurement-contract.md)
and [saved target](../Context/response-time-recommendation.md). Keep required RAG/
Prolog/evidence/validation and reject quality regressions. No accuracy-for-speed trade,
Phase09 completion,Phase10,dependencies,training,DB writes or activation.
