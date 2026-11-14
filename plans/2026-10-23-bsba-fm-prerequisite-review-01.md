# BS Business Administration, major in Financial Management (2018-2019) prerequisite review 01

23 October 2026, College of Business and Accountancy. Read from the rendered page (`bsba-fm/page.png`).
"Bachelor of Science in Business Administration (Major in Financial Management), Curriculum Program
of Study, Effective SY 2018-2019*", Doc. Ref. PSU-CIM-CUR-007.2B (*BOR Res. No. 62 s. 2019).
Undergraduate: in scope. Printed term totals 23/26/23/23/18/18/9/6 match the listed units; total 146.
Printing oddity kept as printed: the code "GE-ES" carries the title "Ethics". All readings fall under
the standing approval: "Fin 2001 & BA 2001" all required; "GE PC" -> GE-PC (hyphen variant);
Practicum's "All courses from 1st to 4th year" kept as printed (unknown).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CBA/BSBA  - FINANCIAL MANAGEMENT/BSBA-FM-for-student-new-version.pdf`,
SHA256 `176cbbd07bcec16a9037b610636546c032fc66ac2aa24536e163632988625141`. Scope `palsu-bsba-fm` / `bsba-fm-2018-2019`, review `p09-bsba-fm-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

P2301 "Fin 2001 & BA 2001"; P2303 "Fin 2001 & BA 2001"; PATH Fit 3 "PATH Fit 1"; P2305 "Fin 2001 & BA 2001"; P2306 "Fin 2001 & BA 2001"; P2308 "Fin 2001 & BA 2001"; GE-LWR "GE-PH"; NSTP 2 "NSTP 1"; PATH Fit 2 "PATH Fit 1"; P2302 "Fin 2001 & BA 2001"; P2304 "Fin 2001 & BA 2001"; BE 2001 "GE PC"; PATH Fit 4 "PATH Fit 1"; BAC 8 "BAC 7"; P2307 "Fin 2001 & BA 2001"; Practicum "All courses from 1st to 4 th year".

49 courses; 16 printed cells; 33 blank cells stay **unknown**, not "no prerequisite": GE-UTS, GE-CW, GE-PC, BAC 1, BA 2001, GE-PH, NSTP 1, PATH Fit 1, GE-Elect: ES, GE-PS, BAC 4, E2301, E2302, BAC 7, GE-IER, BAC 2, GE-STS, BMEC 2, E2305, BE 2002, GE-ES, GE-MMW, Fin 2001, GE-AA, BAC 5, GE-Elect: EM, BMEC 1, BAC 6, GE-Elect: PES, E2303, E2304, Fin 2002, BAC 3.

## Rules applied

- Kept as printed, unknown: Practicum: "All courses from 1st to 4 th year".
- Spacing, case or hyphen variant -> the one matching course: BE 2001: "GE PC" -> GE-PC.
- List -> all required: P2301: "Fin 2001 & BA 2001"; P2303: "Fin 2001 & BA 2001"; P2305: "Fin 2001 & BA 2001"; P2306: "Fin 2001 & BA 2001"; P2308: "Fin 2001 & BA 2001"; P2302: "Fin 2001 & BA 2001"; P2304: "Fin 2001 & BA 2001"; P2307: "Fin 2001 & BA 2001".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsba-fm/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 49 reviewed courses, kinds {'unresolved': 34, 'course': 7, 'all_of': 8},
activation_allowed false, file SHA256 `7f711040ed8245211ebb6375422065da5ec19c494c2ef9839a26047352298791`.
Real SWI-Prolog/Janus checks (offline research path): 6/6 as the readings imply:

- P2301 {'passed': ['Fin 2001', 'BA 2001']} -> eligible (expected eligible)
- P2301 {'passed': ['Fin 2001'], 'failed': ['BA 2001']} -> ineligible (expected ineligible)
- BE 2001 {'passed': ['GE-PC']} -> eligible (expected eligible)
- BAC 8 {'passed': ['BAC 7']} -> eligible (expected eligible)
- Practicum {} -> unknown (expected unknown)
- BAC 7 {} -> unknown (expected unknown)

Affected by Fin 2001: P2301, P2302, P2303, P2304, P2305, P2306, P2307, P2308.
Affected by BA 2001: P2301, P2302, P2303, P2304, P2305, P2306, P2307, P2308.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
