# Natural grading failures and omitted student-source coverage —26October2026

Two saved natural queries completed once against active corrected78/39;both failed answer expectations.
Omitted Handbook/Charter material contains substantial undergraduate-applicable content. This is a
coverage/audience triage,not a full field-accuracy audit or approval to chunk/activate new material.
[Bounded plan](2026-10-26-natural-grading-and-source-coverage-triage.md).

## Two actual hosted queries

Research root release-offline-research-set-95fe326cf31a4439;hosted p11-research-corrected-20261026.
Same39curricula/existing short-draft profile,8192context/768output;no prompt/code/source/release change.
Four model calls(total routing/style),0case retries;runner exit0means capture completed,not quality PASS.

| Query | Actual final status/reply | Observed failure location | Warm inner seconds |
| --- | --- | --- | ---: |
| Ano yung passing grade dito sa PalSU? | temporarily_unavailable;“Hindi muna magawa ang check ngayon. Subukan ulit mamaya.” | Router picks grading_scale but requests8mappings1.0–2.75,not3.0. Retrieval returns storage_error after31.237s;underlying storage cause not proven. |46.489|
| GRADE 1.0 ILANG PERCENT??? 😭 | insufficient_evidence;“Wala pa ito sa reviewed sources ng Bintanong. Paki-ask sa tamang university office.” | Router chooses control=clarify,evidence_need=unknown,no subject/claims/ambiguities. Existing empty-clarification path becomes no_evidence. No retrieval occurs. |12.107|

Expected source-backed facts remain reviewed:Handbook physical46,3.0=75–76/Passed and
1.0=98–100/Excellent. The latter fact passed the explicit accepted query in the preceding smoke.
These outcomes do not establish bad source chunks;one fails before retrieval,the other has a storage
error and overbroad claim selection. Do not claim the storage error's cause is fixed or known.
No draft/reviewer completions were made. Capture includes raw model requests/responses,wire output,
integration stage events,evidence status and final answers. Warm inner includes hosted calls;
encoder startup21.668s/composition/model startup/API/browser excluded;queueing unmeasured.

## Source identity and inspection coverage

Originals resolved from p11/dataset and hashes verified;no edits or new intake:

| File | Total physical pages | SHA-256 |
| --- | ---: | --- |
| PSU Student Handbook.pdf |394|4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8|
| PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition.pdf |117|42a93994e1467df0f32c7038d1c21f638c23ac0f1dee984463acf56caf526529|

Owner's “0–40” interpreted as physical1–40;there is no physicalpage0. Handbook1–40native inventory,
detailed academic clauses26–40 and adjacent41–46context consulted to avoid cutting continuations.
Charter all117page native inventory/contents scanned,selected service-audience fields checked.
Original renders inspected:Handbook27/39;Charter33/34/59/86/103/109. Other renders saved for later review.
This is not an independently reviewed transcription of all117pages or every field on these services.
Use physical page numbers below:Charter printed numbering has jumps/duplicates;fixed offsets unsafe.

## Handbook first40:proposed coverage

| Physical pages | Content and proposed treatment |
| --- | --- |
|1–17|Cover/approvals/messages/introduction/mission/history/maps/organization;mostly background,not transaction procedures. Do not describe all as non-student material.|
|18–24|Program/campus offerings;undergraduate information mixed with Laboratory School(p19)and graduate(p20)entries. Useful historical source context,not an automatic replacement for39versioned prospectus ledgers.|
|26–27|General admissions and undergraduate freshmen requirements;direct candidate. On27explicit GRADUATE STUDENTS begins a separate excluded block.|
|28–30|Transfers,foreign/dual-citizenship admissions,readmission/second baccalaureate;undergraduate-applicable clauses candidate. Separate Law,graduate/transnational graduate/probation passages. ETEEAP bachelor offerings exist on19;review their special pathway separately,not as staff-only merely because applicants are employed.|
|31–34|Sequencing/prerequisites,registration checklists,freshmen/transfers/old/foreign students,cross-registration/cross-enrollment;strong candidates. Exclude graduate checklist on33. Prerequisite decision logic stays reviewed/versioned Prolog;new general exceptions cannot override it automatically.|
|34–37|Refunds/withdrawal,academic and summer loads,graduating overload,student/class classifications,special classes;strong candidates with undergraduate/graduate clause separation and all conditions.|
|38–40(+41continuation)|Attendance,leave of absence,student maternity leave,withdrawal,warning/probation/dismissal/disqualification;strong candidates,high-consequence fields require source review. Keep complete exceptions/continuations.|

Original examples:Handbook27prints UNDERGRADUATE STUDENTS/FRESHMEN APPLICANTS and later GRADUATE
STUDENTS on the same page. Handbook39:“Students are allowed to take a maternity leave for a maximum
of one month without prejudice to their attendance in classes.” This is a student procedure;the
employee maternity leave in Charter44is a separate excluded HRMO procedure.

## Charter:proposed omitted-service coverage

| Physical pages | Services | Audience judgment |
| --- | --- | --- |
|6–20|Registration/readmission;TOR/transfer credentials/certifications/CAV/diploma|Strong undergraduate academic-record candidates;select undergraduate-applicable checklists and alumni-of-undergraduate pathways,not graduate-only fields.|
|51–57|Counselling,good moral certificate,admission test/results,student activity approval|Explicit student-facing services;candidate student pathways,retain faculty/adviser actions in the student process.|
|59–64|Medical examination/health and dental clearances/certificate of sickness;consultation/treatment|Enrollment/OJT/ROTC/academic-activity/sickness-document pathways are relevant candidates. Student support access can be reviewed;employee/dependent pathways and clinical advice are not authorized.|
|66–68|Statement of account/assessment;school-fee refunds|Strong academic-finance candidates;retain exact withdrawal/dropping/overpayment conditions.|
|70–73|Cash/check disbursement|Mixed students/employees/suppliers/creditors;hold until a specific undergraduate academic claim is identified. Do not exclude the whole Cashier office or promise an entitlement.|
|75–84|Library inquiries/document delivery/cards/borrowing/return/clearance/facilities/computers/printing/interlibrary use/donation acknowledgement|Student academic-support candidates;many explicitly limited to PSU Main Campus. Certification/donation pathway needs distinct treatment.|
|86|Library-resource requisition under Internal Services|Explicit students AND faculty/staff;not automatically staff-only. Review student title-suggestion/request pathway and source description mismatch before inclusion.|
|103–113|Faculty consultation,subject changes/dropping,graduation/awards evaluation,academic requests,class cards,removal exam|Strong student academic candidates beyond existing pre-enrollment102–103;preserve complete logical service/page breaks.|
|22–49;88–100|HR employment/personnel leave;PMO contractor billing/department repair/planning|Employment/procurement/administrative procedures excluded from undergraduate advisory coverage.|
|114–117|Feedback/complaints and office contacts|Possible referral/support metadata after scope/date/source review;not blanket approval of every government contact/service.|

Concrete original text supporting inclusion:
- Charter103,printed99,STUDENT CONSULTATION TO FACULTY:“Students may consult their faculty in any
  academic concerns.” Who may avail:“Palawan State University Students”.
- Charter67,printed63,APPLICATION FOR REFUND OF SCHOOL FEES:“Students may apply for refund of school
  fees due to withdrawal of enrolment or overpayment”. Complete qualifications remain to review.
- Charter86,printed82,REQUISITION OF LIBRARY RESOURCES,Who may avail:“Bonafide PSU Main Campus
  Students and Faculty/Staff”. Internal Services heading alone is not an audience exclusion.

## Source issues to carry into focused review

- Charter86description says“Students and other stakeholders requesting acknowledgement receipts for
  various delivery.” while heading/actions concern selecting titles/requisition. Preserve both;do not
  silently rewrite description or infer student procurement authority.
- Charter109,printed105,academic-related requests repeats“Students may request evaluation for academic
  awards.” under a broader heading. Service student applicability is clear;scope of actual requests
  requires full field review109–110,not a fabricated generic authority.
- Charter112,printed108,removal-exam checklist says“Class Card Issuance Form”;step1says“removal form”.
  Preserve discrepancy for focused review;do not substitute a form. Grade/removal policy authority and
  dates still need source decisions;procedure does not resolve existing deadline conflicts.
- Handbook27/29introduce extra program requirements without a visible list before the next heading;
  source completeness needs exact-region review. Keep original gaps;no guessed college requirements.
- Charter printed pagination shifts around HRMO;physical34prints30,physical102prints98. Referencing
  an assumed physical-minus-one label would misidentify later services.

## Recommended review order and next boundary

Expand the review queue,not study audience:Handbook undergraduate admission/registration26–34;
Charter Registrar6–20and college student services103–113;then Handbook load/attendance/leave/standing
34–41,school-fee assessment/refunds66–68,OSAS51–57,library75–86and student academic clearances59–64.
Review clear sections in small complete-service batches;new defects/mixed applicability go to owner
with original regions/exact wording. Current inspection does not approve numeric policy fields.

Next owner judgment:priority/inclusion of these student-service candidates and treatment of mixed
support pathways;then separate bounded grading-failure correction and source-review implementation.
No chunks,embeddings,source words,prompts,release membership or production behavior changed here.
Active78/old19rollback/old80draft retained. Prior full6896+1595subtests belongs unchanged code;
no repeat suite needed for observation/documents. Validate source hashes,receipt/links,diff and phase.

Evidence:A/p11-grading-coverage-triage-20261026;A=workspace/audit-evidence. source-page-index.json,
sources/*.txt,renders/*.png,grading/results.json/completion.json/binding.json,per-case raw calls/
integration/answer.json,grading.log/.exit. Source/thesis scope evidence in bounded plan.
