---
artifact: phase-plan
phase: 1
status: in_progress
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-00-handoff.md
---

# Phase 1 — Source governance, shared contracts and experiment design

Formally started on 2026-10-08 (owner authorization recorded in `plans/phase-01-checkpoint.md`), on the local branch `feat/phase-01-source-governance-contracts` only. The prospectus extractor/review workstream stays parallel and does not advance this ledger; preparation documents are not completion. Nothing here completes Phase 1, authorizes Phase 2 advancement, verifies any institution document or activates any curriculum. Existing runtime behavior remains unchanged unless a task says otherwise.

## Goal and authoritative context

Follow master §§1.3, 6, 7, 11.4 and 16, the thesis scope and runtime architecture: undergraduate academic-policy assistance, Bintu-1 routing to RAG/Hybrid/Symbolic, separate institutional evidence and anonymous private session facts, source-supported outcomes and explicit abstention. The parallel prospectus extractor/review/OCR workstream produces candidates and does not advance this ledger. Extraction audit, content review and source verification are separate; none is institutional approval.

## Global constraints

Work in a worktree under Bintanong-wt, preserve owner checkout and existing history. No attribution trailers, automatic merge, dev movement or source activation. Original PDFs/images/PPTXs, acquisition metadata with local paths, references, private inputs and generated evidence stay outside Git. Commit schemas, governance documentation, synthetic examples, tests and plans only. No private grades/photos/student identity in institutional manifests or evaluation artifacts. Use fresh approved environments or owner-authorized system Python; no existing-venv installs/sync. Root runs broad gates directly in PowerShell, external pytest basetemp; one implementer followed by independent reviewers.

## Repository boundaries

| Location | Planned responsibility |
|---|---|
| backend/bintanong_contracts/ | Cohesive shared source, ingestion and runtime types/validation; reuse existing Pydantic conventions and compatibility adapters |
| knowledge/manifests/ | Source-register schemas, controlled vocabulary and governance; public examples contain synthetic locators only |
| evaluation/ | Rubrics, grouping/split policy, versioned synthetic templates and evaluation harness contracts |
| plans/ | Formal ledger/plan, source-inventory summary, unresolved decisions and Phase 2 preparation |
| External originals/reference/scratch roots | Immutable original bytes, acquisition inventory, restricted references and generated evidence |

These are planned boundaries, not instructions to scaffold empty modules. Inspect backend/bintanong_api, bintanong_embedding and bintanong_tools consumers before implementing shared models.

## Ten contracts and invariants

All contracts carry explicit schema versions; reject malformed/unknown privileged status assertions. IDs are stable within a documented source edition, never inferred from filenames. Exact field names are settled against existing consumers at implementation, documented through adapters rather than parallel independent models.

| Contract | Minimum content and trust boundary |
|---|---|
| SourceDocumentVersion | Document/version IDs, issuer, scope, acquisition locator/hash, verification state, approval identifiers, effectivity and supersession evidence. Local acquisition is pending; approval null without authorized evidence. Distinguish observed metadata from verified scope. |
| SourceSpan | Exact source version/digest, physical PDF page, optional printed label, section/table/cell locator, printed text and extraction provenance. Original-page offsets survive split PDFs; bounding boxes have origin/page-size metadata. |
| Chunk | Edition-stable ID, complete source spans, printed source_text separate from explanatory text, section path/scope, content hash, chunker version and count metadata. Unanchored inputs cannot assert a verified source. |
| EmbeddingRecord | Chunk ID, model ID/revision, tokenizer/preprocessing/prompt fingerprint, dimension, normalization and vector. Exact token counting includes prefixes and special tokens; estimates never guarantee limits. No embedding/vector calls in Phase 1. |
| NormalizedQuery | Original/minimally normalized text, language hints, intent, resolved entities, ambiguities and references to private session facts. Preserve negation/time qualifiers; user assertions are not policy. |
| RoutingDecision | Schema version, RAG/Hybrid/Symbolic or null, control outcome, typed predicate request, required/missing facts and short reason. Validate before dispatch. Existing Direct discrepancy remains unresolved during preparation. |
| RetrievalResult | Knowledge-release ID, chosen chunks/scores/source locators, coverage status and configuration. Results cannot mix incompatible editions/releases silently. |
| SymbolicResult | Five-outcome status, supported predicate, typed inputs, satisfied/violated/unknown conditions, rule IDs/source spans and rule-bundle version. Fixed goals with bound inputs, no arbitrary generated Prolog. |
| EvidenceBundle | Route/release, institutional passages, symbolic result, session-only facts, unresolved conflicts and permitted claims. Private facts cannot promote sources or enter institutional storage. |
| AnswerEnvelope | Status/language/text, scoped structured decision, citations, validation result and request ID. Unsupported, unknown and operational error never become approval/denial. |

## Governance and conflict handling

Register each acquired byte identity and its acquisition evidence before parsing. Preserve duplicate locators and differing versions rather than treating same filename as same edition. Record source issuer, campus/college/program/cohort scope, printed revision/effective dates, supersession and authorization as separately observed/pending/verified fields. Do not infer effective school year, authority or a hierarchy from filename dates, college versus university wording or local possession. A proposed BOR curriculum remains a proposal candidate. Preserve both handbook versions and distinct Charter PPTXs.

A conflict is an explicit record naming the incompatible claims, source versions/spans, affected scope, current resolution state and authorized resolution evidence. Do not pick the newest-looking filename or invent an office precedence. Unresolved conflicts block only the corresponding capability; unrelated infrastructure work can continue. Source approval and content review are distinct transitions with provenance. Activation requires verified scope/effectivity and authorization; no supplied authorization currently exists.

Private uploaded transcripts, grades and photographs are anonymous session context, never institutional evidence. Institutional source IDs and session fact IDs have separate namespaces/storage/lifecycles. Student confirmation does not write a staff ledger or update an institutional source. Define retention/deletion/session isolation and inspect existing API boundaries before implementation.

## Five decision outcomes

| Outcome | Required meaning |
|---|---|
| eligible | Every supported scoped condition satisfied, required facts and authoritative rule coverage present; no official enrollment approval implied |
| ineligible | At least one documented applicable condition demonstrably unmet, with evidence |
| unknown | Missing facts, applicability, rule coverage or conflict resolution; ask/explain what is missing |
| unsupported | Operation outside approved capability registry; no invented predicate/decision |
| error | Operational reasoning failure; never converted into a policy result |

Verified zero prerequisites differs from blank/unreviewed, unreadable, unresolved or unsupported rule structure. RAG explanation success does not satisfy a failed Hybrid symbolic component.

## Evaluation protocol

Prepare development and sealed final sets separately. Group paraphrases, English/Tagalog/Taglish variants and near-duplicate scenarios in one split; define a stable scenario-family/group ID and disjoint split assignment before tuning. Shared approved source corpus is allowed; final answers/examples never tune prompts, thresholds or rules. Synthetic cases are explicitly synthetic, not verified policy.

Five thesis categories: enrollment, prerequisites, grades, academic standing and discipline. Target at least 50 independently verified final Taglish cases, at least ten per category. Each case records group/category, query, applicable version/scope, expected route/control outcome, five-outcome result when relevant, required/missing facts, gold spans/rules, acceptable claims/abstention, reviewer/evidence/version and split. No verified-final claim until source-backed independent review exists. Include ambiguity, negation, missing facts, wrong edition, conflicting evidence, unknown course, incomplete coverage, unsupported operations and operational failure. Keep private evaluation evidence restricted outside Git; committed templates use fictional students and synthetic policy.

## Task checklist

- [ ] 1. Inspect Phase 0 handoff and consumer contracts; document versions and Direct routing discrepancy without changing runtime.
- [ ] 2. Finalize register vocabulary/state transitions, source scope/effectivity/supersession and conflict records, acquisition/authority separation.
- [ ] 3. Implement shared contracts incrementally using tests for malformed input, forbidden status promotion and institutional/private mixing; preserve existing adapters.
- [ ] 4. Bind one source version/span to one reviewed chunk, one rule draft and one evaluation case; synthetic traceability checks may precede source authorization but remain synthetic.
- [ ] 5. Implement split/group validation and rubrics; build development examples, freeze final protocol and prepare fifty source-backed final cases when verified coverage exists.
- [ ] 6. Independently review source governance/contracts/privacy and run focused/comprehensive checks directly; record actual source/authorization blockers.

## Review focus and verification

Use [evaluation/README.md](../evaluation/README.md) for route, evidence, symbolic-result, answer-correctness and unsupported-claim rubrics. Record code_version, prompt_version, model_revision, quantization, embedding_config, knowledge_release_id, rule_bundle_version and decoding parameters with each run. A committed template is not a verified benchmark case.

Adversarial tests cover fabricated verification/approval, incompatible editions, source mutation, duplicate source locations, missing printed page labels, invalid span geometry, copied private facts, route/outcome confusion, stale derived state, unsupported rules, partial Hybrid results and group leakage. Test deterministic roundtrips/schema compatibility against API/tools/embedding consumers. No synthetic assertion establishes institution policy. Explicitly inspect source inventories against original hashes; external inventory current count is preparation evidence only.

## Exit gate

The ten contracts and governance vocabulary are documented/validated, institutional/private boundaries enforced, evaluation groups/splits/rubrics established, and one document/chunk/rule/case traces to exact source spans with honestly recorded verification state. Independent review and actual tests must pass. Missing authorized source coverage is documented rather than fabricated. Only then may a complete Phase 1 handoff authorize Phase 2. This plan is in progress; no Phase 1 completion/handoff exists.

## Known discrepancy

backend/bintanong_api/bintu_client.py presently permits Direct alongside three runtime routes, whereas master intent is Bintu-1 RAG/Hybrid/Symbolic with explicit null/control outcomes. Resolve the contract/compatibility meaning during Phase 1 implementation with regression evidence; preparation changes no route behavior.
