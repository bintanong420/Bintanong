# BS Environmental Science (2018-2019) prerequisite review 01

23 October 2026, College of Sciences. Read from the rendered page (`bses/page.png`); no developer CSV.
"Bachelor of Science in Environmental Science, Curriculum Program of Study, Effective SY
2018-2019*" (*BOR Res. No. 62 s. 2019 dated 3 July 2019). Undergraduate program: in scope.
Printed term totals 24/24/25/19/25/24/21/5 match the listed units; total 167 matches.

Owner decisions (23 Oct 2026), shown inline: several cells contain native text that is clipped out of
the printed page. Owner: use the visible text only ("let's stay with whatever is visible ... they
still base on what they can see"); EnS 104/L stays unknown (printed cell blank); the trailing comma
in Bio 107/L's "Bio 121/L," is ignored; EnS 110's two visible lines "EnS 105/L" / "EnS 103/L" are
both required (owner: "its good that you saw the ens 103/l"). Other cells use the standing approval.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CS/Environmental Science/EnviSci-for-student-new-version.pdf`,
SHA256 `02480073e4975f255931376136bcaf8e1ab454eb57545129ad5ac50764d22e91`. Scope `palsu-bses` / `bses-2018-2019`, review `p09-bses-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

Chem 3/L "Chem 2/L"; Bio 107/L "Bio 121/L,"; Math 2 "Math 1"; PATH Fit 3 "PATH Fit 1"; EnS 103/L "EnS 100/L"; EnS 105/L "Bio 107/L"; EnS 106 "EnS 102"; EnS 107/L "EnS 101/L"; EnS 113/L "Chem 3/L"; EnS 114/L "EnS 109"; Thesis 2 "Thesis 1"; EnS 115 "Chem 3/L"; Chem 2/L "Chem 1/L"; Bio 122/L "Bio 121/L"; PATH Fit 2 "PATH Fit 1"; NSTP 2 "NSTP 1"; EnS 102 "Bio 107/L"; PATH Fit 4 "PATH Fit 1"; Thesis 1 "Math 3"; EnS 108/L "EnS 100/L"; EnS 109 "EnS 103/L"; EnS 110 "EnS 105/L EnS 103/L"; EnS 111 "EnS 100/L"; EnS 112 "EnS 102"; GE-LWR "GE-PH"; Thesis 3 "Thesis 2"; Practicum "70%total units of major courses passed and completed".

50 courses; 27 printed cells; 23 blank cells stay **unknown**, not "no prerequisite": GE-CW, GE-UTS, GE-MMW, Chem 1/L, Bio121/L, PATH Fit 1, NSTP 1, GE- PH, Phys 1/L, EnS 104/L, GE-PC, Math 4, GE-Elect: PIC, GE-PS, GE- STS, GE-Elect: PES, GE-AA, Math 1, GE-Elect: IT, Math 3, EnS 100/L, EnS 101/L, GE - ET.

Native text clipped out of the printed page (recorded, not used; owner 23 Oct 2026):

- EnS 104/L: native cell "BIO 107/L"; hidden 'BIO 107/L'
- EnS 114/L: native cell "ENS 106 EnS 109"; hidden 'ENS 106'
- Thesis 2: native cell "ENS 110 Thesis 1"; hidden 'ENS 110'
- EnS 110: native cell "ENS 105/L EnS 105/L EnS 103/L"; hidden 'ENS 105/L'

## Rules applied

- Kept as printed, unknown: Practicum: "70%total units of major courses passed and completed".
- Spacing/case-only difference -> the one matching course: Bio 107/L: "Bio 121/L" -> Bio121/L; Bio 122/L: "Bio 121/L" -> Bio121/L; GE-LWR: "GE-PH" -> GE- PH.
- List -> all required: EnS 110: "EnS 105/L EnS 103/L".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bses/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 50 reviewed courses, kinds {'course': 25, 'unresolved': 24, 'all_of': 1},
activation_allowed false, file SHA256 `a08d0da317e5dcb434367ec1e235c96a0324368fe4e0c381f62f684253be4167`.
Real SWI-Prolog/Janus checks (offline research path): 12/12 as the readings imply:

- Chem 2/L {'passed': ['Chem 1/L']} -> eligible (expected eligible)
- Chem 2/L {'failed': ['Chem 1/L']} -> ineligible (expected ineligible)
- EnS 114/L {'passed': ['EnS 109']} -> eligible (expected eligible)
- Thesis 2 {'passed': ['Thesis 1']} -> eligible (expected eligible)
- Bio 107/L {'passed': ['Bio121/L']} -> eligible (expected eligible)
- EnS 110 {'passed': ['EnS 105/L', 'EnS 103/L']} -> eligible (expected eligible)
- EnS 110 {'passed': ['EnS 105/L']} -> unknown (expected unknown)
- EnS 110 {'passed': ['EnS 105/L'], 'failed': ['EnS 103/L']} -> ineligible (expected ineligible)
- EnS 104/L {'passed': ['Bio 107/L']} -> unknown (expected unknown)
- GE-LWR {'passed': ['GE- PH']} -> eligible (expected eligible)
- Practicum {'passed': ['Thesis 3']} -> unknown (expected unknown)
- Math 4 {} -> unknown (expected unknown)

Affected by Bio121/L: Bio 107/L, Bio 122/L, EnS 102, EnS 105/L, EnS 106, EnS 110, EnS 112.
Affected by EnS 100/L: EnS 103/L, EnS 108/L, EnS 109, EnS 110, EnS 111, EnS 114/L.

Not yet loaded into Supabase or wired into the runtime release.
