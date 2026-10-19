# Structured curriculum authoring

`authoring.build_curriculum_ledger(scope, sources, courses, reviews=())` validates
source-bound structured records. It emits inactive authoring JSON, not Prolog,
eligibility decisions, a runtime capability or a release approval.

Use reviewed undergraduate source selections. Scope is explicitly supplied
program_id/curriculum_id, and remains declared rather than institutionally
verified. Existing SourceDocumentVersion/SourceSpan validators bind original
bytes, source version, physical page and locator. Each course repeats the same
scope and its owning source version. Prerequisite references must name another
course from that version. Cross-source/version composition is deferred.

Supported facts: course_code (required), course_title, units.total/lecture/lab,
year_level and semester. Each value needs its own complete printed-field support.
Units accept finite nonnegative numeric values; missing facts stay absent and an
explicit printed zero stays zero. No curriculum/cohort/grade inference occurs.

Requirements preserve authored course, co_requisite, ordered all_of/any_of,
verified_none or unresolved nodes with source spans. No text-to-logic parser or
evaluator exists here. None/empty conjunctions are rejected; unknown requirements
need an explicit unresolved reason. Expression traversal is bounded to32levels.
Even verified_none is an authored assertion: record review and original source
authority remain separate; this module cannot verify a university policy's truth.

Review workflow:

1. Prepare courses with review_state=draft and review_refs=[]; build the ledger.
2. A researcher reviews those exact facts/logic/source spans. Record a review_id,
   source_version_id, reviewer_label and course_digests map from course_id to the
   prepared course content_sha256. Labels are declared attribution, not identity
   authentication or issuing-office authorization.
3. After that actual review, rebuild with review_state=reviewed and review_refs
   naming the receipt. The digest binds the complete normalized authored content,
   excluding review state/references to avoid a circular identity. Changed content
   cannot silently retain the old review. Unreferenced historical receipts remain
   review data; they do not apply to changed course records.

All outputs retain activation_allowed=false, eligibility_executable=false and
approval_id=null. Original source lifecycle fields remain unchanged. Course,
source and review collections sort deterministically; semantic item/span order
is preserved. Callers cannot supply arbitrary extra fields; no input string is executed.

`compiler.compile_curriculum_preview(ledger)` revalidates the complete ledger,
including all derived digests, review receipts and inactive flags. Reviewed,
structurally complete input produces reproducible `candidate_*` ground facts;
source records/review receipts and complete original spans remain attached as
canonical JSON data. Ordered all_of/any_of trees and co-requisites are preserved.
It emits no eligibility predicate and performs no Prolog execution or file writes.

Drafts, unresolved conditions or a detected prerequisite cycle hold the entire
preview with diagnostics and null Prolog. Cycle reporting gives one deterministic
witness, inspecting all alternative branches conservatively; it is a request for
review, not a policy denial. Co-requisites are not prior-completion edges. Text
accepted by authoring but incompatible with the existing strict atom-quoting
contract is held as `unrenderable_text`, preserving the original ledger verbatim.

Source lifecycle states remain unchanged and are carried as release holds. A
pending source can support an offline candidate preview; a review label/digest
cannot make it an authorized institutional bundle. Every output still has
activation_allowed=false, eligibility_executable=false and approval_id=null.
The returned content/prolog SHA-256 digests identify the exact preview; they do
not authenticate reviewers or establish truth, applicability or school approval.

The existing prospectus extraction candidate compiler and capability registry are
unchanged. No real-source rule translation is approved by synthetic tests. Runtime
compilation/release gates and institutional operation registration remain future
Phase06 increments; the synthetic research runtime is described below. Do not use
the preview for institutional decisions.

`compiler.compile_curriculum_review_bundle(ledger)` is the separate partial human
review exporter. It revalidates the same complete ledger and emits reviewed
`candidate_fact` values and unresolved-free reviewed `candidate_requirement` trees.
Draft facts/rules remain absent from those semantic predicates. All courses have
`candidate_reference_identity` with their exact code, source, digest and explicit
identity review state, plus `candidate_coverage` with direct-rule state, unresolved
reasons and ordered pending identity references. Full `candidate_record` JSON is
audit evidence; it does not promote draft contents to reviewed facts.

A reviewed identity can still have unknown prerequisites. A reviewed direct rule
can name a draft identity, which stays flagged for review. Neither case establishes
transitive coverage or eligibility. Explicit verified_none is exported only when
reviewed; blank or missing prerequisites never produce it. An unresolved branch
holds that entire course expression, preserving all-of/any-of semantics.

Partial output has status `partial_review_candidate`; all-draft input can produce
an identity/coverage audit only. Reviewed complete input is `review_candidate`.
A cycle among reviewed complete prior-completion expressions or unrenderable text
holds the entire export as `blocked` with null Prolog. Draft edges do not contribute
speculative cycles; co-requisites stay distinct. The strict preview is unchanged.
Every review bundle retains runtime_ready=false, activation_allowed=false,
eligibility_executable=false, approval_id=null and explicit release holds. The
function returns text in memory; offline tooling may save it for human review.
No Prolog consultation, decision, source promotion or capability registration occurs.

## Synthetic prerequisite runtime

`bundle.prepare_runtime_bundle(ledger)` extracts the same compiler-checked worker
projection as a deterministic `curriculum-runtime-bundle-v1` JSON artifact. It
binds the complete ledger, review-compiler digest, coverage, source/release holds,
compact payload and exact tracked Prolog engine bytes. Preparation neither
consults Prolog nor promotes a source. Every artifact retains runtime_ready=false,
activation_allowed=false, eligibility_executable=false and approval_id=null.
Real-source ledgers may be prepared only as inactive data.
The explicit offline acceptance path below can execute their checked projection
for research without changing these artifact flags.

`bundle.validate_runtime_bundle(bundle)` rebuilds every field against the current
compiler/engine and rejects any difference, including unknown extra keys.
`CurriculumRuntime.from_bundle(bundle)` validates saved JSON and creates the same
synthetic-only runtime as the ledger constructor. A concurrent engine/compiler
change rejects loading; later engine drift rejects in the worker. Hashes prove
content identity, not reviewer authentication or institutional permission.

`runtime.CurriculumRuntime(ledger).check(request, facts=None)` is the offline
research runtime for `check_prerequisite_eligibility` and
`list_missing_prerequisites`. Its
PredicateRequest has exactly `curriculum_id` and `course_id` bound inputs;
`StudentFacts` contains explicit synthetic passed/failed/currently enrolled and
explicitly not_enrolled course IDs. Missing enrollment is unknown; failed completion
alone cannot prove an unmet co-requisite. This is normalized fixture state, not numeric grade interpretation or policy
for repeated attempts, exemptions or equivalent courses.

The constructor revalidates the entire ledger through the review compiler and
retains detached immutable JSON. It rejects non-synthetic sources and compiler
holds. Institutional candidates cannot execute through this interface. Synthetic
execution does not change ledger flags, approve sources, activate a release,
register an institutional capability or publish an API. EMPTY_REGISTRY stays empty.
Non-synthetic release/runtime integration remains a separate gated Phase06 step.

The canonical [Prolog engine](../algorithms/curriculum_runtime.pl) in
`backend/algorithms/` evaluates reviewed expression trees: ordered all_of/any_of,
explicit co_requisite and verified_none. Draft identities, unknown rules, missing
completion and mismatched curricula remain unknown; known required failure stays
distinct. Any satisfied alternative is sufficient; missing alternatives alone do
not establish failure. Conflicting relevant completion states stay unknown unless
an independent alternative proves the result. A referenced course's own unknown
prerequisites are not rechecked when its explicit completion is supplied; this is
a direct prerequisite check, not an inferred transitive completion audit.

The adapter uses the existing registry and SymbolicResult contracts, attaching
scoped rule/source spans and stable satisfied/violated/unknown explanations.
The missing-prerequisite operation returns the same scoped decision with known
unmet and unknown conditions; it does not flatten alternative paths into a new
conjunction. Other decision operations return unsupported. It never interprets a failed Prolog goal,
worker failure, malformed output, timeout or size limit as a policy denial.

Each request runs in a fresh hidden Python/Janus subprocess with typed input
bindings and one of two fixed goals. Only the tracked engine is consulted; its exact bytes
are pinned in the bundle identity and checked by the worker. Authoring/candidate
files are not consulted, student facts are arguments, and there are no global
student assertions. A shared admission lock serializes workers; queue plus process
execution has a bounded deadline. `subprocess.run` kills/waits on timeout. Limits:
timeout >0 through30 seconds (default5), at most256 entries per fact list,
128-character printable IDs, at most two request inputs/request8KiB,
bundle512KiB/worker input1MiB/complete result64KiB, and1–256 condition
entries (default128). Exceeding a result limit returns an operational error without
truncating a policy result. No credentials, student inputs or child stderr are logged.

`runtime.CurriculumRuntime(ledger).list_affected_courses(request)` returns a
separate `DependencyResult`: potential transitive prior-completion dependencies,
with source spans and bundle/scope identity. Both all_of and any_of references
are potential graph edges; co-requisites are excluded. This is dependency
inspection, not an eligibility decision. Completeness applies only to the supplied
bundle. Any draft or unresolved rule makes the listing partial, including an empty
listing; it cannot prove that no affected courses exist in the full curriculum.
Unknown input identity or curriculum also remains partial without borrowed rules.
Unsupported operations and operational errors cannot cite dependency facts.
The same synthetic-only execution boundary and resource limits apply.

Test with system Python3.13, no pytest cache and external TEMP/TMP/basetemp:
`tests/test_symbolic_runtime.py`, `tests/test_symbolic_queries.py` and
`tests/test_symbolic_runtime_bundle.py`.
These tests execute actual synthetic Janus calls;
missing Janus is an operational failure, not an implicit passing integration check.
Real-source generated-output human inspection and all institutional release gates
remain outstanding and are not proved by synthetic test success.

## Controlled real-bundle acceptance

`CurriculumRuntime.for_offline_research(bundle, authorization=record)` validates
an exact non-synthetic saved bundle against the current compiler/engine. Its
closed record requires purpose `offline_curriculum_acceptance`, a
`research-...` authorization reference, the exact bundle `content_sha256`, and
one to three explicitly allowed operations from the existing runtime operations.
This is a trusted local research execution record, not authenticated university
permission or a user-facing authorization service. Normal constructors remain
synthetic-only; StudentFacts remains fictional completion/enrollment state.

The same fixed Prolog engine and request/resource bounds apply. Research context
is bounded to8KiB and checked again in the worker alongside the exact payload
hash and allowed predicate. Actual rule data retains synthetic=false; results
use separate offline-research schemas, bundle/research scope, pending human
output-review labels, source holds and institutional_use_allowed=false.
`as_policy_result` and the answer EvidenceBundle reject these observations.
No source, approval, bundle flag or global institutional registry is promoted.

Fresh source-bound JSON -> candidate PL -> checked runtime projection acceptance
is recorded in
[the Phase06 report](../../plans/2026-10-17-phase06-offline-real-runtime-acceptance.md).
Tracked `tests/test_symbolic_offline_research.py` uses fictional institutional
records; actual source-derived outputs and execution evidence remain ignored.
