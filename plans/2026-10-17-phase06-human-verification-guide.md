# Phase06 human verification and earlier testing practices

Reviewed17October2026 at f2f4fd6; product49bc993 unchanged. This is a targeted
review of earlier handoff evidence and selected test implementations, not a
fresh rerun or exhaustive audit of Phases00-05. The two concurrent Docker edits
remain untouched. Repository handoff/reminder and verify-and-stop workflows apply.

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
3. Continue the five remaining generated mappings using the linked source-to-code
   REVIEW. Check oldCS1/L's draft dependency and the four unknown targets. Missing
   completion differs from failed completion; conflicting facts stay unknown.
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
research only. These command lines are assembled from the already-run acceptance
script, not claimed as a new run in this review. No installs or models required.
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
