# BS Biology major in Medical Biology (2018-2019) prerequisite review 01

23 October 2026, College of Sciences. Read from the rendered page (`bsbio/page.png`); no developer CSV.
"Bachelor of Science in Biology (major in Medical Biology), Curriculum Program of Study, Effective
SY 2018-2019*" (*BOR Res. No. 62 s. 2019 dated 3 July 2019). Undergraduate program: in scope.
Printed term totals 24/24/26/24/21/24/17/8 match the listed units (year 3 sem 2 reaches 24 only with
Thesis 1 at 2 units, whose units cell is blank on the page; the "2" exists only as clipped native
text); total 168 matches.

All readings fall under the owner's standing approval (23 Oct 2026), no new question: comma lists
and one-per-line lists are all required; "Bio 108/L" (Bio 111/L) is the only "Bio 108L"; "75% of
Major Subjects" / "90% of Major Subjects" kept as printed (unknown); the clipped "2" in Thesis 1's
prerequisite cell is not used (visible-text rule); "Practicu" / "m" is a line wrap of "Practicum".
The page note "Choose one course from each cluster" (Bio Elect 1a-1d, 2a-2c) names elective
options for the slots "Bio Elect 1*" / "Bio Elect 2*"; it changes no prerequisite. The code
"GE – LWR" is printed with an en dash and kept as printed (runtime code matching should treat
dash variants alike; to handle when wiring course lookup).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CS/Biology - Medical Biology/BS-Bio-for-student-new-version.pdf`,
SHA256 `9d3e6cafb40d57d9db56c7ff78bc380990c66b0739532ac1982ae17bc022b6c5`. Scope `palsu-bsbio-medbio` / `bsbio-medbio-2018-2019`, review `p09-bsbio-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

Bio 103/L "Bio 100/L, Bio 101/L"; Bio 104/L "Bio 100/L, Bio 101/L"; Chem 3/L "Chem 2/L"; PATH Fit 3 "PATH Fit 1"; Bio 106/L "Bio 100/L, Bio 101/L"; Bio 107 "Bio 104/L"; Bio 108L "Bio 100/L, Bio 101/L, Chem 4/L"; Bio 109/L "Bio 100/L, Bio 101/L"; Bio Elect 1* "75% of Major Subjects"; Bio 116/L "Bio 104/L"; Bio 117 "Chem 4/L"; Bio 118/L "Bio 101/L"; Bio 119/L "Bio 100/L, Bio 101/L"; Thesis 2 "Thesis 1"; Bio 102/L "Bio 100/L Bio 101/L"; PATH Fit 2 "PATH Fit 1"; NSTP 2 "NSTP 1"; Bio 105/L "Bio 100/L Bio 101/L"; Chem 4/L "Chem 2/L"; GE – LWR "GE-PH"; PATH Fit 4 "PATH Fit 1"; Bio 111/L "Bio 108/L"; Bio 112/L "Bio 104/L"; Bio 114/L "Bio 100/L Bio 101/L"; Bio 115/L "Bio 105/L"; Thesis 1 "75% of Major Subjects"; Bio Elect 2* "75% of Major Subjects"; Thesis 3 "Thesis 2"; Practicum "90% of Major Subjects".

48 courses; 29 printed cells; 19 blank cells stay **unknown**, not "no prerequisite": GE-Elect: ES, GE-MMW, GE- AA, Bio 100/L, Bio 101/L, PATH Fit 1, NSTP 1, GE-ET, GE - PH, GE-Elect: PIC, Bio 110/L, GE - UTS, GE - CW, GE - PC, Chem 2/L, GE - STS, GE-Elect: IT, GE-PS, Bio 113/L.

Native text clipped out of the printed page (recorded, not used; owner 23 Oct 2026):

- Thesis 1: native cell "2 75% of Major Subjects"; hidden '2'

## Rules applied

- Kept as printed, unknown: Bio Elect 1*: "75% of Major Subjects"; Thesis 1: "75% of Major Subjects"; Bio Elect 2*: "75% of Major Subjects"; Practicum: "90% of Major Subjects".
- Shortened/variant code -> the one matching course: Bio 111/L: "Bio 108/L" -> Bio 108L.
- Spacing/case-only difference -> the one matching course: GE – LWR: "GE-PH" -> GE - PH.
- List -> all required: Bio 103/L: "Bio 100/L, Bio 101/L"; Bio 104/L: "Bio 100/L, Bio 101/L"; Bio 106/L: "Bio 100/L, Bio 101/L"; Bio 108L: "Bio 100/L, Bio 101/L, Chem 4/L"; Bio 109/L: "Bio 100/L, Bio 101/L"; Bio 119/L: "Bio 100/L, Bio 101/L"; Bio 102/L: "Bio 100/L Bio 101/L"; Bio 105/L: "Bio 100/L Bio 101/L"; Bio 114/L: "Bio 100/L Bio 101/L".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsbio/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 48 reviewed courses, kinds {'course': 16, 'unresolved': 23, 'all_of': 9},
activation_allowed false, file SHA256 `3f9372e7307dafb27c9c8929ae0d796e5dd9dd33651ebfe912f1f46891293f75`.
Real SWI-Prolog/Janus checks (offline research path): 11/11 as the readings imply:

- Bio 103/L {'passed': ['Bio 100/L', 'Bio 101/L']} -> eligible (expected eligible)
- Bio 103/L {'passed': ['Bio 100/L'], 'failed': ['Bio 101/L']} -> ineligible (expected ineligible)
- Bio 102/L {'passed': ['Bio 100/L', 'Bio 101/L']} -> eligible (expected eligible)
- Bio 108L {'passed': ['Bio 100/L', 'Bio 101/L', 'Chem 4/L']} -> eligible (expected eligible)
- Bio 108L {'passed': ['Bio 100/L', 'Bio 101/L']} -> unknown (expected unknown)
- Bio 111/L {'passed': ['Bio 108L']} -> eligible (expected eligible)
- GE – LWR {'passed': ['GE - PH']} -> eligible (expected eligible)
- Thesis 1 {'passed': ['Bio 115/L']} -> unknown (expected unknown)
- Practicum {} -> unknown (expected unknown)
- Thesis 2 {'failed': ['Thesis 1']} -> ineligible (expected ineligible)
- Bio 110/L {} -> unknown (expected unknown)

Affected by Bio 101/L: Bio 102/L, Bio 103/L, Bio 104/L, Bio 105/L, Bio 106/L, Bio 107, Bio 108L, Bio 109/L, Bio 111/L, Bio 112/L, Bio 114/L, Bio 115/L, Bio 116/L, Bio 118/L, Bio 119/L.
Affected by Chem 2/L: Bio 108L, Bio 111/L, Bio 117, Chem 3/L, Chem 4/L.

Not yet loaded into Supabase or wired into the runtime release.
