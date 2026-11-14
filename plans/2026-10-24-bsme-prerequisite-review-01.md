# BS Mechanical Engineering (2018-2019) prerequisite review 01

24 October 2026, College of Engineering. Read from the rendered page (`bsme/page.png`). "Bachelor of
Science in Mechanical Engineering, Curriculum Program of Study, Effective SY 2018-2019*", Doc. Ref.
PSU-CIM-CUR-014B (*BOR Res. No. 62 s. 2019). Undergraduate: in scope. Printed term totals
24/23/summer 9/24/24/26/23/summer 2/21/8; total 185.

Owner decisions (24 Oct 2026): co-requisite marks - Phy 11/L "Math 11/L C - Math 12/L" = Math 11/L +
Math 12/L co-requisite; ME 46/L "C - ME 42/L" = ME 42/L co-requisite. The OJT note ("passed 85% of the
subjects in Third Year") is a status condition; OJT's printed "3rd Year Standing" stays unknown unless
the year is given. Standing approval otherwise: "Math 12", "Math 11", "ME 22", "EE21/L" -> Math 12/L,
Math 11/L, ME 22/L, EE 21/L (missing "/L" or spacing, single match); year standings unknown.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CoE/BSME-for-student-new-version.pdf`,
SHA256 `c8e8a551473c492f6b327f182b0d89de9d59c97d603c6729796822f6badb5ffd`. Scope `palsu-bsme` / `bsme-2018-2019`, review `p09-bsme-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

GE-LWR "GE-PH"; Math 21 "Math 12/L"; BES 1 "Math 12, Phy 11/L"; ME 21 "Phy 11/L"; EE 21/L "Math 12, Phy 11/L"; ME 22/L "Math 11, Phy 11/L"; Math 22 "Math 11"; PATH Fit 3 "PATH Fit 1"; Math 23 ME "Math 21"; BES 23ME/L "BES 3, Chem 11/L"; EE 32A/L "EE 21/L"; ME 30 "BES 4"; ME 31 "ME22/L"; ME 32/L "BES 2"; ME 33 "ME 22/L"; PS 1 "Res 01ME"; ME 41 "ME 36"; ME 42/L "ME 30, ME 33"; ME 43/L "ME 37"; ME 44/L "ME 38/L"; ME 45 "4th Year Standing"; ME 46/L "C – ME 42/L"; ME Elect 2 "BES 6"; Math 12/L "Math 11/L"; Phy 11/L "Math 11/L C - Math 12/L"; PATH Fit 2 "PATH Fit 1"; NSTP 2 "NSTP 1"; BES 2 "BES 1"; BES 3 "BES 1"; BES 4 "ME 21"; ME 23 "ME 21"; ME 24/L "ME 22"; ECE 1/L "EE21/L"; PATH Fit 4 "PATH Fit 1"; ME 34/L "ECE 1/L"; ME 35/L "ICT 1/L"; Res 01ME "Math 22"; ME 36 "ME 31"; ME 37 "ME 32/L, BES 3"; ME 38/L "ME 23"; ME Elect 1 "3rd year Standing"; ME 39 "Math 21"; BOSH "3rd Year Standing"; PS 2 "PS 1"; ME 47/L "ME 46/L"; ME 48/L "ME 44/L"; MEP 1/L "4th Year Standing"; MEP 2/L "4th Year Standing"; MEP 3/L "4th Year Standing".

72 courses; 49 printed cells; 23 blank cells stay **unknown**, not "no prerequisite": GE-MMW, GE-Elect: ES, GE-PH, ME 11, Math 11/L, Chem 11/L, ED 1/L, PATH Fit 1, NSTP 1, GE-STS, GE-AA, GE-Elect: GS, BES 5, BES 7, ICT 1/L, GE-PS, GE-CW, GE-PC, ED 2/L, GE-ET, GE-Elect: EM, GE-UTS, BES 6.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): ME 46/L: "C – ME 42/L" -> COREQ:ME 42/L; Phy 11/L: "Math 11/L C - Math 12/L" -> Math 11/L, COREQ:Math 12/L.
- Year standing -> unknown unless the student states their year: ME 45: "4th Year Standing"; ME Elect 1: "3rd year Standing"; BOSH: "3rd Year Standing"; MEP 1/L: "4th Year Standing"; MEP 2/L: "4th Year Standing"; MEP 3/L: "4th Year Standing".
- Shortened/variant code -> the one matching course: BES 1: "Math 12" -> Math 12/L; EE 21/L: "Math 12" -> Math 12/L; ME 22/L: "Math 11" -> Math 11/L; Math 22: "Math 11" -> Math 11/L; ME 24/L: "ME 22" -> ME 22/L; ECE 1/L: "EE21/L" -> EE 21/L.
- Spacing, case or hyphen variant -> the one matching course: ME 31: "ME22/L" -> ME 22/L.
- Co-requisite: ME 46/L: "ME 42/L"; Phy 11/L: "Math 12/L".
- List -> all required: BES 1: "Math 12, Phy 11/L"; EE 21/L: "Math 12, Phy 11/L"; ME 22/L: "Math 11, Phy 11/L"; BES 23ME/L: "BES 3, Chem 11/L"; ME 42/L: "ME 30, ME 33"; Phy 11/L: "Math 11/L C - Math 12/L"; ME 37: "ME 32/L, BES 3".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsme/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 72 reviewed courses, kinds {'unresolved': 29, 'course': 35, 'all_of': 7, 'co_requisite': 1},
activation_allowed false, file SHA256 `734f4e9dcf9791e4d6e820c4e45daab2c6337135641b151069cc79866c2daf38`.
Real SWI-Prolog/Janus checks (offline research path): 8/8 as the readings imply:

- Phy 11/L {'passed': ['Math 11/L'], 'enrolled': ['Math 12/L']} -> eligible (expected eligible)
- ME 46/L {'enrolled': ['ME 42/L']} -> eligible (expected eligible)
- BES 1 {'passed': ['Math 12/L', 'Phy 11/L']} -> eligible (expected eligible)
- ME 24/L {'passed': ['ME 22/L']} -> eligible (expected eligible)
- ME 37 {'passed': ['ME 32/L'], 'failed': ['BES 3']} -> ineligible (expected ineligible)
- MEP 1/L {} -> unknown (expected unknown)
- BES 5 {} -> unknown (expected unknown)
- ME 47/L {'passed': ['ME 46/L']} -> eligible (expected eligible)

Affected by Math 11/L: BES 1, BES 2, BES 23ME/L, BES 3, BES 4, ECE 1/L, EE 21/L, EE 32A/L, ME 21, ME 22/L, ME 23, ME 24/L, ME 30, ME 31, ME 32/L, ME 33, ME 34/L, ME 36, ME 37, ME 38/L, ME 39, ME 41, ME 42/L, ME 43/L, ME 44/L, ME 46/L, ME 47/L, ME 48/L, Math 12/L, Math 21, Math 22, Math 23 ME, PS 1, PS 2, Phy 11/L, Res 01ME.
Affected by ME 21: BES 4, ME 23, ME 30, ME 38/L, ME 42/L, ME 44/L, ME 46/L, ME 47/L, ME 48/L.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 24 Oct 2026 (runtime read-back equal).
