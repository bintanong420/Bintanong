# Current 559-chunk candidate: bounded selector/answer checks

**Goal:** first actual-model answer evidence on the inactive559local package. Student capability:
explain reviewed undergraduate services/policies (new beyond the active78) with complete source
context,English/Taglish replies and Hybrid composition. Evidence path:LLM router/topic selector ->
local PackageStorage retrieval with complete closures -> per-part generation/review/guards.
Phase exit question:does the559package give complete grounded answers on representative new
topics without regressing accepted active cases? Bounded development check,not formal evaluation,
whole-corpus accuracy,latency SLA or activation. Mirrors the [26Oct corrected-candidate checks](2026-10-26-corrected-candidate-runtime-checks.md).

**Baseline:** code8386501(repair-overflow retry);package SHAs in `package-status.json`;active78
pin/hosted releases unchanged. Owner28Oct:"proceed to the next action". No source/prompt/default
change;new cases are development probes,not accepted benchmark additions.

## Configuration (trusted researcher package input,never request/model input)

- Per-subject budgets:largest complete closure rounded up to1024,only the54subjects over the
  2048default (max8192). Rule reproduces active academic_misconduct3072/pre_enrollment4096.
- Saved-vector component check:all240claim reviews through real engine/PackageStorage:
  238complete with no gaps,2intentional not-stated reviews refuse. Max context7864E5.
- Composition as active pin:39hosted curricula (read-only anon),local559documents,program/
  curriculum aliases,short draft references. Review references `short` (opt-in;canonical review
  overflows the largest groups per [capacity](2026-10-27-559-capacity-results.md)). Gemma4E4B,
  8192/768/8,temp0/seed0,prefix cache,120s inference/180s request. One attempt per case,no retry.

## Frozen cases

| ID | Lang | Exact query | Expected (from printed source) |
| --- | --- | --- | --- |
| good-moral-en | en | How do I get a certificate of good moral character, and how much does it cost? | Checklist (student ID;OR from Cashier;alumni TOR copy;representative letter);7client steps in order with office/person;Php100 at Cashier;total30minutes. |
| library-card-taglish | taglish | Paano po kumuha ng library card, at magkano? | 3steps,Readers Services Librarian;Php10 lamination;15minutes;one-vs-two photo limitation disclosed. |
| entrance-health-fil | fil | Ano ang mga kailangan para sa medical examination ng bagong estudyante? | Requirements (lab tests,drug test,2x2,ID,entrance exam result);4steps clinic->submit->dental->medical;no fee;24minutes. Taglish reply. |
| leave-en | en | How do I apply for a leave of absence, and how long can it be? | Written before semester;reason/period<=1academic year;Department Chair,Dean approval;no readmission;Dean notifies Registrar. |
| shifting-taglish | taglish | Gusto ko mag-shift sa ibang college, ano yung process? | Prescribed form approved by both Deans;approved request to Registrar for recording;no invented counselling steps. |
| cross-enroll-en | en | Can I cross-enroll a subject in another school? What are the conditions? | Conditions a–e incl. not major/licensure,same description/units,<=9units;not two or more schools. |
| discipline-en | en | What happens after a disciplinary complaint is filed against a student? | Ordered printed steps (entry,formal charge/answer,hearing,committee decision10working days,President,BOR appeal);no invented deadlines;capacity stress. |
| hybrid-bscs-en | en,bscs-2018-2019 | I failed CC4. Can I take CC5 next semester, and can I cross-enroll CC5 in another school instead? | Hybrid:Prolog ineligible(CC4 unmet);cross-enrollment conditions incl. major-subject exclusion;no permission granted. |

Regressions (accepted active cases;status/decision must match roster19):grade-excellent-taglish,
cs-cc5-failed-cc4-en@bscs-2018-2019(context bscs),criminology-corequisite-tl.

## Acceptance and stop rule

Record status,route,selected subject/claims,model calls,warm inner seconds and author reading
against expectations. Regression mismatch fails the check. Answer gaps are recorded as capability
findings for regression-first fixes,not fixed by prompt sweeps or retries. No activation follows.
Ignored evidence:workspace/audit-evidence/p11-559-answer-checks-20261028/.
