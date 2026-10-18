# Phase06 human verification and earlier testing practices

Updated18October2026 after the owner's partial CSV review; product49bc993 unchanged.
The earlier-phase section is a targeted historical review, not a fresh audit of
Phases00-05. The two concurrent Docker edits remain untouched.

## What Phase06 needs from the reviewer and developer

The [previous developer's delivery](2026-10-17-phase06-prolog-review-delivery.md)
asked for a source-to-generated-rule check: does the generated prerequisite mean
what the original prospectus and settled reviews say? It did not require the owner
to certify Python/Janus behavior by grading every technical CSV row.
The [scaffold](2026-10-17-phase06-hawksprey420-scaffold-handoff.md) carried that
pending output review to this machine; it did not turn test metadata into policy.

Use these two questions:

1. **Reviewer:** Is this the correct course/curriculum and prerequisite meaning
   shown by this exact original row? Confirm genuine unresolved source content;
   flag a generated expression that changes an already accepted meaning.
2. **Developer:** Does the compiler preserve that meaning, and does the engine
   give the correct result or explain why it cannot check? Prove this with tests,
   request/result evidence, source bindings and reproducible bundles.

The thesis motivates prerequisite checks, affected-course reasoning and deterministic
answers. Master sections1.3/11 make the practical requirements explicit, including
unknown versus proven failure. This CSV is component evidence, not the thesis's
complete end-to-end evaluation or an official enrollment determination.

## The CSV categories as developer tasks

| Category | Plain question and engine consequence | Who supplies the evidence? |
| --- | --- | --- |
| matrix | For the reviewed rule, do both/one/no passed prerequisites give the right result? A wrong result is a reasoning defect. | Reviewer checks source meaning; developer tests combinations. Existing48 ok verdicts stand. |
| missing-completion | A required completion was not supplied. Return unknown, not a guessed failure or pass. | Developer tests missing input; owner has already accepted six such rows. |
| conflicting-completion | The same course is both passed and failed in one request. Return unknown with a conflict. No retake policy is inferred. | Developer tests contradictory input; owner has already accepted six such rows. |
| unknown-not-none | The prerequisite rule is absent/unresolved, or the course identity is draft. Do not treat that as verified no prerequisites. | Developer proves the guard. Reviewer only resolves genuinely missing source content; settled blank readings stay settled. |
| potential-dependencies | Which later courses have reviewed prerequisite paths from this course? This is a partial dependency list, not blanket ineligibility. | Developer checks graph paths against already reviewed relationships. Ask the reviewer only about a new/ambiguous relationship. |
| wrong-curriculum | The request names an unrecognized curriculum. Return unknown instead of borrowing this bundle's rules. | Developer tests scope isolation. No new university rule needs approval. |
| unknown-course | The request uses course-unknown. Return unknown rather than approve an empty prerequisite list. | Developer tests recognized identity. H39/H70's CC5/L display label is misleading; use the saved actual request. |
| unsupported | The operation is unregistered. Return unsupported rather than execute an arbitrary goal or invent a decision. | Developer tests the operation registry. This is not a policy prohibiting a course. |
| determinism-first | Run the identical request twice with the same bundle. Decision, reasons and provenance must agree. | Developer compares both results. The first exported row alone cannot prove repetition. |
| timeout | Deliberately exceed the execution budget. Return runtime_timeout, then recover for a normal request. | Developer verifies timeout/recovery logs. It is not a failed prerequisite. |

Technical rows may remain ungraded by the owner while verified developer evidence
is recorded separately. Do not convert those blanks into owner acceptance or treat
them as a requirement for the owner to approve implementation mechanics.

Developer verification18October:the unchanged acceptance script was copied into
ignored workspace/audit-evidence/p06-developer-checks-20261018 and rerun against
the current code. All73 recorded BSCS cases, four concurrent/version-isolation
checks and39 native spans passed. The script also asserts identical repeated
results and timeout recovery for both versions. Prior sealed artifacts and the
owner's returned CSV remain unchanged. Docs/phase551 passed/11 subtests17.49s.
This proves the current engineering checks; it does not fill owner verdict cells
or approve unknown source content/institutional release.

## Which fields actually affect the engine?

| Field or record | Actual role |
| --- | --- |
| Applicable curriculum/course IDs, operation, prerequisite expression, completion facts | Runtime inputs that determine which supported check is evaluated and its scoped result. |
| Authoring review_state and rule coverage | Software gates: draft identity or unresolved rule can prevent a conclusive result. These are not university prerequisite conditions. |
| Source spans/hashes, bundle hashes, execution authorization | Provenance/integrity and execution controls. They establish what data/code can be used; they are not additional passed-course requirements. Developers verify them. |
| CSV case/test_id, expected, automated_check | Test-report labels and comparisons. The engine does not read them as policy. |
| CSV observed, reason, error_code | Exported engine outputs to inspect, not independent authoring inputs. |
| CSV review_status, reviewer, reviewed_at, reviewer_notes | Human annotations. Editing them does not update authoring review_state or import/activate a rule. |

The [bundle builder](../backend/bintanong_symbolic/bundle.py) explicitly projects
authoring review_state into the engine's reviewed boolean. The
[Prolog completion check](../backend/bintanong_symbolic/curriculum_runtime.pl)
checks that boolean before passed/failed facts. This explains H27-H32:
CS1/L requires CC1/L is already accepted, but the referenced CC1/L identity is draft.
The returned identity_unreviewed is a preparation limitation, not a PalSU condition
that CC1/L is impossible to pass. The owner's desired pass/fail behavior is recorded.
Developer action: locate the exact pending source record and show only its unresolved
identity question; bind actual review evidence, regenerate and rerun affected cases.
Do not remove the guard, infer verified_none or ask again about the settled edge.

## Use the returned review

[Intake](2026-10-18-phase06-owner-runtime-review.md):48 affirmative, three no,
22 without a verdict; H30-H32/H41 also have comments. Preserve the original file.
Do not require the owner to redo accepted rows or fill technical verdicts just to
complete a spreadsheet. Keep source decisions, developer checks and release gates
separately attributable. Remaining output review is scoped to the actual mappings
and consequential source gaps, not certification of every audit column.

## How the earlier work was tested

| Phase | Recorded method | What that does not establish |
| --- | --- | --- |
| 00 infrastructure | Compose rendering, health probes, model hashes, synthetic PDF/CLI checks | Current machine/service readiness; these historical claims were not rerun here |
| 01 governance/contracts | Broad pytest, synthetic traces, adversarial and mutation checks; original/cache hash comparisons | Source authority or a real final benchmark; its handoff explicitly reports zero verified final cases |
| 02 ingestion | Candidate validation, integrated smoke tests, source spans and prospectus review tooling | All-original accuracy; the later corrective audit disputes the unqualified completion claim |
| 03 embeddings | Adapter/batch contracts, dimension/normalization/fingerprints, selected similarity tests | The inspected similarity test checks finite scores, without asserting positive outranks negative; the adapter permits mock fallback |
| 04 storage | Actual roles/RPCs in uniquely named disposable databases, failure/concurrency/security checks, local/hosted inspection | An approved or active institutional corpus; synthetic authorization state is test data |
| 05 retrieval | Saved actual vectors, source/hash/citation audits, accepted questions, offline ranking/context results | Calibrated student answers or university authorization; owner explicitly accepted an offline research/software milestone |

Evidence: [Phase00 handoff](phase-00-handoff.md), [Phase01](phase-01-handoff.md),
[Phase02](phase-02-handoff.md), [Phase03](phase-03-handoff.md),
[Phase04 corrective verification](phase-04-handoff.md), [Phase05](phase-05-handoff.md).
Read the [Phase1-2 corrective audit](2026-10-12-phase12-progress-claims-audit.md)
with the historical completion labels. The specific Phase03 inspection is
`tests/test_embedding_offline_similarity.py::OfflineSimilarityTests.test_multilingual_queries_rank_matching_policy_above_hard_negative`
and `backend/bintanong_embedding/adapter.py` load/encode fallback behavior.
That is a bounded evidence gap, not an exhaustive Phase03 implementation audit.

Earlier human reviews used exact original regions, short plain-language batches,
actual owner answers and content/hash-bound receipts. Phase06 reviews01-03 already
followed this process. Do not repeat their source/logic approval questions.

## Review Phase06 now

Open the ignored worksheet:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p06-human-verification-20261017/REVIEW.md`.
It decodes all73 existing observations into printed course codes and fictional
passed/failed inputs. It links original crops and exact generated PL expressions.
No source material, original sealed output or code was changed to prepare it.

1. Start with oldCC5/L: H01,H03,H05,H07,H09,H10. Compare the original row,
   already-approved both-required meaning, generated oldPL line32 and outcomes.
2. Review proposedCC5/L: H43,H45,H47,H49,H51,H52. Compare the proposed source,
   generated proposedPL line27 and outcomes. The second required course is CS2.
3. Use the linked source-to-code REVIEW for the remaining generated mappings;
   reuse actual returned verdicts. Developers verify draft/unknown handling and
   completion edge cases; show the owner only unresolved source-content questions.
4. Give matches/mismatch/unsure with the inspected IDs. A partial batch verdict
   does not approve the entire bundle. For mismatches, identify the output/source
   location; correct structured authoring and regenerate rather than edit PL.
5. After an actual answer, record reviewer/date, exact inspected outputs/hashes,
   scope and actual wording in a new receipt/checkpoint. No human receipt or
   approval has been created by preparing this worksheet.

This is the human check of generated artifacts and representative runtime
behavior. The automated73 cases,854 regressions and source-span checks are
engineering evidence, not your human verdict. Do not enter real grades or invent
numeric passing policy; fictional completion states suffice. No chat website,
LLM routing, transcript upload or frontend is required for Phase06 verification.

## Optional fresh rerun without overwriting sealed evidence

The saved accept.py writes under its own directory. Run a copy in a new ignored
folder; it reuses the same BSCS authoring inputs and APIs. From PowerShell:

```powershell
Set-Location C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p06
$reviewRun = Join-Path 'C:/Coding-projects/bintanong_workspace/audit-evidence' ('p06-human-rerun-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $reviewRun -ErrorAction Stop | Out-Null
Set-Content -LiteralPath (Join-Path $reviewRun '.gitignore') -Value '*' -Encoding utf8
New-Item -ItemType Directory -Path (Join-Path $reviewRun 'tmp') | Out-Null
$env:TEMP = Join-Path $reviewRun 'tmp'
$env:TMP = $env:TEMP
Copy-Item -LiteralPath 'C:/Coding-projects/bintanong_workspace/audit-evidence/p06-real-runtime-20261017/accept.py' -Destination (Join-Path $reviewRun 'accept.py')
py -3.13 -B (Join-Path $reviewRun 'accept.py') 'C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p06'
Get-Content -LiteralPath (Join-Path $reviewRun 'ACCEPTANCE.md')
```

Expected summary:73 cases,4 concurrent checks,39 native spans, passed offline
research only. The command pattern was exercised again on18October at the
developer evidence root above. No installs or models required.
The current two full-suite Docling dependency failures are separate from this
authoring JSON -> PL -> Janus path; see the [acceptance report](2026-10-17-phase06-offline-real-runtime-acceptance.md).

## Meaning of the blocked handoff

Human output review, scoped software completion and institutional release are
separate decisions. Your review can confirm generated-output fidelity. It cannot
substitute for issuing-office/source-authority evidence or activate rules.
The Phase05 offline completion was an explicit owner scope decision, not an
automatic consequence of passing tests. The same kind of qualified Phase06
closure would need its own explicit exit criteria/owner decision; none is assumed.
University release holds do not prevent the already-authorized offline tests or
this human inspection. The current [blocked handoff](phase-06-handoff.md) stays
unchanged until actual review and the applicable completion boundary are settled.
