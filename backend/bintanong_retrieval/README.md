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

Every report is candidate-only, activation-ineligible and has
`claim_coverage='unknown'`, even with nonempty gap-free context. This diagnostic
does not establish relevance, source authority, audience, recency or answer
sufficiency. Required groups remain atomic; source limits and citations are not
removed to fit a budget. See
`plans/2026-10-15-context-selection-reporting-plan.md` for the bounded workflow.
