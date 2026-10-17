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
compilation/release gates, Janus, request-local student facts and safe registered
operations remain future Phase06 increments. Do not use the preview for decisions.

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
