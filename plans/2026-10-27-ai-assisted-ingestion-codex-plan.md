# Bintanong Phase 11 — AI-Assisted Ingestion Extension

**Date:** 2026-10-27  
**Target branch:** `feat/p11-policy-ingestion-review`  
**Implementation mode:** autonomous sequential execution with tests and small commits  
**Scope:** Lawrence's follow-up for AI-assisted Handbook and Citizens' Charter ingestion

---

# 1. Objective

Extend the **existing Phase 11 policy-ingestion workflow** with two experimental AI-assisted ingestion strategies:

## Strategy A — Native extraction + multimodal verification

```text
Existing deterministic/script extraction
        ↓
Existing candidate representation
        ↓
Original PDF page / source region
        ↓
Configurable multimodal LLM verification
        ↓
Advisory proposal
        ↓
Existing ReviewSession / researcher UI
        ↓
Human Accept / Correct / Hold
        ↓
Existing build + verify pipeline
```

## Strategy B — LlamaParse-assisted extraction

```text
Original PDF / selected page ranges
        ↓
LlamaParse
        ↓
Normalize into existing candidate/review representation
        ↓
Existing ReviewSession / researcher UI
        ↓
Human Accept / Correct / Hold
        ↓
Existing build + verify pipeline
```

Then evaluate both strategies against representative PalSU Handbook and Citizens' Charter pages.

The system must preserve this invariant:

> **Parsers produce candidates. AI produces advisory proposals. Humans produce review decisions. Only reviewed human decisions may become authoritative downstream knowledge.**

---

# 2. Existing implementation is authoritative

This is **not a greenfield ingestion system**.

Before changing code, inspect and reuse the existing implementation.

Read:

- `AGENTS.md`
- `plans/2026-10-26-policy-ingestion-workstream.md`
- `plans/2026-10-26-policy-ingestion-developer-workflow.md`
- `plans/2026-10-26-policy-ingestion-developer-plan.md`
- `plans/2026-10-26-policy-ingestion-checkpoint.md`
- `plans/2026-10-26-ingestion-pipeline-assessment.md`
- relevant Phase 2 prospectus ingestion plans
- any additional Lawrence-authored `.txt` or `.md` plans present in the worktree

Inspect at minimum:

- `backend/bintanong_tools/knowledge_update/`
- `backend/bintanong_tools/document_ingest/`
- `backend/bintanong_tools/prospectus_review_gui/`
- `backend/bintanong_contracts/source.py`
- existing backend tests
- existing reviewer frontend
- existing model/generation/provider abstractions elsewhere in Bintanong
- repository dependency manifests and lockfiles
- existing PDF/page rendering implementation

The current checkpoint indicates:

- T1 source-bound preparation exists.
- T2 persisted review/API/researcher UI exists.
- T3 reviewed package build/verification exists.
- T4 local lifecycle work remains separate.
- T5 operator delivery/rehearsal remains separate.

Do not rebuild T1–T3.

Do not claim T4/T5 complete as a side effect of this work.

---

# 3. What already exists and should be reused

The current implementation already provides the important foundation.

Reuse:

- deterministic/script-driven document extraction;
- review packet preparation;
- source-document provenance;
- candidate hashes;
- packet hashes;
- original PDF evidence;
- physical-page information;
- existing PDF/page renderer;
- source-region information where available;
- `ReviewSession`;
- append-only review decisions;
- `accepted`;
- `corrected`;
- `unresolved`;
- `pending`;
- researcher review UI;
- review export;
- reviewed package construction;
- package verification;
- embedding reuse/build behavior;
- prospectus ingestion compatibility;
- current omission/gap reporting;
- existing `review_template` proposal mechanism;
- existing `proposed_value` semantics.

In particular, determine whether the existing conceptual flow:

```text
original_value
proposed_value
reviewed_value
decision = pending
```

can directly represent AI-generated suggestions.

**Prefer extending this mechanism over introducing another persistence model.**

---

# 4. Explicit non-goals

Do NOT build any of the following unless the existing code demonstrably cannot satisfy Lawrence's requirement:

- second reviewer application;
- second review journal;
- AI-specific database;
- autonomous approval workflow;
- direct AI writes to reviewed chunks;
- direct AI writes to authoritative policy data;
- PDF → LLM → trusted Prolog;
- separate build pipeline for LlamaParse;
- separate package format for AI output;
- student-facing AI ingestion features;
- hosted Supabase workflow;
- hosted release publication;
- automated institutional approval;
- model training or fine-tuning;
- generic document-ingestion platform;
- generalized agent framework.

The goal is to add **two interchangeable upstream assistance strategies to the existing human-review boundary.**

---

# 5. Authority model

Never collapse these states:

```text
Source evidence
    ↓
Extracted candidate
    ↓
AI advisory proposal
    ↓
Human review decision
    ↓
Reviewed knowledge
    ↓
Derived RAG / symbolic artifacts
```

An AI response must never itself set:

- `accepted`
- `corrected`
- `approved`
- `verified`
- `authorized`
- `reviewed`
- release eligibility
- publication eligibility

AI-generated output remains advisory until an explicit human action records the decision using the existing review machinery.

Existing safeguards rejecting privileged metadata must remain intact.

---

# 6. Execution policy for Codex

Execute the tasks in this plan sequentially.

Do **not** stop between normal tasks to request permission.

For each task:

1. inspect the existing implementation;
2. write or extend tests first;
3. demonstrate the intended test failure;
4. implement the smallest correct change;
5. run focused tests;
6. run relevant regression tests;
7. refactor only if justified;
8. commit the completed task;
9. continue to the next task.

Preserve unrelated user changes.

Do not use destructive Git operations.

Do not force-push.

Do not rewrite existing history.

Do not silently modify shared contracts simply because doing so is convenient.

If an assumption in this plan is wrong, prefer the architecture already present in the repository.

---

# 7. STOP conditions

Codex should continue autonomously unless one of these materially blocks safe implementation:

1. the checked-out branch is materially different from the Phase 11 checkpoint;
2. uncommitted user changes overlap the exact files that must be rewritten and cannot safely be preserved;
3. the existing `proposed_value` mechanism fundamentally cannot represent advisory AI suggestions;
4. supporting AI proposals requires changing a shared source/chunk contract used broadly outside Phase 11;
5. preserving Citizens' Charter table relationships requires a major canonical schema change rather than a local ingestion representation;
6. the existing PDF renderer cannot provide page/image evidence and replacing it would require a substantial ingestion rewrite;
7. the current LlamaParse API materially differs from the assumptions discoverable from its official documentation;
8. a necessary dependency introduces a broad runtime or packaging conflict;
9. existing baseline tests reveal an unrelated failure requiring a broad refactor;
10. implementation would require AI output to become authoritative.

When one occurs, stop before making the broad change and report:

- observed repository state;
- why the current mechanism is insufficient;
- smallest safe change;
- affected consumers;
- compatibility risks;
- required tests;
- recommended next action.

Routine implementation choices are **not** stop conditions.

---

# 8. Task 0 — Reconcile the current branch with this plan

## Goal

Establish the exact implementation surface before writing production code.

## Inspect

Confirm:

- current branch;
- current HEAD;
- working tree status;
- current Phase 11 CLI;
- `prepare.py`;
- `review.py`;
- `templates.py`;
- reviewer API;
- reviewer frontend;
- build/verify path;
- page rendering;
- current proposal/import behavior;
- current source/candidate hashing;
- model-provider code elsewhere in Bintanong;
- dependency management;
- test conventions.

## Answer internally

Before implementation, determine:

### A. Where should an AI proposal enter?

Preferred:

```text
AI
 ↓
existing review-template proposed_value
 ↓
normal pending review
```

### B. When can the proposal safely be created?

Because packets are hash-bound, determine whether proposal generation should happen:

**Option 1 — preferred if compatible**

```text
prepare candidate
→ run assist
→ add proposal to review template
→ finalize/hash packet
```

or:

**Option 2 — only if necessary**

Create a separate immutable advisory artifact bound to:

- packet ID;
- source document/version;
- source SHA;
- candidate hash;
- review item;
- field.

The advisory artifact must not mutate an already-finalized packet.

Do not casually rewrite `packet.json` after preparation.

### C. Can an existing provider abstraction be reused?

Search the repository before introducing a new one.

If a suitable model/provider interface already exists, reuse it.

Otherwise create only a minimal ingestion-assistance protocol.

## Output

Update or create a short implementation note recording:

- selected integration point;
- files to change;
- tests to extend;
- proposal lifecycle;
- provider abstraction decision;
- renderer reuse decision;
- LlamaParse integration boundary.

Then continue automatically.

## Suggested commit

`docs(p11): pin ai-assisted ingestion integration points`

---

# 9. Task 1 — Lock down the AI proposal contract

## Goal

Prove with tests that AI output cannot become a review decision.

## Tests first

Add tests using the repository's existing test layout.

Cover at minimum:

### Proposal does not equal decision

Given:

```text
original_value = "5 working days"
proposed_value = "15 working days"
```

loading the proposal must still result in:

```text
decision = pending
reviewed_value = original/default review value
```

until the human explicitly chooses otherwise.

### Human acceptance remains human-controlled

AI suggestion presence must not cause:

```text
accepted
corrected
reviewed
verified
approved
```

automatically.

### Human correction works

If the reviewer uses the suggestion and saves it as a correction:

```text
decision = corrected
reviewed_value = "15 working days"
```

must be produced through the existing review journal.

### Stale proposal

If the underlying candidate hash changes, an old proposal must not silently apply.

### Wrong source

A proposal bound to another source SHA/page/item must not apply.

### Malformed proposal

Malformed model output must fail closed to manual review.

### Privileged metadata

Provider output attempting to inject privileged approval fields must be ignored/rejected according to existing contracts.

## Implementation rule

Reuse the existing proposal mechanism if it passes these requirements.

Only introduce a new advisory representation if absolutely necessary.

If additional metadata is necessary, keep it minimal:

```text
provider
model
model_version if available
created_at
source_sha256
candidate_hash
item_id
field
proposed_value
rationale
confidence optional
```

Do not add review status to AI metadata.

## Suggested commit

`test(p11): pin human authority over ai proposals`

followed by, if implementation is needed:

`feat(p11): support source-bound advisory proposals`

---

# 10. Task 2 — Add the minimal assistance provider interface

## Goal

Allow Phase 11 to call a configurable AI verifier without coupling the ingestion pipeline to one vendor.

## First inspect

Search for an existing Bintanong:

- generation client;
- LLM provider;
- OpenAI-compatible provider;
- Ollama client;
- model configuration;
- structured-output helper.

Reuse an appropriate abstraction if one exists.

Do not create another provider framework merely because this feature needs one method.

## If no reusable abstraction exists

Create a minimal interface conceptually equivalent to:

```python
class AssistProvider(Protocol):
    def inspect(self, request: AssistRequest) -> AssistResult:
        ...
```

The exact naming should follow repository conventions.

### AssistRequest should contain only what is required

For example:

```text
document identity
source hash
physical page
source region if available
candidate field/value
page image or crop
optional neighboring context
expected document structure
```

### AssistResult

Support outcomes conceptually equivalent to:

```text
no_change
proposal
uncertain
failed
```

A proposal may include:

```text
proposed_value
rationale
confidence
issue type
```

It must not include an authoritative review decision.

## Deterministic fake provider

Implement a fake/test provider before any live provider.

Use it to test the entire proposal path without:

- API keys;
- network access;
- paid inference;
- nondeterministic model output.

## Error behavior

Provider failures must produce:

```text
AI assistance unavailable
→ leave review pending/manual
```

not:

```text
AI assistance unavailable
→ assume candidate is correct
```

## Suggested commit

`feat(p11): add advisory ingestion provider boundary`

---

# 11. Task 3 — Implement Strategy A: native extraction + multimodal verification

## Goal

Implement Lawrence's first requested strategy:

> existing scripts produce the extraction, AI examines the original page/image for further verification, then a human verifies/corrects it.

## Pipeline

Use:

```text
existing document ingestion
        ↓
existing candidate
        ↓
existing page renderer
        ↓
multimodal verification
        ↓
existing proposal mechanism
        ↓
existing review UI
```

Do not reparse the entire PDF with the LLM if the existing parser already produced the candidate.

The multimodal model's job is primarily:

> Compare the extracted representation against the visible source evidence and identify likely mismatches.

## Source-image behavior

Reuse the current renderer.

Prefer the smallest sufficient evidence:

1. source-region crop when reliable;
2. whole physical page when crop geometry is unavailable;
3. adjacent page/context only when cross-page continuation requires it.

Do not invent page geometry.

If the repository cannot identify a reliable region, send the page rather than fabricate a crop.

## Model instructions

The verifier should be explicitly told to:

- compare against visible evidence;
- preserve original language;
- preserve numbers exactly;
- preserve policy wording;
- preserve table relationships;
- report uncertainty;
- use `cannot determine` when necessary;
- never invent missing policy;
- never infer institutional rules from general knowledge;
- never approve content;
- never mark content reviewed;
- never output executable Prolog as trusted truth.

## Useful issue categories

Keep these lightweight. Do not build an ontology.

Possible categories:

```text
omission
substitution
ocr_error
reading_order
hierarchy
table_alignment
row_association
column_association
cross_page_continuation
numbering
possible_duplicate
uncertain
```

Only add categories actually useful to the reviewer or evaluation.

## Selective assistance

Support practical modes fitting current CLI conventions.

Conceptually:

```text
none
flagged
all
selected
```

Where:

- `none` preserves existing deterministic behavior;
- `flagged` applies AI where existing warnings/gaps indicate risk;
- `all` assists every eligible candidate for experiments;
- `selected` assists explicit pages/items.

Do not build a sophisticated scoring engine just for `flagged`.

Reuse existing warnings, gaps, malformed extraction indicators, or similar deterministic signals where possible.

## CLI

Fit this into the existing CLI rather than inventing another application.

Possible shape only:

```text
prepare ... --assist-provider <provider>
            --assist-mode flagged
            --assist-pages ...
```

or an equivalent design consistent with existing CLI architecture.

The existing non-AI command must continue to work unchanged by default.

## Configuration

Provider credentials must come from:

- environment variables;
- existing secure configuration mechanism.

Never store keys in:

- packet files;
- review journal;
- browser payloads;
- Git;
- test fixtures;
- logs.

## Tests

Use the fake provider for default tests.

Test:

- exact source/candidate binding;
- correct physical page;
- image rendering failure;
- proposal creation;
- no-change result;
- uncertain result;
- malformed structured response;
- provider timeout;
- provider exception;
- candidate changed after proposal;
- explicit page selection;
- `none`;
- `flagged`;
- `all`;
- provider never writes a ReviewSession decision.

Add synthetic cases such as:

```text
source:    "15 working days"
candidate: "5 working days"
```

Expected:

```text
AI may propose "15 working days"
review remains pending
human must record correction
```

## Live smoke test

If a compatible provider is already configured in the environment, perform a narrowly scoped live smoke test on non-sensitive representative source material.

Do not make live inference part of the default test suite.

Record:

- provider/model;
- page;
- result;
- whether proposal was correctly presented;
- no secret values.

## Suggested commit

`feat(p11): add multimodal verification to native ingestion`

---

# 12. Task 4 — Extend the existing reviewer UI for AI proposals

## Goal

Make AI suggestions useful without making them authoritative.

Do not build another UI.

Locate the current researcher reviewer and extend it minimally.

## Reviewer display

For an assisted field, make the distinction visually and semantically clear:

```text
Source evidence
Extracted value
AI suggestion
AI rationale / uncertainty
Human decision
```

Do not visually imply that AI confidence equals correctness.

## Required interactions

### Ignore suggestion

Reviewer continues with the original extracted value.

No authoritative AI rejection event is required unless the current review schema naturally supports it.

### Use suggestion

The AI value may populate the correction control.

It must **not** save automatically.

The reviewer still performs the existing explicit correction/save action.

### Modify suggestion

Reviewer may edit the proposed value before recording the human correction.

### Hold / unresolved

Must remain available.

## Stale proposal

If candidate/source identity no longer matches, visibly mark the proposal stale and prevent one-click application.

## AI unavailable

The researcher must still be able to complete normal manual review.

## No bulk AI approval

Do not add:

```text
Accept all AI suggestions
Approve all high-confidence results
Automatically correct >0.9 confidence
```

in this phase.

## Frontend tests

Extend current frontend/browser tests rather than creating another harness.

Verify:

- AI suggestion visible;
- original value remains distinct;
- use-suggestion only prefills;
- save is still explicit;
- modify-suggestion works;
- ignore works;
- unresolved works;
- stale proposal cannot apply;
- provider failure does not block manual review;
- no regression to ordinary non-AI packets;
- no regression to prospectus review where applicable.

## Suggested commit

`feat(p11): surface advisory ai proposals in researcher review`

---

# 13. Task 5 — Implement Strategy B: LlamaParse adapter

## Goal

Implement Lawrence's second requested strategy without creating a second downstream review system.

## Architecture

```text
PDF / selected page batch
        ↓
LlamaParse
        ↓
normalization adapter
        ↓
existing candidate/review representation
        ↓
existing ReviewSession
        ↓
existing build/verify
```

The integration boundary ends at the same place as native extraction.

Do not create:

```text
LlamaParseReviewSession
LlamaParseBuildPipeline
LlamaParseChunkStore
```

## Current API verification

Before implementing live integration, consult the current official LlamaParse/LlamaCloud documentation available to the execution environment.

Verify:

- authentication;
- supported parse endpoint;
- page/range selection;
- async/job behavior if applicable;
- output format;
- error behavior;
- rate/quota responses;
- maximum file/page behavior.

Do not hardcode assumptions about:

- free-tier page count;
- pricing;
- credit consumption;
- account limits.

These change independently of Bintanong.

## SDK vs HTTP

First inspect existing dependencies.

Prefer:

1. an already-installed compatible client;
2. an existing HTTP dependency already used in Bintanong;
3. a small new dependency only when justified.

Do not add a large SDK solely for one endpoint if existing infrastructure can cleanly support the call.

If adding a dependency is narrow, compatible, tested, and follows repository policy, proceed and document it.

Stop only if it causes a broad packaging/runtime conflict.

## Page batching

Support page selection/batching because Handbook and Citizens' Charter are large.

The purpose is:

- checkpointing;
- bounded failures;
- retries;
- selected experiments;
- easier manual validation;
- avoiding restarting an entire document after one failed request.

Do not claim page splitting inherently saves credits unless official provider behavior demonstrates that.

## Resume/retry

A failed page batch must not destroy successful work.

Support, within existing project conventions:

- retriable provider errors;
- timeout;
- authentication failure;
- quota/credit failure;
- malformed response;
- partial batch failure;
- explicit resume or deterministic rerun.

## Provenance

Preserve enough information to answer:

```text
Which source PDF?
Which source SHA?
Which physical page?
Which LlamaParse job/batch if available?
Which parser configuration?
Which normalized candidate?
```

Do not treat provider output itself as reviewed truth.

## Tests

Default suite must mock the provider.

Cover:

- successful single-page parse;
- multi-page selection;
- page batch normalization;
- malformed output;
- timeout;
- authentication failure;
- quota-like failure;
- partial batch result;
- retry;
- resume;
- source hash preserved;
- physical page preserved;
- candidate remains pending;
- no automatic review decision;
- same downstream reviewer can open the result;
- same downstream build path can consume human-reviewed results.

If `LLAMA_CLOUD_API_KEY` or the current required equivalent exists, optionally run a limited live smoke test.

If no key exists:

- complete the mocked/tested adapter;
- mark live smoke test as `NOT RUN — credential unavailable`;
- do not block the rest of implementation.

## Suggested commit

`feat(p11): add llamaparse ingestion strategy`

---

# 14. Task 6 — Harden for Handbook and Citizens' Charter

## Goal

Make sure both strategies are evaluated against the actual failure modes these documents contain.

Do not generalize this into a universal document-understanding framework.

---

## Handbook

Focus tests on:

- Book hierarchy;
- Sections;
- Subsections;
- numbered policies;
- TOC/body disagreement;
- repeated headings;
- header/footer contamination;
- page continuation;
- OCR substitutions;
- omitted policy text;
- multi-page sections.

### Important rule

Treat the TOC as a structural hint, not institutional truth.

If TOC and body disagree:

```text
flag for review
```

not:

```text
automatically rewrite body from TOC
```

---

## Citizens' Charter

Table relationships are more important than raw text presence.

Preserve relationships conceptually like:

```text
Service
 ├─ Office
 ├─ Classification
 ├─ Transaction type
 ├─ Eligible clients
 ├─ Requirements
 └─ Procedure
      ├─ Client action
      ├─ Agency action
      ├─ Fees
      ├─ Processing time
      └─ Responsible person / office
```

Test specifically for:

- row shifts;
- column shifts;
- merged cells;
- one client action → multiple agency actions;
- repeated page headers;
- cross-page procedures;
- fee attached to wrong step;
- processing time attached to wrong step;
- responsible office attached to wrong row;
- detached requirements;
- missing service metadata;
- page continuation;
- repeated heading interpreted as data.

### Critical adversarial fixture

Create a fixture where **all words are extracted correctly** but the relational mapping is wrong.

Example:

```text
Step A fee is attached to Step B.
Step B processing time is attached to Step A.
```

The test must fail even though plain-text recall is technically 100%.

This is important because the Citizens' Charter cannot be validated by text-presence metrics alone.

## Schema gate

If the existing review candidate representation can preserve these relationships, reuse it.

If it cannot and fixing it would require a broadly shared canonical contract change:

**STOP at that boundary** and document the smallest required schema change instead of silently redesigning the source contract.

## Suggested commit

`test(p11): harden ai ingestion for handbook and citizens charter`

---

# 15. Task 7 — Add an A/B evaluation harness

## Goal

Generate evidence for Lawrence's proposed experiment:

> Which approach actually reduces human cleanup?

Compare:

### A

```text
Native parser
+
multimodal verification
+
human review
```

### B

```text
LlamaParse
+
human review
```

Optionally include a native-only baseline if easy to obtain:

### C

```text
Native parser
+
human review
```

This baseline is useful because otherwise we cannot tell whether multimodal assistance actually improves anything.

## Sample

Create a justified representative sample rather than running hundreds of pages immediately.

Include both documents and several extraction types.

Suggested initial target:

```text
20–40 representative pages total
```

depending on available fixtures and provider cost.

Cover:

### Handbook

- normal prose;
- hierarchy;
- numbered rules;
- TOC;
- cross-page policy;
- dense/messy formatting;
- OCR-sensitive page.

### Citizens' Charter

- simple service;
- multi-step service;
- merged table cells;
- repeated headers;
- multi-page procedure;
- fee/time fields;
- responsible-person fields;
- one-to-many actions.

Use the same underlying source pages for A and B whenever possible.

## Metrics

Measure what matters operationally.

### Correctness

- extraction mismatch count;
- omissions;
- hierarchy errors;
- table relation errors;
- reading-order errors;
- wrong numerical values;
- source/citation mismatch.

### Human effort

Primary metrics:

```text
human corrections per page
human corrections per 100 pages
reviewer minutes per page
reviewer minutes per 100 pages
unresolved items
```

### AI assistance quality

- correct suggestions;
- false-positive warnings;
- bad suggestions;
- hallucinated suggestions;
- uncertain responses;
- proposals ignored by reviewer.

### Operational behavior

- provider calls;
- parser calls;
- latency;
- retries;
- failed pages/batches;
- recoverability.

### Cost

If reliable usage/cost information is available from provider responses or current documented rates, record it.

Keep observed and estimated cost clearly separate.

Do not infer accuracy from model confidence.

## Evaluation output

Prefer generated evidence such as:

```text
JSON
CSV
Markdown summary
```

following existing repository conventions.

Do not store this as authoritative knowledge.

Keep large/raw provider responses out of Git unless they are synthetic and deliberately useful as fixtures.

## Example result table

```text
Strategy | Pages | Human corrections | Table errors | Reviewer min | Calls | Failures
---------|-------|-------------------|--------------|--------------|-------|---------
Native   | ...   | ...               | ...          | ...          | ...   | ...
A        | ...   | ...               | ...          | ...          | ...   | ...
B        | ...   | ...               | ...          | ...          | ...   | ...
```

The evaluation should make it possible to answer:

> Is either AI strategy actually worth using for full Handbook/Citizens' Charter ingestion?

## Suggested commit

`feat(p11): add ingestion strategy evaluation harness`

---

# 16. Task 8 — End-to-end regression and security validation

## Goal

Prove the AI extension did not compromise the existing pipeline.

## Required regression paths

Verify:

```text
deterministic prepare
→ review
→ build
→ verify
```

still works with **no AI configuration**.

Verify:

```text
native + multimodal proposal
→ human correction
→ build
→ verify
```

Verify:

```text
LlamaParse candidate
→ human correction
→ build
→ verify
```

Verify relevant existing prospectus behavior remains compatible.

## Security checks

Confirm:

- no API key committed;
- no key written into packet;
- no key written into journal;
- no key returned to browser;
- no key printed in normal logs;
- no provider token inside test snapshots;
- no hosted Supabase write;
- no release/publish mutation;
- no automatic activation;
- no hidden approval field;
- no AI-generated privileged metadata;
- network failure cannot create an accepted result.

## Source binding

Verify a proposal cannot be reused against:

- different PDF;
- different source SHA;
- different candidate hash;
- different item;
- different page when page binding matters.

## Failure-mode validation

Run adversarial cases including:

### Numerical substitution

```text
source: "15 working days"
candidate: "5 working days"
```

### Table contamination

Fee from adjacent procedure row attached to the wrong step.

### Cross-page continuation

Second half of procedure appears on next physical page.

### TOC mismatch

TOC wording/hierarchy differs from body.

### Hallucinated AI suggestion

Provider proposes text that exists nowhere in the evidence.

Expected result:

```text
human review required
```

### Stale proposal

Candidate edited/re-extracted after proposal generation.

Expected:

```text
proposal rejected/marked stale
```

## Full verification

Use repository-native commands discovered from:

- `AGENTS.md`;
- CI configuration;
- Python project configuration;
- frontend package scripts.

Do not invent another test runner.

Record:

- commands;
- exit codes;
- passed tests;
- skipped tests;
- live-provider tests that were not run;
- environment limitations.

## Suggested commit

`test(p11): verify ai-assisted ingestion regressions`

---

# 17. Task 9 — Documentation and operator workflow

## Goal

Make another thesis developer capable of running the feature without understanding the implementation internals.

Document:

## Native-only

```text
PDF
→ prepare
→ review
→ build
→ verify
```

## Native + multimodal

```text
PDF
→ prepare with assist enabled
→ inspect AI proposals
→ human review
→ build
→ verify
```

## LlamaParse

```text
PDF / selected pages
→ LlamaParse strategy
→ review
→ build
→ verify
```

Include:

- required environment variables;
- provider selection;
- model selection if applicable;
- page selection;
- assistance mode;
- retries/resume;
- mock/offline tests;
- how to run evaluation;
- how to distinguish proposal from review decision;
- known limitations;
- data sent to external providers;
- how to run without any AI service.

Do not document T4/T5 as completed unless separately completed and verified.

## Suggested commit

`docs(p11): document ai-assisted ingestion workflow`

---

# 18. Dependency policy

Before adding a dependency:

1. search existing dependencies;
2. search existing utility/provider code;
3. prefer existing infrastructure;
4. add a dependency only when it materially simplifies or safely enables the feature.

A small, justified dependency may be added autonomously when:

- it follows repository policy;
- it has narrow scope;
- it does not conflict with runtime versions;
- lockfiles are updated;
- tests cover the integration.

Do not add:

- another PDF renderer if the existing renderer works;
- another review framework;
- another web framework;
- another database;
- an agent framework;
- a vector database;
- another model orchestration stack.

---

# 19. Prolog / neuro-symbolic boundary

Nothing in this extension authorizes:

```text
PDF
→ LLM
→ trusted .pl
```

For rule-critical content:

```text
PDF
→ parser candidate
→ optional AI comparison
→ human-reviewed source
→ normalized policy representation
→ separately validated symbolic authoring
→ Prolog
```

Keep human/symbolic validation for:

- prerequisites;
- standing;
- eligibility;
- AND/OR relationships;
- exceptions;
- cutoffs;
- enrollment rules;
- institutional constraints.

AI extraction assistance may reduce transcription work.

It does not remove knowledge-representation validation.

---

# 20. Definition of done

This extension is complete when all of the following are demonstrated:

- [ ] Existing deterministic ingestion still works without AI.
- [ ] Existing reviewer remains the sole authority for review decisions.
- [ ] Existing `proposed_value` path is reused where sufficient.
- [ ] No unnecessary parallel AI persistence system was created.
- [ ] Native extraction can invoke a multimodal verifier.
- [ ] The verifier uses original source-page evidence.
- [ ] AI output remains advisory.
- [ ] Human can ignore, use, or modify an AI suggestion.
- [ ] Using a suggestion still requires an explicit human review save.
- [ ] AI/network failure leaves content reviewable manually.
- [ ] Proposal/source/candidate staleness is detected.
- [ ] LlamaParse can parse selected pages/batches.
- [ ] LlamaParse output reaches the same existing review boundary.
- [ ] Failed LlamaParse batches are recoverable.
- [ ] Handbook hierarchy failure modes have tests.
- [ ] Citizens' Charter relational-table failure modes have tests.
- [ ] A relationally wrong but textually complete table fixture is tested.
- [ ] Strategy A and Strategy B can be evaluated on the same sample.
- [ ] Human correction effort can be measured.
- [ ] No AI confidence value is treated as accuracy.
- [ ] No direct trusted Prolog generation was introduced.
- [ ] No API credentials appear in Git/artifacts/browser payloads.
- [ ] No hosted database/release mutation was introduced.
- [ ] Existing prepare/review/build/verify regression tests pass.
- [ ] Relevant prospectus compatibility tests pass.
- [ ] T4/T5 remain correctly represented as separate unfinished work unless independently completed.
- [ ] Operator documentation exists.
- [ ] Final Git status is understood and reported.
- [ ] Every implementation phase has an attributable commit.

---

# 21. Preferred commit sequence

Aim for small, reversible commits resembling:

```text
docs(p11): pin ai-assisted ingestion integration points

test(p11): pin human authority over ai proposals

feat(p11): support source-bound advisory proposals
# only if existing proposal representation needs extension

feat(p11): add advisory ingestion provider boundary

feat(p11): add multimodal verification to native ingestion

feat(p11): surface advisory ai proposals in researcher review

feat(p11): add llamaparse ingestion strategy

test(p11): harden ai ingestion for handbook and citizens charter

feat(p11): add ingestion strategy evaluation harness

test(p11): verify ai-assisted ingestion regressions

docs(p11): document ai-assisted ingestion workflow
```

Skip commits for changes that turn out not to be necessary.

Do not create empty architectural abstractions merely to match this list.

---

# 22. Final report required from Codex

After completing the plan, return:

## A. Repository state

- branch;
- final HEAD;
- working tree status.

## B. Architecture

Explain the final flow for:

- native-only;
- native + multimodal;
- LlamaParse.

## C. Reuse

List what existing Phase 11 components were reused unchanged.

## D. Changes

List modified/new files and why.

## E. Human-authority proof

Explain exactly why AI cannot approve or silently correct policy content.

## F. Tests

For every verification command:

```text
command
exit code
passed
failed
skipped
```

Distinguish mocked tests from live-provider tests.

## G. Live integrations

Report whether:

- multimodal live smoke ran;
- LlamaParse live smoke ran.

If not:

```text
NOT RUN — reason
```

Do not fabricate results.

## H. Evaluation

Summarize available A/B results.

If a meaningful human-reviewed evaluation cannot be completed automatically, generate the harness/sample and clearly identify which measurements require the human reviewer.

## I. Risks / limitations

Report unresolved technical limitations, especially:

- source geometry;
- complex table semantics;
- cross-page parsing;
- provider nondeterminism;
- external API dependence.

## J. Commits

List commits created in order.

## K. Remaining work

Separate:

- AI-ingestion extension work;
- T4;
- T5;
- unrelated backlog.

---

# 23. Final implementation principle

When choosing between:

```text
a clever new architecture
```

and:

```text
the smallest extension of the existing verified Phase 11 pipeline
```

choose the latter.

Lawrence's requested experiment needs two **upstream assistance strategies**.

It does not need Bintanong's ingestion pipeline to be redesigned.