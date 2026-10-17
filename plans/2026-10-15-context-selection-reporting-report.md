# Offline context-selection reporting — 15 October 2026

Plan9fec57d; first implementation4da6e19, followed by the reviewed metadata fix.
The metadata fix is committed as7456613.
The caller can now build an explicit ranked prefix while inspecting every
offered/deferred primary and its required source dependencies. The original
context builder and runtime engine remain byte-identical to e8ead56/feaa961.
Candidate output is inactive; this does not finish Phase05 or authorize Phase06.

## Delivered behavior

`backend/bintanong_retrieval/context_selection.py` adds the opt-in
`build_context_selection_report` helper. `primary_limit=None` requests all offered
primaries; zero requests none. Invalid limits fail explicitly. Display options
and the exact nested `assembly` are preserved from the existing builder.

Each offered primary retains rank, chunk/version/hash/score, whether requested
and literally emitted, local transitive required IDs, absent dependency rows,
malformed-list markers, unemitted required IDs and original assembly gaps. A
deferred primary may already be emitted as another candidate's required neighbor.
Dependencies are resolved only from that primary's supplied neighbor map; another
offered primary cannot silently repair a missing neighbor. Complete source groups
still fit atomically or receive the original refusal. No field/limitation is
shortened and no budget gap is suppressed.

These fields describe chunk identities. Deduplicated overlapping spans can be
represented without emitting every offered chunk ID. A well-formed dependency
trace is not validated source content, and deferred rows are not certified as
applicable/citable evidence. Every report says `claim_coverage=unknown`,
`candidate_only=true` and `activation_eligible=false`. No query classifier,
automatic prefix choice, temporal rule, authority decision or sufficiency label
was introduced. The longest-gap-free prefix remains an experimental comparison.

## TDD, review and real-data replay

- Initial focused RED: expected missing helper module, exit2. GREEN:87tests/
  87subtests passed1.52s. Synthetic controls cover all display modes, zero/all/
  invalid prefixes, deferred versus refused groups, atomic budgets, local absent/
  transitive/cyclic/malformed dependencies, duplicate/overlapping IDs, invalid
  citations, preserved inputs and unknown coverage.
- One fresh-context review:650independent graph/prefix/budget checks pass;
  reviewer87tests/87subtests pass1.84s. OneP2finding: missing version/hash/score
  raised KeyError after the assembler had returned a valid refusal report,
  including deferred rows. Six requested/deferred combinations reproduced RED.
  The minimal fix preserves absent metadata as null without inventing values;
  GREEN88tests/93subtests pass1.47s. No other findings or second review.
- Initial pre-fix full suite:5303tests/527subtests passed358.45s,6skips/6existing
  warnings. Final post-fix verification is recorded in the closure below.
- Both pre-fix and post-fix replay reproduce **all4,390 saved attempts**, all
  **1,350 default/full-prefix baselines**, **44,986 dependency checks** and all
  **52 distinct contexts**. Context hashes, exact tokenizer counts, emitted IDs,
  original gaps, full evidence payloads/citations and source limits match the
  immutable prior archive. Post-fix replay took118.58seconds; no new embeddings.
- All300preserved input hashes match, including prior manifests, originals,
  vectors, acceptance and exact tokenizer. The unchanged seven prior product/test
  byte hashes are checked separately. Saved source/query wordings are untouched.

At k3/.5/2048 the prior U1 example still needs two primaries to recover its expected
office/payment context; a clean top1 context alone lacks it. U2 still has complete
fee-example evidence with its source-declared neighbors while some extra groups
exceed budget. The wrapper records these facts without deciding claim coverage.
Raw outside-scope/wrong-program/acronym controls remain capable of clean-looking
wrong contexts. No improvement to automatic NLP or engine status is measured.

Raw evidence stays ignored under workspace/audit-evidence/
`p05-context-selection-reporting-20261015/`, including the first run, final-replay,
reviewer probes, RED/GREEN/full logs, preservation inventory and acceptance event.
Do not run writing scripts in sealed roots. No installs, downloads, dependency
changes, model duplication, source conversion, publication or shared writes.

## Review rulings and boundaries

The reviewer set aside source authority/accuracy, actual answer sufficiency,
automatic scope/temporal interpretation, activation and formal exit. Those remain
outside this reporting boundary and are not inferred; ignoring that boundary
could produce unsupported guidance. The reviewer also did not independently
certify the full suite or complete real-data replay. Parent raw execution and
immutable prior-reference comparison supply that bounded evidence; a shared
verification blind spot remains possible. No minor findings were deferred.

The owner-directed evidence location/retention takes precedence over the skill's
transient scratch-directory/cleanup convention. Keep raw evidence recoverable;
only curated text/code/tests are staged. Owner artifact changes stay untouched.

## Accepted next evaluation and phase position

The owner explicitly accepted **all nine T1/T2/U3 wordings and expectations**.
See [accepted proposal](2026-10-15-temporal-unsupported-query-proposal.md) and
[execution plan](2026-10-15-temporal-unsupported-evaluation-plan.md). The exact
pre-acceptance packet hash is
`34529fad525df70d2274f151538ddcecd3bcfb06f50bbc752a6a0ff984d1a5eb`;
the immutable snapshot and actual reply are saved. No repeat acceptance request.
This task has not encoded/scored those questions. Next verify bounded source
labels/assets, then encode only nine new queries against the unchanged27candidate
vectors; preserve all prior accepted12/36 and six/18 cases.

Technical completion estimate remains roughly80% (75–85%range), a planning
judgment rather than a measured completion percentage. This reporting interface
reduces uncertainty but does not close relevance/coverage calibration or final
governance/exit gates. School verification remains pending and does not block
ordinary provisional offline work. F04 remains held; G01/originalG02 unconfirmed;
G03 only confirmed; autonomous-government clause excluded from undergraduate use.
No new college-government files or institutional approval are inferred.

## Final verification

Post-fix full offline suite: **5305tests/533subtests passed324.19seconds**, exit0,
6skips/6existingwarnings (optional GPU checks and existing dependency deprecations/
unknown marker). Command: existing Python3.13 venv, `-B -m pytest tests -q
-p no:cacheprovider --basetemp <new-audit-root>/pytest-fix-full --tb=short`, with
existing offline model/cache environment. No dependencies changed. Final focused
88tests/93subtests and phase-ledger19tests/11subtests pass. Full suite rerun was
justified by the new review fix; no further product changes follow it.

The final replay's4390traces are byte-for-value identical to the pre-fix traces;
all seven prior product/test byte hashes remain unchanged. New helper/tests have
their final hashes in `final-replay/code-digests.json`. Local document links and
whitespace pass. Phase validation succeeds; can-advance remains refused by the
existing blockedPhase05 handoff, as required. Final raw seal details are recorded
in the progress/checkpoint/CLI closure below the following documentation commit.

## Evidence seal

Closure: new36file evidence seal verified read-only, manifest SHA256:
6d324122b23f06666dcb1ad6495f445ba01b30f17ea6bd6c99d2f9a2f7facb7f.
Phasevalidate0/canadvance1(expectedblocked), whitespace/local links pass. Raw
sealed scripts must not be rerun in place. Product7456613 complete; parentSHA
precedes following documentation commit. Owner artifacts remain unstaged.
Next accepted-nine evaluation plan; no new encoding/activation/Phase06.
