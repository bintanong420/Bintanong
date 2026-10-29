# Simple-question gate: draft for owner wording acceptance

28 October 2026, Claude lane ([split plan](2026-10-28-phase11-model-workstream-split.md)). Purpose: the bare
minimum. Everyday single-detail questions must be answered correctly in English and Taglish before
other answer-quality work counts. **Status: draft. Wordings and expected facts await the owner's
acceptance. Not yet run.** These are evaluation questions, so they must stay out of prompt examples.

Pass rule per question: the status is as expected, the answer contains every listed printed fact (or
its faithful Taglish rendering), it adds no condition the source does not print, and it cites the listed
source. Gate passes only at 42/42. Each failure gets a RED regression before any fix.

| # | Question (English / Taglish) | Must contain (printed source) |
| ---: | --- | --- |
| 1 | What is the normal unit load for summer? / Ilang units ang normal load sa summer? | 9 units; graduating students up to 12 with prior Dean approval (Handbook, Summer load) |
| 2 | How long can a leave of absence be? / Gaano katagal pwede ang leave of absence? | not exceeding one (1) academic year; applied in writing before the semester starts (Handbook, Leave) |
| 3 | Can I transfer to another section? / Pwede ba akong lumipat ng section? | only for misadvising, lack of prerequisite, conflict of schedule and similar cases; instructor consent and Dean approval (Handbook 2.1) |
| 4 | How do I drop a subject? / Paano mag-drop ng subject? | dropping form from the University Registrar after paying the fee at the Cashier; approved by class adviser and Dean; furnished to offices (Handbook FAQ 7) |
| 5 | How do I shift to another program? / Paano mag-shift ng program? | shifting form; approved by the College Dean and College Guidance Practitioner; submitted to the Registrar (Handbook FAQ 8) |
| 6 | What do I need for a library card? / Ano ang kailangan para sa library card? | COR and two (2) 1x1 recent photos; fee None (Charter, Issuance of Library Card) |
| 7 | How do I get a class card? / Paano kumuha ng class card? | Class Card Issuance Form; valid ID (Charter, Issuance of Class Cards) |
| 8 | How do I claim my diploma? / Paano i-claim ang diploma ko? | general clearance (original) and documentary stamp at the Registrar's Office; fee None (Charter, Issuance of Diploma) |
| 9 | When am I considered a second-year student? / Kailan ako considered second year? | completed first year or 25% but not more than 50% of total units (Handbook, Curricular levels) |
| 10 | What is the residence requirement for graduation? / Ano ang residence requirement para maka-graduate? | at least one year of residence work immediately prior to graduation (Handbook 1.4) |
| 11 | What residence is needed to graduate with honors? / Ano ang residence requirement para sa honors? | at least two years immediately preceding graduation; not less than 75% of units in the university (Handbook 5.1.3) |
| 12 | How do I get off probation? / Paano matanggal sa probation? | pass more than 50% of units with final grades in the next semester; two consecutive failures lead to disqualification (Handbook, Scholastic standing) |
| 13 | When is the deadline for a subject substitution petition? / Kailan ang deadline ng petition for substitution? | not later than the last day for extended registration, at the Dean's/Campus Director's office; later goes to the next semester (Handbook 3) |
| 14 | What do I need to apply for a refund of school fees? / Ano ang kailangan para sa refund ng school fees? | valid ID; refund request form (1 copy); applies to withdrawal or overpayment (Charter, Refund) |
| 15 | What should I do if I was absent from class? / Ano ang gagawin ko kung umabsent ako? | excuse slip from the College Secretary, presented to the instructor (Handbook, Absence) |
| 16 | What grade is 1.0 in percentage and rating? / Ano ang percentage at rating ng grade 1.0? | the grading_scale row for 1.0, matching the active 78 answer (accepted roster family) |
| 17 | CC5 with failed CC4, BSCS 2018-2019 (accepted roster wording, en + Taglish) | Prolog: ineligible, CC 4/L not completed (structured path) |
| 18 | What are the courses for BSIT 1st year? / Ano ang mga subject ng BSIT first year? | all 16 printed courses of BSIT 2018-2019 first year, by semester. 1st sem: CC 1/L, CC 2/L, GE-CW, GE-PC, GE-STS, GE-UTS, NSTP 1, PATH Fit 1. 2nd sem: CC 3/L, GE-AA, GE-ES, GE-MMW, IT 1, IT 2/L, NSTP 2, PATH Fit 2 (structured `list_term_courses`) |
| 19 | What are the subjects for first year, first sem in Criminology? / Ano ang subjects ng 1st year 1st sem crim? | 8 printed courses of BSCrim 2018-2019: Crim 1, GE - CW, GE - PC, GE - UTS, GE-PS, LEA 1, NSTP 1, PATH Fit-DEF TAC 1 |
| 20 | What are the subjects for first year, second semester in Criminology? / Ano ang subjects ng crim first year second sem? | 9 printed courses: CDI 1, Crim 2, GE - AA, GE - ET, GE - MMW, GE – Elect: ES, GE-Elect:IT, NSTP 2, PATH Fit-DEF TAC 2 |

Plus two controls (one language each): "Hi po!" -> greeting reply, no academic answer; "What are the
admission requirements for the College of Law?" -> undergraduate-scope notice, no undergraduate rule.
Count: 16 x 2 document + 4 x 2 structured + 2 controls = 42. Course lists come from the only
reviewed curriculum of each program in the release (BSIT/BSCrim 2018-2019), so no curriculum clarification
is expected; printed codes, titles and units are kept as printed.

Open points for the owner: accept or edit the wordings; confirm each must-contain fact matches what a
student needs (the readings are quoted from reviewed chunks; source gaps stay disclosed).
