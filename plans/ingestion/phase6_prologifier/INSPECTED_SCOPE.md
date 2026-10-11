# Phase 6 prologifier — inspected scope, not an approved spec or implementation plan

## Owner intent and current boundary
Owner requested parallel planning and a draft implementation for the prospectus prologifier in the old6k+line extractor. FormalPhase6 is structured knowledge/Prolog, not the prospectusA–F naming. Master:148 depends on1/2/4; master:157 permits candidate preparation without phase advancement. No formalPhase6start, Janus/runtime, source activation, embeddings, database/API/Docker work or release approval is implied.

## Existing work to reuse
- integration-fin/docs/decisions/prospectus-extractor-package.md:8 records the6,320line monolith at7591264, source hash8ea75006a4c588902738c3a31096d44aa453a2fdfdeffae8750bf681eae3164d. Its current legacy path is a29line compatibility shim.
- backend/bintanong_tools/prospectus_extractor/prolog.py:72–218 already generates program/course/prerequisite/standing/elective/term candidates and a relational mirror; :28–69 includes fixed candidate query helpers. Full218lines read. This is the current behavior to inspect, not permission to restore older weaknesses.
- prerequisites.py:223–235 defines distinct prerequisite states; alternatives/exceptions remain non-complete; blank is distinct from reviewed empty/stated none.
- pipeline.py:109–140 builds separate authority and blocks clause production on audit error. Audit success labels extraction, not institutional verification or rule approval. The current emitter includes a timestamp and candidate label; it does not itself deliver deterministic provenance-bound formalPhase6 releases.
- Existing consumers: pipeline.build_payload; compatibility shim exports; extractor CLI --export-pl/--export-all, output staging/publication; test_prospectus_authority.py and test_prospectus_materialise.py. Inspect full affected producer/consumer/test modules before any implementation. Existing generator preserved; no user-facing CLI changed by scope notes.

## Proposed approaches for owner review
1. Recommended: a source-linked candidate preparation/compiler boundary, reusing current extraction and formatting helpers. Pending source/field review produces pending rule candidates and explicit blockers; it cannot produce an active rule bundle. Formal semantics and release interface remain separately gated.
2. Existing generator only: lowest code cost and useful compatibility reference, but its extraction-completeness guard/candidate comments do not substitute for reviewed rule specifications, per-rule source binding or approved release coverage.
3. Full Janus/runtime subsystem now: broader than the draft prospectus request and violates current prerequisite/approval/runtime boundaries. Defer runtime integration.

## Recommended candidate scope
Use one canonical structured candidate representation derived from current prospectus payload plus Phase1 document/version/spans and explicit field-review evidence. Validate source digest/edition/identity before compilation. Preserve course codes, units, electives and prerequisite state; no default blank-to-zero/no-prerequisite promotion. Preserve all-of/any-of/co-requisite/exception semantics only when explicit and supported; unknown or unsupported structures remain blocked for review. Detect cycles/unresolved references, report them, never auto-repair policy. Stable IDs/digests and deterministic candidate content exclude volatile generation timestamps from identity. Existing generated relational/Prolog views are outputs, not separately edited truth.

For this preparation, candidate clause text is review data in external JSON/manifests. No consult/load/query, arbitrary goals, active .pl publication, approved-state promotion or institutional/student record persistence. Future formal runtime requires reviewed specifications and fixed bound goals; request facts remain local. Policy/entity rules are never inferred from a student's upload.

## Acceptance evidence to name in the future plan
Synthetic-only fixtures: resolved all-of, explicit no-prerequisites, blank/unreviewed, unreadable/unresolved, alternatives/exceptions, standing/co-requisites, malformed/forged state, unknown course, wrong curriculum/digest, duplicate codes, cycles, quoting/comment injection, source mutation, deterministic output and no input mutation. Test authority/field-review separation and provenance coverage. No Prolog execution; systempy3.13, pytest no-cache/external basetemp, bound imports. Root owns a relevant broad gate; fresh independent Spec then separate Standards. Review exceptions remain one recheck for a confirmedHigh fix.

## Approval stage
This is an inspection note and proposed scope. The explicitly requested Codex brainstorming skill:38–55 requires architectural written-spec approval, then implementation-plan review/execution selection; conversational design approval only permits writing the spec. No product code, scaffold, new project or implementation plan was created. The owner has selected subagent implementation generally; do not request that method again. Preserve applicable two-agent limit. Next: present the concrete scope, obtain conversational design approval, write external spec for owner review, then approved plan and separate implementer. No commit/owner checkout writes are authorized here.

Nothing here is institutional approval.
