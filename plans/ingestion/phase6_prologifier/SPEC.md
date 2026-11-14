# Phase 6 prospectus candidate compiler — written specification

Status: conversational approach approved by the owner's “Yes” on 2026-10-10. Written design was presented; the owner's 2026-10-11 continuation was used to prepare IMPLEMENTATION_PLAN.md for confirmation. Owner explicitly authorized alignment-report corrections and implementation on2026-10-11. This is candidate preparation, not formal Phase 6 advancement or institutional approval.

## Purpose and boundary

Prepare reproducible, source-linked rule candidates from the existing prospectus extraction payload. Reuse the current generator and prerequisite analysis rather than restoring or rewriting the 6,320-line monolith. Give reviewers the candidate semantics, exact source support and unresolved issues in one artifact. Every output remains inactive review data.

The master plan requires source clause → spans and scope → reviewed specification → domain review → approved version bundle → rule tests. This draft implements only the candidate preparation boundary. It does not deliver Janus, eligibility decisions, approved rules, release coverage or activation.

## Existing implementation and scope

Existing behavior is in backend/bintanong_tools/prospectus_extractor/prolog.py (218 lines): generate_prolog_knowledge emits candidate course, prerequisite, standing, elective and term relations plus formatted clause text. prerequisites.py distinguishes resolved, stated_none, reviewed_empty, blank_unreviewed, unresolved_reference, standing_condition, alternative_or_exception and unreadable. audit.find_prerequisite_cycles detects multi-course cycles but filters direct self-edges; the new boundary must reject self-prerequisites explicitly.

The new preparation module is additive. It imports existing formatting/generation helpers, prerequisite classification and cycle detection. It uses existing Phase 1 contracts directly. It does not alter pipeline.build_payload, current CLI/export behavior, protected contracts, extractor behavior, runtime routing, configuration, dependencies or lockfiles. A later approved integration change can connect the compiler to existing CLI staging.

Affected places for this draft: one new pure candidate module, focused synthetic tests and a decision record. Inputs and review outputs live outside Git. Existing callers remain compatible. Generated clauses and relations are derived views, never separately edited truth.

## Input contract

Callers supply:
1. A current prospectus candidate payload, including the extractor's source-byte digest and course/prerequisite metadata.
2. A parsed SourceDocumentVersion, validated through check_register, with the registered byte digest and document/edition/version identities.
3. Explicit per-record, per-field SourceSpan evidence and any review-evidence references. Evidence must name which candidate field it supports; a document-level source label cannot stand in for every rule's provenance.

The module accepts already-produced extraction data; it does not read an arbitrary path, run conversion, consult Prolog or collect student data. Original PDF bytes and reviewer source checks remain the authority. Generated JSON is not a validation oracle.

Before formatting any candidate, require payload digest equality with the register. Parse spans through SourceSpan, check_span_binding against the registered bytes, and require complete text, physical page and locator. Explicitly require each rule-supporting span's version_id to equal the register version_id; an optional span version must not weaken this boundary. Reject foreign namespaces, invalid geometry, unknown fields or forged privileged state. Evidence for another edition cannot be borrowed because its course code matches.

Do not infer issuer, effectivity, curriculum scope, approval or supersession from a filename or extraction success. Retain pending register states. Acquisition mismatch refuses preparation. Supplied review evidence is recorded for review; it cannot itself promote institutional approval.

## Candidate representation

Produce one JSON-serializable review artifact with a format/compiler version, source document/edition/version/digest, inherited source states, candidate records and a complete blocker list. All records have activation_allowed=false and approval_id=null. The artifact contains no active rule bundle or runtime decision result; SymbolicResult is not reused as a rule-ledger schema.

Each record carries a stable id, its rule/fact kind, exact course identity, typed candidate value, the original prerequisite state and text where applicable, supporting spans, scope as recorded by the source register, review evidence references and blockers. Clause strings and the existing relational mirror may be included as clearly labelled review views for supported records. Fixed query helper code from PROLOG_RULES is not published as a callable runtime.

Stable identifiers and the artifact content digest derive from canonical candidate semantics, source version/digest and normalized locator identities plus compiler version. Ignore timestamps, local absolute paths and traversal order. Preserve semantic list order when the source gives an order; sort only unordered record collections deterministically. Do not mutate caller inputs.

## Validation and preserved semantics

Validate types before calling the existing generator. Course codes must be nonempty and unique within the source; resolved prerequisite claims must reference known course codes in that source and may not reference themselves. Structurally valid source-supported unknown codes remain unresolved_reference review blockers; they do not discard the review artifact. Reject bools masquerading as numbers, non-finite/negative values and malformed containers. Validate year/semester/unit values before interpolation. Unsupported or missing numeric facts remain unknown or blocked; the generator's historical fallback of zero is not accepted as source evidence. A printed zero may be retained as a zero only with supporting span text and field provenance.

Resolved all-of prerequisites can have a supported candidate view only when every referenced course and every prerequisite edge is source-supported and recomputed classification agrees with the payload. stated_none requires explicit source wording. reviewed_empty requires an explicit applicable reviewer record; a blank cell alone remains blank_unreviewed. Treat supplied executable/completeness/authority flags as untrusted claims, not authorization.

Preserve alternatives, exceptions, co-requisites, standing requirements and unreadable/unresolved text as review blockers. Do not flatten “A or B” into “A and B”, infer a corequisite rule from course proximity, or convert unsupported wording into an eligibility clause. Such records still retain raw text, spans and their unresolved representation. Detect cycles with the existing detector and reject self-edges separately. Report affected candidates without silently repairing source policy.

Preserve extracted raw source text, including negation, punctuation, numbers, dates, en dashes and superscripts. Helpers may normalize identifiers for matching/quoting, but normalized text must not replace the retained original evidence. Course title, code, units and prerequisite fields each need their own supplied support or an explicit blocker.

Malformed global inputs, source mismatches or invalid span bindings fail before a candidate artifact is returned. Recoverable semantic incompleteness produces a complete review artifact with blockers. No blocked semantic record gets a completeness marker or an eligible/approved interpretation.

## No execution or status promotion

Output is JSON review data only, optionally containing quoted candidate-clause strings. Do not write active .pl files, invoke Janus/consult/query, register goals, alter routing, persist private facts, create embeddings or change APIs/Docker. Never convert audit success into content review, source verification or policy approval. No output is an admission, academic eligibility decision or authorized institutional rule.

The compiler is a pure function. Publication, if added in an approved later plan, must reuse established external scratch/staging containment and verify original source identity before publication. It must not write next to an original or into the owner checkout.

## Focused acceptance checks for the draft

Use synthetic source-backed fixtures and system py -3.13. Check digest/version/edition mismatches, incomplete/foreign spans, forged authority fields, duplicate/unknown/self-referencing courses, malformed and non-finite numbers, printed zero versus missing values, explicit none versus blank/reviewed empty, alternative/standing/corequisite blockers, cycles, quote/comment injection, stable output and input immutability. Verify every output record is inactive and no Prolog execution/file publication occurs.

Test reuse against existing supported generator output, excluding its volatile timestamp. Do not infer correctness from agreement with generated JSON alone. Local draft commit requires these focused checks and accurate limitations. Full corpus accuracy, human source review, mutation campaign, runtime tests and release validation remain deferred under the owner's latest instruction. Independent Spec and separate Standards review still govern review readiness; focused passing tests alone do not establish approval or merge readiness.

## Follow-on gates

Owner instruction to implement the alignment report authorizes the corrected written plan and isolated draft implementation. The plan must identify the concrete additive module, evidence mapping, focused tests and controlled integration boundary. The owner has already selected subagent implementation; no repeat execution-method question is needed. Local draft commits are authorized, while formal phase start/adoption/merge/API/Docker/source activation remain separately gated.

Nothing here is institutional approval.
