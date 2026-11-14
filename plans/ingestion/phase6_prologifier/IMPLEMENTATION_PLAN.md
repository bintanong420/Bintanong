# Prospectus Rule Candidate Compiler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox tracking.

**Goal:** Build a pure, deterministic, source-bound review artifact from existing prospectus curriculum data without publishing or executing active rules.

**Architecture:** One additive module validates source/field evidence and candidate semantics, reuses existing quoting/generation and prerequisite/cycle helpers, and returns inactive JSON. It does not alter the extractor, source contracts, current CLI or runtime.

**Tech Stack:** System Python3.13, existing Pydantic contracts and prospectus helpers, pytest; no added dependencies.

**Spec:** [SPEC.md](SPEC.md).

Status: owner explicitly authorized implementation of plan_alignment_20261011/REPORT.md on2026-10-11, including the clarified unresolved-reference acceptance case. Implementation is authorized in the isolated draft. Owner has already selected separate fresh implementer, Spec and Standards runs; coordinator+one active child maximum.

## Global constraints

- Execute from a verified isolated worktree based on57b598522cc7ed5d13e40eb8d1bcafede8c9ba1b unless fresh Git proves a newer approved parent. No owner/protected-ref changes, adoption, push/merge or attribution.
- Every PowerShell first selects its worktree; absolute paths, systempy-3.13-B, no bytecode/cache, unique external pytest basetemp, offline. No installs/downloads/dependency/lock changes.
- Only inactive JSON review data is returned. No .pl files, PROLOG_RULES query helpers, Janus/consult/query, embeddings, runtime routing, API/Docker or ledger advancement.
- Original PDF and explicit source review are authority; generated payloads and claimed review flags are untrusted inputs. Source/content states are inherited, never promoted.
- Stop new batches>=85% either Codex window; save>85 promptly. New feature reviews cannot close unrelated M1/F/session findings by implication.

## Review focus

1. Missing numeric evidence must not turn into the generator's zero fallback; printed zero needs field support.
2. Blank, reviewed-empty, explicit-none and unresolved alternatives must remain distinct.
3. Same course code from another edition or optional-null span version must not satisfy provenance.
4. Unknown/self/cyclic prerequisites and injection-like titles must not yield usable rule views.
5. Reordered unordered inputs and volatile timestamps/paths must not change stable candidate identity or mutate inputs.

All five are pinned in the single cohesive task below. This authoring check is not an independent review verdict.

## Task1: Pure source-bound candidate preparation

**Files:** create backend/bintanong_tools/prospectus_extractor/rule_candidates.py; create tests/test_rule_candidates.py; create docs/decisions/phase-06-prospectus-candidates.md. Reuse existing synthetic fixture builders where possible; add local fixtures in the new test module rather than a new fixture framework. No other product file changes.

**Consumes:** source.SourceSpan/check_span_binding, governance.SourceDocumentVersion/check_register, prolog.pl_atom/pl_comment/generate_prolog_knowledge, prerequisites.classify_prerequisite_state, audit.find_prerequisite_cycles and current structured payload.courses/elective_tracks/term_units.

**Produces:** `build_rule_candidates(payload:Mapping[str,Any], source:SourceDocumentVersion, field_spans:Mapping[str,Mapping[str,Sequence[SourceSpan|Mapping[str,Any]]]], *, review_evidence:Mapping[str,Any]|None=None)->dict[str,Any]`. field_spans is keyed by exact unique course_code and the existing fields course_code,course_title,units.total,units.lecture,units.lab,year_level,semester,term_index,prerequisites_raw,category. This first boundary has no independently supported program/term/elective field mapping: preserve any such supplied values in blocked review records, with `unsupported_field_evidence`, and emit no corresponding clause. Do not grow an evidence schema to infer them from course proximity. Review evidence is source-version/field-bound recorded evidence, not an approval switch.

- [ ] Add focused RED cases for source/payload digest mismatch, edition/namespace/privileged claims, incomplete/foreign/null-version spans and invalid geometry; assert no artifact is returned and inputs remain untouched.
- [ ] Add semantic RED cases: explicit resolved all-of, stated-none wording, applicable reviewed-empty evidence, blank-unreviewed, OR/exception/corequisite/standing/unreadable blockers and multi-course cycle blockers; a structurally valid source-supported printed XX999 absent from the catalog remains an unresolved_reference record with raw text and spans, blocks dependent views, and does not discard the review artifact. Malformed/forged reference data, false claims of resolved edges, self-edges, duplicate codes and malformed bool/nonfinite/negative numbers refuse globally. Missing meaningful numeric facts versus independently supported printed zero stay distinct. Each blocked record retains its source wording and support; no complete/eligible/approved marker is emitted for it.
- [ ] Add inactive/deterministic RED cases: all records activation_allowed=false/approval_id=null; no query helpers/directives or rule_complete eligibility marker in emitted views; quotes, backslashes and comment/newline injection stay data; reordered record collections/volatile generator timestamp/local paths do not change IDs or content digest; exact retained raw text includes negation/dashes/superscripts. Poison publication/execution calls so any attempted file write, network fetch or Prolog invocation fails the test.
- [ ] Run the new test module only, using worktree-bound imports and external no-cache basetemp; save RED commands/exits. Do not edit production until failures match the missing new boundary.
- [ ] Implement global validation first: reparse source/check_register, require payload.run_identity.pdf_sha256==source.byte_sha256, validate known field names and complete field spans, require each supporting version_id exactly equals source.version_id, run check_span_binding and reject malformed input before constructing an output. Copy data instead of mutating models/dicts. Source scope/state remains pending or as independently validated; forged supplied authority is rejected.
- [ ] Implement record preparation: preserve raw field/prerequisite text, compare recomputed prerequisite classification with the payload, distinguish valid unresolved_reference/unknown catalog entries (blocked records) from malformed/forged resolved references (global refusal), reject self-edges, and use the existing cycle detector for longer cycles. Only source-supported all-of/explicit-none/reviewed-empty cases may receive supported review views. Unsupported semantics or absent valid field support remain explicit named blockers. Malformed scalar/container input refuses globally; meaningful unknown values are blocked records rather than invented numeric zero.
- [ ] Reuse the generator only with fully validated supported inputs, or its quoting/formatting helpers where whole-generator defaults would fabricate absent facts. If using its result, select only explicitly allowed source-supported relational facts; never copy full clauses containing directives, program/term totals without support, rule_complete or PROLOG_RULES. Do not claim exact full-generator parity; tests compare supported values with the existing generator while independently checking source support and inactive state.
- [ ] Return format_version,compiler_version,source identity/states,records,blockers and content_digest. Stable record IDs hash canonical semantics+sourceversion/digest+normalized span locator identities+compiler_version, excluding local paths/time. Sort unordered record sets only; preserve ordered semantic values and source text. Record fields include id,kind,course_code,value,prerequisite_state,raw_text,spans,scope,review_evidence_refs,blockers,activation_allowed=false,approval_id=null. No runtime SymbolicResult or competing editable truth store.
- [ ] Run focused GREEN plus existing prerequisite/generator/contract tests located by rg; choose the smallest tests actually exercising reused helpers. Root independently verifies imports, all inactive records, exact no-execution boundary, frozen hashes, diff --check and only the three allowed paths. No repeated ~4000-test suite without new justification.
- [ ] Explicitly stage those three paths and commit `feat(prospectus): prepare source-bound inactive rule candidates`. Freeze an external read-only candidate archive. Fresh independent Spec review, then fresh separate Standards only after Spec passes; never self-review. One confirmed High repair recheck only, unless the owner explicitly grants a separate exception.

## Commands and exit criteria

Start every PowerShell with Set-Location -LiteralPath '<ABSOLUTE_EXECUTION_WORKTREE>'. Run `py -3.13 -B -m pytest <ABSOLUTE_TEST_PATHS> -q -p no:cacheprovider --basetemp <NEW_ABSOLUTE_EXTERNAL_PATH>` with process-only no-bytecode/offline flags and asserted worktree-bound imports. RED must demonstrate the new missing invariant; GREEN must exit0. Save actual counts/logs/exits externally. Git staging uses only the three named paths; no generated JSON is staged.

Exit means an implemented and independently reviewed candidate-preparation boundary with truthful limitations, not full Phase6 or approved institutional rules. Corpus/domain review, governed release compilation, capability registration and typed Janus remain later phases. Current Phase6 full estimate remains~25 until implementation/evidence changes; this plan earns no implementation credit and does not raise overall ingestion by itself.

Owner instruction to implement the alignment report authorizes the corrected written plan and execution; no repeat confirmation is required. The selected subagent method and owner implementation authorization are already recorded; no repeat confirmation is required. API/Docker, adoption/merge and source activation remain separately gated.
