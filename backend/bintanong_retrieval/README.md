# Retrieval debug interface

This module implements master-plan section 10 without generating an answer. The trusted internal caller supplies a pinned release and canonical scope/entity/version hints. Unknown scope is an empty tuple; the retriever never infers a curriculum or college.

```powershell
python -m backend.bintanong_retrieval --query 'What does the policy say?' --release-id release-example --scope program:EXAMPLE --top-k 5 --context-budget 2048 --asset-manifest C:/Coding-projects/bintanong_workspace/audit-evidence/p05-20261012/embedding-assets.json
```

The asset manifest is external JSON mapping model-relative filenames to their expected SHA-256. Model files must exist below `MODELS_DIR` (default `C:/Coding-projects/MODELS`). The encoder verifies assets, uses the matching SEA-LION Retrieval instruction once, loads local files only, refuses token overflow and never uses the legacy adapter's mock fallback. System Python currently lacks the model libraries; no installation is performed by this command.

Storage uses `SUPABASE_URL` and `SUPABASE_ANON_KEY` through the existing client. Every read/RPC uses its runtime role. Apply `20261012013339_phase5_retrieval_snapshot.sql` before retrieving a published release. The RPC is STABLE/SECURITY INVOKER and carries one statement snapshot: active pin, encoder fingerprint, candidate scores, source spans, source versions and required neighbors. Publication between embedding and the RPC returns `release_changed`; callers must obtain a fresh authorized pin and retry. Superseded releases remain hidden by existing RLS.

Scope tags match the exact stored `chunks.scope`: for a known scope every chunk tag must be in the supplied tags; global chunks have no tags. Canonical entity hints match any requested value in `chunks.type_fields.entity_hints`; they are metadata checks, not another retrieval architecture. `--document-version` restricts exact active-release versions. An unknown entity yields no match.

Required adjacent clauses are explicitly listed in `chunks.type_fields.required_neighbor_chunk_ids`. The RPC supplies only authorized same-version neighbors. The assembler includes the whole dependency group, including citations, or exposes a missing-neighbor/budget gap. It never truncates clauses. Span overlap identity uses source hash/version/page/locator/bbox/text rather than chunk-specific span UUIDs. Textless table spans retain their table/cell locator and use the table chunk text.

The versioned `bintanong-retrieval-debug-v1` JSON contains configuration fingerprints, raw cosine similarities (not probabilities), evidence/citations, serialized context and its exact token count. It is an internal envelope; public Phase 01 contracts remain unchanged. It can preserve conflicting source editions instead of forcing them into the existing public `RetrievalResult`, which rejects multiple editions.

| Status | Meaning |
| --- | --- |
| `release_changed` | The requested release is absent, draft or no longer current; no evidence returned. |
| `configuration_mismatch` | Query and stored encoder configuration differ; no evidence returned. |
| `encoder_unavailable` | Local assets/dependencies cannot be verified/loaded. |
| `invalid_query` | Query/vector/token counting is invalid or encoder context would overflow. |
| `insufficient_evidence` | No complete relevant evidence, or required context/citation/budget gaps. |
| `needs_scope` | Multiple plausible curriculum versions need caller clarification. |
| `conflicting_sources` | Competing editions are retained for review; score does not choose authority. |
| `uncalibrated` | Context is available but development relevance/coverage approval is pending. |
| `storage_error` | The runtime storage call failed; no administrative retry. |
| `ok` | A configured development policy accepted complete context; institutional approval is separate. |

Exit code 2 exposes an open retrieval gate. The default policy stays `uncalibrated-v1`; a synthetic threshold is never installed as institutional calibration. No endpoint, API service, LLM answer, candidate publication or institutional activation is introduced.

An internal opt-in `SourceAwareEvidencePolicy` can be supplied through
`RetrievalEngine(..., evidence_policy=policy)`. Prepare it with explicit pinned
release/set IDs and complete trusted candidate chunks/catalogue/source reviews.
Then call `retrieve(request, subject_id=..., requested_claims=(... ,))` with exact
trusted intent. The engine binds actual RPC rows, checks conflicts before subject
selection, assembles complete groups and assesses only its actual emitted IDs.
Original source payloads are validated before private transport projections are
derived; source packaging and DB-only identifiers do not hide changed facts.

Opt-in calls return `bintanong-retrieval-debug-v2`, a policy/snapshot fingerprint,
assessment or an explicit not-run reason, and root candidate/inactive/unverified-
authorization flags. Missing claims force `insufficient_evidence`; unknown claims
stay `unassessed`; available reviewed fields stay `uncalibrated`, regardless of a
caller-selected settings policy name. Answer sufficiency stays unassessed. Shared
citations/group display use the original exact token budget. No-policy calls
retain the exact v1 behavior; supplying intent without a policy is invalid.

The engine also verifies that reviewed fields survive rendering. Validated marked
records use the existing whole-field renderer; generic records require literal
field/span text and its source locators in the emitted evidence. Otherwise the
claim reports `reviewed_fields_not_in_context` with `unverified_rendered_fields`.
An emitted footnote alone cannot establish field availability. Malformed version
transport objects are rejected before citation assembly.

This injected research snapshot is not an authorized release loader. Matching
release IDs do not establish membership/currentness or institutional approval.
There is no CLI/public exposure, administrative storage fallback, automatic
subject/claim recognition or activation. See
`plans/2026-10-16-source-aware-retrieval-policy-design.md` and its implementation plan.

Development measurement:

```powershell
python -m evaluation.retrieval --cases evaluation/retrieval-dev-synthetic.json --observations C:/path/outside/git/retrieval-observations.json --output C:/path/outside/git/retrieval-evaluation.json
python -m unittest discover -s tests -p 'test_retrieval_*.py' -v
```

Observations come from separate retrieval runs. The committed fixture uses manual unit vectors and labeled synthetic database chunks; it tests mechanics, not SEA-LION quality. The evaluator compares k=3/5/8, uses `hits/k` for Precision@k and `hits/gold_count` for Recall@k, separates language/category, and rejects final-split tuning. Ranking metrics alone cannot pass the approved source/citation exit gate. See `plans/phase-05-retrieval-report.md` for measurements and limits.

The optional offline `context_selection.build_context_selection_report` wraps the
existing assembler with an explicit caller-selected `primary_limit` (None: all;
zero: none). It does not choose a prefix or change the engine. Pass the same
candidate list, budget, exact token counter and optional display flags as to
`build_context`; the unchanged result is under `assembly`.

Its `context-selection-report-v1` envelope records offered primaries in rank
order, requested/deferred IDs, literal emitted IDs, source version/hash/score,
local transitive required IDs, absent neighbor rows, malformed dependency lists
and the original assembly gaps. A deferred primary may already be emitted as
another primary's neighbor. Unemitted IDs may also reflect span deduplication;
they do not prove missing information. Deferred rows are not certified as valid
citations or applicable evidence. Duplicate offered IDs retain their ranks;
emission and gaps describe chunk identities rather than individual attempts.
Missing version/hash/score metadata remains null in the trace; it does not hide
the assembler's invalid-citation refusal or prevent reporting deferred rows.

Every report is candidate-only, activation-ineligible and has
`claim_coverage='unknown'`, even with nonempty gap-free context. This diagnostic
does not establish relevance, source authority, audience, recency or answer
sufficiency. Required groups remain atomic; source limits and citations are not
removed to fit a budget. See
`plans/2026-10-15-context-selection-reporting-plan.md` for the bounded workflow.

The separate offline `candidate_subject` helper prepares a source-bound subject
catalogue from complete chunks and explicit researcher assignments by `reading_id`,
`subject_id` and `basis_ref`. It never reads a query or gold labels. A selection
requires an explicit trusted canonical subject; missing/unknown subjects return
no IDs. Current chunk payloads, provenance and dependency membership must match
the catalogue. Assigned rows require undergraduate applicability metadata, and
every declared dependency must share the subject. Unassigned rows stay visible.

The catalogue digest detects accidental changes, not forged researcher input.
Callers must keep this preparation boundary trusted. Checks validate metadata
bindings only, not human approval, citations, source authenticity or requested
claims. All results stay candidate-only/inactive with unknown claim coverage;
subject matches do not verify a deadline, current year or payment method.
The engine, SQL filters, public contracts and curriculum selectors are unchanged.

`candidate_claims.build_candidate_claim_report(catalogue, chunks, *, subject_id,
requested_claims, emitted_chunk_ids)` is a separate opt-in offline report.
Trusted caller claim strings match existing unresolved
`source_limits[].affected_claims` exactly. A match reports `not_established`;
unmatched claims stay `unassessed`. No affirmative support outcome exists, and
empty claims cannot establish coverage. A subject or assembled context alone
does not answer a claim. The helper never consumes benchmark expectations.

Source limitations are inspected across the selected subject snapshot even when
their chunk was not retrieved. Copied limit records identify the source chunk and
whether its literal ID was supplied as emitted; those IDs do not certify emitted
text/citations. Missing context IDs mean unknown emission, not empty context.
The existing subject catalogue validates complete current payload bindings.
Malformed limitations and unknown/duplicate context IDs are rejected. Missing
subjects/claims and unknown subjects remain explicit; no runtime gate, source
content verification, NLP inference or institutional activation is implemented.

An optional `claim_reviews` register prepared by `prepare_candidate_claim_reviews`
extends this same helper with a v2 report. Each trusted researcher finding binds
the complete selected subject snapshot, a source-audit reference/hash and either
existing reviewed field references or a `not_stated_in_selected_fields` finding.
The digest checks integrity, not reviewer identity or source truth. Do not use
benchmark expected labels to manufacture these findings.

Visible fields require nonblank values, review-event metadata and matching source
spans. `reviewed_fields_available` means that those fields and their transitive
required chunks occur in the supplied context IDs; missing or unknown emission
remains explicit. Answer sufficiency stays unassessed. Existing exact source
limitations override positive field findings; unreviewed claims stay unassessed.
Selected-field absence is never a university-wide absence or policy prohibition.
Without this opt-in register, the v1 report is unchanged.
