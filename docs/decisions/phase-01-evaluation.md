# Phase 1 evaluation protocol: split and group validation, rubrics, development examples

Status: implemented as code and synthetic data. This record approves no source, curriculum, edition or benchmark. Every committed case is synthetic. The final set is empty and the coverage target is not met.

## What is built

All of it lives in `evaluation/` and is exercised by `tests/test_evaluation_*.py`.

| Part | File | Role |
|---|---|---|
| Case schema | `evaluation/case.schema.json`, `evaluation/case.py` | Structural JSON Schema plus a strict checker for cross-field rules. Routes, controls and the five symbolic outcomes are read from the governance vocabulary through the contracts package, not retyped. |
| Split and group validation | `evaluation/protocol.py` | Derived splits, leakage, near-duplicate, freeze, prompt-example and coverage checks. Pure functions with canonical JSON output (sorted keys, LF). No command line. |
| Rubrics and scoring | `evaluation/rubrics.py` | Five machine-checkable rubrics, a deterministic scoring function over a case and a system output, a summary by category and language, and the `RunRecord` shape. |
| Development examples | `evaluation/cases/dev/`, `evaluation/examples/` | 21 synthetic development cases and one worked synthetic traceability example. |

### Case

A case records its id, group id (scenario family), category (enrollment, prerequisites, grades, academic_standing, discipline), language (en, tl, taglish), query, adversarial kinds, applicable scope (or null with a reason), expected route or control, the five-outcome result when relevant, required and missing facts, gold spans and rules, acceptable claims, whether the system must abstain, split, status and review evidence.

- Status is `synthetic`, `candidate` or `verified`.
- A synthetic case carries no gold spans or rules and no review evidence, states its invented rule in `synthetic_policy`, and belongs to the dev split only. It cannot be marked verified.
- A verified case needs gold spans, an applicable scope, and all of reviewer, evidence reference and review version. The reviewer must differ from the author (compared after trimming and case folding).
- Gold spans hold the source version id, the byte digest, the page, a locator and a digest of the passage. The passage text stays outside Git.
- Exactly one of route and control is set. An outcome needs a Symbolic or Hybrid route, and a Symbolic route needs an outcome. `unknown`, `unsupported` and `error` must abstain; `eligible` and `ineligible` must not.
- Closed adversarial kinds: ambiguity, negation, missing_facts, wrong_edition, conflicting_evidence, unknown_course, incomplete_coverage, unsupported_operation, operational_failure. All of them except negation require abstention; missing_facts needs a missing-facts list; unsupported_operation needs outcome `unsupported` or control `unsupported_scope`; operational_failure needs outcome `error` or control `evidence_unavailable`.
- Text containing an email address or a run of nine or more digits is refused as a possible private identity.

### Set validation

- Every group belongs to one split, and the split is derived from the group id and a salt, so case content and insertion order never decide it and adding cases never moves a group. A case whose split differs from the derived one is a finding.
- A group present in both splits, or spanning two categories, is a finding.
- Two cases in different groups whose normalised query token sets overlap at or above the threshold are a finding. Normalisation is Unicode NFKC, case folding and word tokens.
- A gold span of a verified case must name a version in the supplied source registry with the matching byte digest. With no registry, no verified case resolves.
- A freeze record stores the sorted final group ids, a digest per final case, the salt and an overall digest. Against a freeze record, a moved group, an edited, missing or added final case, an added final group, a changed salt and a tampered record are each a finding. Freezing refuses an empty set and any final case that is not verified and source-resolved.
- A final case's query or acceptable claim, exactly or nearly, inside a prompt or few-shot example list is a finding. Development text may be reused.
- Coverage counts only valid, verified, source-resolved final cases. A claim of coverage is recomputed and any disagreement is a finding.

### Rubrics

Route, evidence, symbolic result, answer and unsupported claims, each scored 0 or 1 (or not applicable). The rule everything rests on: `unknown`, `unsupported` and `error` are never an approval and never a denial. Only `eligible` counts as approval and only `ineligible` as denial.

- Approving when the gold outcome is not `eligible`, or denying when it is not `ineligible`, is a critical flag (`false_approval`, `false_denial`) and zeroes the case total.
- Abstaining when the gold outcome is determinate is `false_abstention` (flagged, not critical).
- An error or operational failure converted to an approval or denial is `error_as_policy` (critical).
- A claim that is not one of the case's acceptable claims (normalised exact match) is an unsupported claim (critical).
- A Symbolic or Hybrid expectation answered by the RAG route is flagged as `silent_rag_fallback`.
- Malformed cases or outputs raise rather than score.

`RunRecord` holds code version (full commit), prompt version, model id and revision, quantization, embedding configuration, knowledge release id, rule bundle version, decoding parameters, evaluation set version and the grouping digest. A missing field, an unknown field or a floating model or embedding revision is refused; the pinned-revision rule is the contracts package's own.

## Strict defaults (owner-reviewable)

| Default | Value | Where |
|---|---|---|
| Near-duplicate threshold | token-set Jaccard 0.8, inclusive | `NEAR_DUPLICATE_THRESHOLD` |
| Split salt | `bintanong-eval-split-v1` | `SPLIT_SALT` |
| Share of groups derived to final | 30 of 100 buckets | `FINAL_PERCENT` |
| Coverage target | 10 verified final Taglish cases per category and 50 in total | `TARGET_PER_CATEGORY`, `TARGET_TAGLISH_TOTAL` |
| Claim matching | normalised exact text | `rubrics.score_case` |
| Axis scores | 0 or 1; total is the mean of applicable axes, forced to 0 by a critical flag | `rubrics.score_case` |

Changing the salt or percentage re-derives every split, so it is only possible before a freeze; a freeze records the salt and a different salt is a finding.

Limits worth knowing: the near-duplicate check is lexical, so an English and a Tagalog variant of one scenario share few tokens and stay together only because the author gave them one group id. Because the split follows the group id, an author could pick a group id to land a case in a chosen split; reviewers should treat group ids as assigned before the case text is written.

## Coverage status

`NOT MET: 0 verified final cases, 0 Taglish (target 50 Taglish, >= 10 per category: enrollment 0/10, prerequisites 0/10, grades 0/10, academic_standing 0/10, discipline 0/10)`

The validator prints this line from the data and refuses to pass a claim that disagrees with it. There is no final-split case of any status. The 50-case target is blocked on source-backed independent review and on owner-authorized sources: no source version is approved, so no gold span can resolve to a registered source. The 21 development cases are synthetic, test the machinery only, and say nothing about institutional policy. The traceability example is a synthetic illustration; the real source, chunk, rule and case binding is Task 4.

## Owner decisions, listed and not decided

1. Who the independent reviewer is, and what counts as independent beyond a different name (role, office, no authorship of the rule).
2. The near-duplicate threshold, and whether to add a cross-language check.
3. Taglish phrasing guidelines for authors, and a native-speaker check for Taglish and Tagalog wording.
4. Whether English-only verified cases count toward the 50, or toward the per-category ten.
5. Where private evaluation evidence (gold passages, reviewer notes, run outputs) is stored outside Git, and who can read it.
6. The freeze procedure and timing: when the final set is sealed, who runs `make_freeze`, and where the record is kept.
7. The final share (30 percent) and the salt.
8. How claim wording is adjudicated beyond normalised exact match, and who owns that adjudication.

## Not done

- No verified or final case exists; none was created.
- No run was scored against a real system; the scoring function is exercised only by unit tests.
- Gold spans are not checked against a real source register; the registry is a supplied mapping.
- The checkpoint and the other Phase 1 records were not changed by this work.

## Task 6 SPEC fix pass

Three Medium findings were reproduced and fixed at the shared protocol boundaries; no High finding was reported.

- Final query or acceptable-claim text embedded in a long prompt now triggers leakage before the whole-example Jaccard heuristic. Containment uses the existing NFKC/case-folded word-token convention in original word order, with whole-word boundaries; Unicode whitespace and punctuation follow that convention. A word inside another word, or reordered words in long unrelated context, does not count as literal containment. The existing near-copy heuristic remains. Long paraphrases without a matching normalized sequence still require reviewer checks; this is a lexical guard, not semantic authentication.
- A verified case's non-null declared scope.version_id must equal every supporting gold span's version. The existing gold-span registry/digest checks then resolve that declared version. A registered but unrelated version and mixed gold versions under one declared version are refused; those cases cannot count toward coverage or be frozen. This is a strict default for ambiguous multi-version applicability. A null scope.version_id remains allowed by the existing schema, including multiple registered gold versions, with applicability left to the author/reviewer declaration. A hash-only registry cannot authenticate institution, edition, issuer or reviewer identity, and this pass invents no such metadata or policy.
- Duplicate case-id findings now originate in the shared case check. Every occurrence of a repeated id, including a conflicting or malformed copy, is excluded from coverage; duplicates cannot inflate independent-case totals or produce a false MET claim. make_freeze rejects duplicate ids anywhere in its supplied set, including development rows, instead of silently collapsing them into one digest. Set validation retains its duplicate findings.

TDD: the new protocol regressions first gave 9 failed and 32 passed (exit 1): four long-context leakage variants, three declared-version/ambiguity inputs and two duplicate-coverage/freeze inputs. The focused protocol run then passed 41 checks; all evaluation tests passed 229 checks, exit 0. Twelve targeted critical-guard mutants were applied only to scratch copies: disabled literal containment, removed word boundaries/order/case folding, removed or weakened scope association, restored invalid scope coverage, disabled duplicate exclusion/counting/findings/freeze refusal, and bypassed registry digest resolution. All twelve were killed; no survivor remained. Tests and mutation logs remain outside source evidence; no real verified/final case or source approval was added. The committed development corpus still has zero verified final cases and coverage NOT MET.

Fresh full-suite verification after the fixes: 3991 passed, 1 skipped, 8 warnings and 13 subtests in 136.05s, exit 0; prospectus self-test 80/80. The original three review reproducers are now rejected. Docs hygiene passed 56 checks. Protected packages/dependency files have zero diff, the owner checkout's nine status entries are unchanged, and independent Standards review follows this fix pass.
