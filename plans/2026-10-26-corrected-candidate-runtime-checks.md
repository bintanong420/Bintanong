# Corrected candidate runtime checks

**Goal:** compose the existing corrected78-chunk candidate with its trusted context budgets and run a
bounded six-question quality check. No new pages/topics,chunks,embeddings,activation or prompt changes.
**Approved baseline:** Phase11/master16,completed80-ID audit and correction results;owner “ok proceed
then”26Oct after disclosure that runtime wiring/query checks remain. Existing limits remain binding.
**Execution:** inline TDD in existing p11;new source-derived artifacts ignored under workspace
audit-evidence/p11-corrected-runtime-20261026/. Existing active19 and draft80/corrected78 unchanged.

## Architecture and acceptance

Use optional trusted package `subject_context_budgets` as the complete explicit per-subject budget map.
If absent,retain current pre_enrollment4096/default2048 behavior. Reuse RetrievalEngine validation,
copying and subject checks. Bind an explicitly supplied map into the root research release identity;
changing that config must not change symbolic rule-bundle versions or silently reuse a pin.
The field is researcher package input,never an HTTP/student/router field. Corrected candidate loads
the already-saved map academic_misconduct3072/pre_enrollment4096. No active pin-file change.

## Tasks

1. [x] Add synthetic factory regressions in tests/test_runtime_multi_curriculum.py:complete3000-token
   group admitted with explicit package budget,legacy budget still withholds;single/multi wrappers;
   invalid/unbound maps reject;budget-only change gets a new root without changing curriculum rules.
   Observe expected RED before editing backend/bintanong_runtime/research.py.
2. [x] Minimal factory change;GREEN relevant tests including engine budget/identity/catalogue tests.
   Independent final review before completion;repair any important findings with focused regressions.
3. [x] Compose actual corrected package with saved budget map,verify complete selected groups through
   real retrieval/context assembly. Preserve corrected package and all three hosted releases unchanged.
4. [x] Run the frozen six actual-model cases below once each through normal router/retrieval/generator/
   review/guards. Canonical references,768 output cap,prefix reuse,current resident model/settings.
   No retry sweep,prompt edits or automatic activation on schema success. Record actual answer quality.
5. [x] Full tests/ suite with shared Python3.13,-B,-p no:cacheprovider,external basetemp/evidence.
   Serialize full suite and actual-model calls to avoid memory contention. No browser/UI test claim.
6. [x] Save results/current progress/checkpoint/recovery and small verified commits. If a gate fails,
   retain the inactive candidate and report exact capability gaps;do not grow this into a prompt sweep.

## Frozen query cases and expectations

| ID | Language | Exact query | Expected evidence/answer |
| --- | --- | --- | --- |
| removal-en | English | How can I remove a grade of 4, and what grade do I get if I pass or fail the removal exam? | Complete3.3:re-exam/repetition,pass3/fail5,one removal exam;no invented deadline precedence. |
| inc-period-taglish | Taglish | Kapag naging 4 yung INC ko, may panibagong one year ba para i-remove? |3.7 remaining original INC period;retain conflicting-deadline limitation;no fresh one-year allowance. |
| fraud-en | English | What are the penalties for deception and fraud during admission and registration? | Related34/45/46 fields,progression and admission-overlap warning;no selected individual sanction. |
| procedure-fil | Filipino | Ano ang mga kailangan at step sa pagkuha ng pre-enrollment slip? | Checklist,four client steps in order,correct action/office/time associations;original step3 cutoff and total discrepancy. |
| fee-taglish | Taglish | Magkano yung special class fee per hour, at magkano yung example para sa 3 units lecture? | Rate370.37/hour,example54hours/20,000;individual assessment/currentness limits,no new arithmetic. |
| cheating-en | English | What are the penalties for cheating during an examination? | Printed exam-cheating penalties plus shared-measures context/individual-applicability limitation. |

Student capability:faithful answers over the corrected selected source groups. Evidence path:existing
document RAG with complete dependency closure;curriculum symbolic architecture unchanged. Phase exit
question:did these corrections/wiring restore complete grounded answers for the changed groups? This
is a bounded development check,not whole-corpus accuracy,formal evaluation or a student latency SLA.

## Verified implementation checkpoint

Budget RED12 expected failures,then GREEN61. Independent review found explicit null disabled legacy
procedure budget;edge RED2 confirmed it,then fixed. Local PackageStorage returned only direct
neighbors and leaked cross-version/out-of-scope companions when no chunk filter was supplied.
Three RED regressions confirmed it;separate version-filter RED1. Minimal eligible same-version
transitive closure now matches current SQL dependency semantics. Positive fixtures now use matching
versions;explicit excluded-version/audience tests retained. This is required local candidate parity,
not a new source or policy capability. Final focused109passed +9subtests,3.39s;independent61passed.
No remaining important review finding. Pre-existing config/entity-hint parity was not expanded into
this patch;current six cases still require exact trace inspection,not a hosted runtime claim.
Next:full frozen suite,then six cases once each;no prompts/source/activation changes.

Existing Charter sequence carry-forward:the corrected source package's base claim register has no
procedure_order;the already-reviewed1-4 list lives in2026-10-25-pre-enrollment-sequence-review.md.
The runtime check uses a separate validated runtime-source-review-register.json overlay for only
visible pre-enrollment instructions. All78 chunks/vectors/source receipts and hosted data unchanged.
Waiting six-case runner restarted before any model calls to load that overlay;no case was repeated.
Frozen code d72b88f;full-suite session19793,case runner35864(auto waits for full exit0). Logs/runner seal
and exact status reside in p11-corrected-runtime-20261026/. Do not commit new HEAD before observations
because runner verifies the frozen code hash. Snapshot documentation may be dirty while jobs run.

26Oct02:01 recovery:prior exec sessions disappeared;no Python processes remained,full suite had stopped
at94% with no exit marker,last log01:50:51,and no case-start file existed. Preserve old log as
full-suite-interrupted.log,not a passing/failing suite. Relaunched hidden PowerShell helperPID14328
using run_remaining.ps1;new full-suite-restart.log then six cases once on success. No model call
repeated;source/code frozen d72b88f. running-jobs.json now records launcher/time/log locations.

## Final result

Runtime code d72b88f/full suite6821+1595subtests passed(6skip2xfail6warnings,1341.43s,exit0).
All six cases completed once,16completions,3answered/3fallback/0exceptions;quality gate FAILED.
No activation or additional source work. All corrected78artifacts remain sealed. No jobs running.
[Detailed outcomes and next bounded fixes](2026-10-26-corrected-candidate-runtime-results.md).
Earlier RUNNING/recovery notes above are historical;this final result supersedes those statuses.
