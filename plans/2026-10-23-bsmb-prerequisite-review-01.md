# BS Marine Biology (2022-2023) prerequisite review 01

23 October 2026, College of Sciences. Read from the rendered page (`bsmb/page.png`); no developer CSV.
"Bachelor of Science in Marine Biology, Curriculum Program of Study (Based on CMO no. 46, s. 2017),
Effective SY 2022-2023", Doc. Ref. PSU-CIM-CUR-042B, Rev. 00, effective 8 August 2022, *BOR Res.
No. 19 s. 2022 dated 4 March 2022. Undergraduate program: in scope. Printed term totals
20/24/24/24/21/20/summer 3/21/5 match the listed units; total 162 matches.

Owner decisions (23 Oct 2026), shown inline: (1) semicolons separate required courses like commas
(Bio 105/L, MBio 106/L, Bio 109/L); (2) "Bio 106A/L" -> Bio 106/L Genetics and "Bio 108A/L" -> Bio
108/L General Physiology (MBio 106/L, Bio 114/L); (3) "Physics 1/L" -> the course printed "Physic 1/L"
General Physics, and "Res 02" -> Res 2. Other cells use the standing approval ("75% of Core Courses"
kept as printed; "Chem 1 /L", "Bio 106 /L", "MBio  106/L" spacing; Bio 114/L's two lines all required).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CS/Biology - Marine Biology/BS-Marine-Biology-prospectus-template_07.08.2022-1.pdf`,
SHA256 `00a8f4d93d183dc6e8045a119724f497ab6540d9b249374935ec8a29699b743e`. Scope `palsu-bsmb` / `bsmb-2022-2023`, review `p09-bsmb-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

Chem 3/L "Chem 2/L"; PATH-Fit 3 "PATH-Fit 1"; MBio 102/L "MBio 101/L"; MBio 103/L "Earth Sci, Math 2, Physics 2/L"; MBio 104 "Math 2"; Bio 105/L "MBio 100/L; MBio 101/L"; Bio 106/L "Bio 105/L"; Practicum "75% of Core Courses"; MBio 107/L "MBio 106/L"; MBio 108/L "MBio 106/L"; MBio 109/L "MBio 106/L"; MBio 110/L "MBio 106/L"; Bio 114/L "Bio 106A/L Bio 108A/L"; Res 2 "Res 1"; Chem 2/L "Chem 1 /L"; NSTP 2 "NSTP 1"; PATH-Fit 2 "PATH-Fit 1"; Physics 2/L "Physics 1/L"; PATH-Fit 4 "PATH-Fit 1"; MBio 105/L "Earth Sci, MBio 103/L"; MBio 106/L "Bio 106A/L; MBio 105/L"; Bio 108/L "Bio 106 /L"; Bio 109/L "Bio 105/L; Bio 106/L"; Res 1 "MBio 104, MBio 106/L"; MBio-Elect 3 "MBio 100/L"; Res 3 "Res 02".

50 courses; 26 printed cells; 24 blank cells stay **unknown**, not "no prerequisite": GE-AA, GE- MMW, GE-Elect: IT, Earth Sci, Chem 1/L, NSTP 1, PATH-Fit 1, GE-PH, GE-Elect: EM, Math 2, Physic 1/L, MBio 100/L, GE-ET, GE-CW, GE-PC, GE-UTS, Math 1, GE-LWR, GE-PS, GE-STS, GE-Elect: PIC, MBio 101/L, MBio Elect 1, MBio Elect 2.

## Rules applied

- Kept as printed, unknown: Practicum: "75% of Core Courses".
- Shortened/variant code -> the one matching course: Bio 114/L: "Bio 106A/L" -> Bio 106/L; Bio 114/L: "Bio 108A/L" -> Bio 108/L; Physics 2/L: "Physics 1/L" -> Physic 1/L; MBio 106/L: "Bio 106A/L" -> Bio 106/L; Res 3: "Res 02" -> Res 2.
- Spacing/case-only difference -> the one matching course: Chem 2/L: "Chem 1 /L" -> Chem 1/L; Bio 108/L: "Bio 106 /L" -> Bio 106/L.
- List -> all required: MBio 103/L: "Earth Sci, Math 2, Physics 2/L"; Bio 105/L: "MBio 100/L; MBio 101/L"; Bio 114/L: "Bio 106A/L Bio 108A/L"; MBio 105/L: "Earth Sci, MBio 103/L"; MBio 106/L: "Bio 106A/L; MBio 105/L"; Bio 109/L: "Bio 105/L; Bio 106/L"; Res 1: "MBio 104, MBio 106/L".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsmb/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 50 reviewed courses, kinds {'unresolved': 25, 'all_of': 7, 'course': 18},
activation_allowed false, file SHA256 `6652b9e14d8b34d17fc75c16c3fbf3f27c5014ea370505d0a0630e6fa38345f4`.
Real SWI-Prolog/Janus checks (offline research path): 10/10 as the readings imply:

- Chem 2/L {'passed': ['Chem 1/L']} -> eligible (expected eligible)
- MBio 103/L {'passed': ['Earth Sci', 'Math 2', 'Physics 2/L']} -> eligible (expected eligible)
- MBio 103/L {'passed': ['Earth Sci', 'Math 2'], 'failed': ['Physics 2/L']} -> ineligible (expected ineligible)
- MBio 106/L {'passed': ['Bio 106/L', 'MBio 105/L']} -> eligible (expected eligible)
- Bio 114/L {'passed': ['Bio 106/L', 'Bio 108/L']} -> eligible (expected eligible)
- Physics 2/L {'passed': ['Physic 1/L']} -> eligible (expected eligible)
- Res 3 {'passed': ['Res 2']} -> eligible (expected eligible)
- Bio 105/L {'passed': ['MBio 100/L']} -> unknown (expected unknown)
- Practicum {} -> unknown (expected unknown)
- GE-LWR {} -> unknown (expected unknown)

Affected by Bio 105/L: Bio 106/L, Bio 108/L, Bio 109/L, Bio 114/L, MBio 106/L, MBio 107/L, MBio 108/L, MBio 109/L, MBio 110/L, Res 1, Res 2, Res 3.
Affected by Math 2: MBio 103/L, MBio 104, MBio 105/L, MBio 106/L, MBio 107/L, MBio 108/L, MBio 109/L, MBio 110/L, Res 1, Res 2, Res 3.

Not yet loaded into Supabase or wired into the runtime release.
