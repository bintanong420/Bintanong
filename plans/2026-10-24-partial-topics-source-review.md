# Partial policy topics — source review and delivery decision

Owner 24 Oct (Codex machine date; earlier handoff says 25 Oct) selected the database review path and a new
research release. Existing published records stay immutable. Preserve current 19 chunks and 39 curriculum
links, append independently reviewed content, and keep the current release as rollback. Exact source
readings still require owner confirmation. This is provisional undergraduate research, not school approval.

Original: `dataset/StudentHandbook/2021/PSU Student Handbook.pdf`.
SHA-256: `4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8`.
Native text and rendered original physical p.87 inspected; original and derived images stay ignored.
The table's four columns are 1st, 2nd, 3rd and subsequent offenses.

## Batch 1 — approved

Owner answer: "Approve both as printed". Confirmed for undergraduate research use; no institutional
currentness/authority inferred. Preserve source references and blank cells separately from named penalties.

- I. Improper Uniform: 1st "Verbal Warning"; 2nd "8 Hours Community Service"; 3rd "24 Hours Community
  Service"; subsequent "3 days Community Service". Do not convert hours to days or infer equivalence.
- II. Behavioral Defiance, item 1: "Any violation of law committed within the premises of the University.
  For purposes of this paragraph ‘Law’ shall refer to any general enactment enforced in the Philippines
  specifically but not limited to Theft, Robbery, and Bribery. (Refer to Book III for the Provisions)".
  1st-offense cell: "Depending upon the gravity of the act, the University may give a penalty ranging from
  two weeks to dismissal from the University without prejudice to the imposition of sanction by appropriate
  authorities of the land." Later cells blank. Preserve "two weeks" without inventing the penalty type;
  retain Book III reference. Blank cells never establish no penalty. No individual disciplinary decision.

## Batch 2 — approved with limits

Owner answer: "Approve both with those limits" (same original physical p.87).

- II.2: "Carrying within this University premises any firearm, bladed weapon, or any kind of dangerous and
  deadly weapon; Provided, that this shall not possess the in connection with their studies and have a permit
  for the purpose. Any unlawful possession of firearms shall be immediately reported to the police or proper
  military authority." 1st: "The offender shall be turned over to the police authorities and shall be
  suspended for 1 month." 2nd: "Dismissal"; 3rd/subsequent blank. The malformed "Provided…" clause is in
  the original, not an extraction error. Retain an unresolved source-gap warning; never repair/interpret the
  exception or apply the sanction to a student's case. Retention approval does not resolve that exception.
- II.3: "Possession or use of prohibited drugs or chemicals such as LSD, shabu, marijuana, heroin or opiate in
  any form within the University premises". 1st: "The offender shall be turned over to police authorities
  and shall out rightly be dismissed from the University without prejudice to due process." Later cells blank.
  Preserve wording and due process; blank cells do not establish no penalty.

## Pending

Further disciplinary pages, complete Charter pre-enrollment and grading source packaging remain to review.

## Batch 3 — approved

Owner answer: "Approve both as printed" (original physical p.88, viewed before asking).

- II.4: "Hazing and inflicting physical force or violence resulting to physical injuries, disgrace and demean
  any fellow student in connection with initiations, admission to fraternities, sororities or any other student
  organizations." 1st: "Dismissal from the University. Any case involving the unlawful violence or use of
  unlawful weapons shall be reported to police or to the proper authorities." Later cells blank.
- II.5: "Any student who were found to misappropriate and/or misuse the allotted and/or collected fund; or by
  failure to properly account and liquidate their fund after their term and before the assumption of the next
  student leader. This also includes any student that was found to be involved and served as an accomplice of
  such act." 1st: "Suspension for one semester" plus "*In case of graduating students, their credentials shall
  not be released until they clear all their accounts with the university"; 2nd "Dismissal from the
  University"; later cells blank. Retain the graduating-student condition with item 5; blanks unspecified.

## Database design work remaining

Existing C1 partial-review RPC mutates document_versions and refuses published sources; selected-review
receipts currently reference one C1 receipt per source. Supplementary delivery must support cumulative
old/new chunk snapshots with append-only evidence, without changing document_versions or prior receipts.
Do not bypass published-source triggers or manufacture a new PDF version. Reuse existing field/span,
source-event, selected-context and source-binding validators. Rehearse on a disposable local database,
including replay/conflict/privacy/RLS/immutability and rollback, before hosted apply.
