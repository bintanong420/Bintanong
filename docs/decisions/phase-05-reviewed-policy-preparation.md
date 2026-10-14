# Separate inactive reviewed policy readings

13 October 2026, Phase 05 recovery specification:
`plans/2026-10-13-reviewed-policy-correction-selection-spec.md`.

The strict raw readers preserve extraction refusals; source contracts separately
govern verification, review and approval. Owner page comparisons therefore feed
a separate preparation bundle through
`backend/bintanong_tools/document_ingest/reviewed_policy.py`, rather than altering
raw conversion, existing canonical candidates or source-register states.

`build_reviewed_policy_bundle(readings, sources=..., review_events=...)` is pure.
Sources and review events are SHA256-to-bytes mappings. Normalized readings name
the source/version, intended audience, applicability and its evidence reference,
field originals/reviewed values/locators/decisions/event references, source gaps,
and preserved artifact references. Structured values are copied intact. This
keeps full service associations, role fragments, fee parent provenance and
flowchart arrows beside the original evidence. Empty strings stay literal
source blanks; unknown values may stay null and acquire no inferred meaning.

The builder checks supplied source/event digests, source binding, explicit field
decisions, physical-page locators, gap field/claim references and retained evidence
references. An accepted transcription never approves another field. Callers must
compare each normalization mapping against the actual review's displayed scope;
event hashes prove bytes, not that arbitrary values have human approval. The
builder is a preparation validator, not an approval authority or source verifier.

Audience partitioning uses explicit declarations, not keywords in staff role
labels or shared source headings. Unknown/mixed audience or applicability stays
unresolved; excluded audiences stay in the exclusion accounting. Explicitly
reviewed undergraduate applicability permits only preparation selection. Every
bundle remains `candidate_only=true`, `activation_eligible=false`, with no chunks,
SourceSpan creation, database writes, executable rules or governance transition.

Known gaps bind to affected fields and claims even when visible wording has been
accepted. Later chunk/retrieval integration must carry those limits through its
own governed implementation. Selected bundle counts describe supplied readings,
not an exhaustive handbook/Charter audit or corpus accuracy.

Initial synthetic TDD: fourteen new unittest cases fail on the absent builder,
then all fourteen pass using system Python 3.13.7. Tests cover preserved inputs,
corrections/blanks/refusals, stale hashes/wrong sources, partial field review,
source cutoffs, excluded/unknown scope and complete service associations. Raw
logs stay under workspace `audit-evidence/p05-reviewed-policy-consolidation-20261013/`.

Actual-event compatibility adds explicit `source_hashes` and
`owner_statement_excerpts` forms, preserving the original correction/clarification
bytes. A reviewer reproduced JSON numeric overflow (`1e999` decodes to infinity);
the focused regression fails before validating decoded event finiteness and
passes afterward. Seventeen final unit tests pass; relevant ingestion, canonical,
source, governance and documentation regressions: 1193 passed, one skipped,
12 subtests, 55.80 seconds. Original readers/canonical contracts remain untouched.
