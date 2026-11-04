# Post-gathering development regressions

Only `p12-dev` / `p12-post-gathering-fixes` is edited. The gathering checkout/services remain untouched.

## New reports

- BSCS: eligibility for CS 17/L with CS 11/L not taken answers unmet; a later explicit prerequisite
  listing for CS 17/L incorrectly asks which subject/topic. Screenshot has no backend trace.
- Civil Engineering: explicit AC 31 eligibility with Phy 11/L not taken asks which subject/topic.
  Selected curriculum/version and backend interpretation are not visible in this screenshot.
- Both show an extra frontend diagnostic: "No specific clarification question was provided."

## Delivered candidate

One demonstrated host failure: when dialogue history exists, an absent model dialogue marker rejects
even a fully quoted, reviewed same-scope course operation before normal routing/validation.
Allow that self-contained request to proceed with old conversation focus cleared; normal downstream
validation still applies. Relative follow-ups, forged explicit references, missing course names and
unlocated targets retain their guards. No inference of grades or institutional rules was added.
Two focused cases first failed RED; final dialogue/compiler/session gate: **140 passed**.
Compiler OFF/ON router regressions verify an explicit new target does not reuse the saved course.
This is a proven failure mechanism, not a confirmed explanation of either screenshot's runtime packet.
Removed the redundant frontend diagnostic line; no dependency changes. Browser/device retest pending.

## Benchmark intake

Read `E:/Hawksprey/Downloads/The_Bintanong_Benchmark_Queries (3).pdf`: two pages, 24 English queries,
10 symbolic-family questions and 14 policy/procedure questions. SHA-256:
`4a15aab769b2eee5c4232bd6ed874311b644a7c1c17b2d91268928f0f41ca4e3`.
This differs from the earlier three-page multilingual edition. The PDF's category does not determine
the implemented route: general concurrent-prerequisite policy may need documents, and listing must
describe requirements without demanding grades. Use reviewed same-curriculum evidence; absent or
unreviewed coverage remains unknown/referral. Room/facility requests still require undergraduate applicability.
Keep these queries as evaluation cases, not prompt examples or course-specific routing conditions.

## Pending acceptance

BSIT follow-up report: five natural phrasings ask which courses require IT 3/L, but the server
either asks for a course/topic or lists IT 3/L's own GE-MMW prerequisite. No source rule changed.
Confirmed compiler gap: direct code targets immediately accepted the model's operation, while the
existing reverse-direction correction applied only to longer/unnamed targets. Added a bounded relation
check for a single named course followed by an explicit prerequisite role in a subject/course question.
It preserves opposite-direction questions and leaves multiple-course ambiguity to existing handling.
Router prompt now defines list_affected_courses as the reverse relation. No benchmark-specific course IDs.
RED: 20 failures across two synthetic curricula, five phrasings and two incorrect model operations.
GREEN: 168 dialogue/compiler/session tests, including eight opposite-direction safeguards.
The fixes do not establish that the live model will choose a usable operation on every paraphrase.
Owner supplied ngrok -> localhost:3216; this is the existing gathering app, not a p12-dev server.
No restart, merge into p12, or shared-model probe was performed. Old diagnostic text in the report is
consistent with a runtime that has not loaded the branch, but exact process revision is not exposed.

Run the 24-query benchmark and the two reported sequences against a separately configured development
runtime when shared-model probing will not compete with data gathering. Include fresh/history variants,
English/Taglish paraphrases, course-title inputs and other programs. Raw live model output is needed
to establish the screenshots' exact cause; no live probe was run in this continuation.
Retain the earlier checklist: clarification recovery, topic switching/shifting-office referrals,
partial-source limits, natural dependency questions, concise recovery plans and course names in replies.
The first screenshot also shows repeated unmet rule prose and "you're good to go"; wording remains pending.
