# Risk-scenario probe results (owner request, 24 October 2026)

HEAD `050e808`, hosted 39-curriculum research release, Gemma 4 E4B on :18088, one attempt per question, fresh
session each. Script and raw log: workspace `audit-evidence/p11-20261023/live-api/risk_probe.{py,log,jsonl}`.
An exploratory probe, not an evaluation family or an accuracy rate; keep these wordings out of prompt examples.

Owner scenario: PalSU colleges have their own Citizen's Charters that differ a bit from the university-wide one.
The dataset holds only the university-wide 2025 4th Edition (`dataset/CitizenCharter/2025/University/`).

## Results (24 questions)

| # | Question (short) | Reply | Verdict |
| - | --- | --- | --- |
| R1 | Pre-enrollment steps "in CBA" / "citizen's charter ng CTE" | Answered from the university-wide Charter, no note that it is university-wide | **Risk (owner scenario confirmed)** |
| R1b | "proseso ng pag-enroll sa College of Sciences" | office referral | acceptable |
| R2 | "What is the prerequisite of CC 5?" (BSCS chosen) | "Eligibility cannot be established..." + CC 3/L, CC 4/L unknown | **Wrong framing** (= E2): a list question answered as an eligibility check |
| R3 | "Ano ang ibig sabihin ng INC ... hanggang kailan ma-complete?" | referral | **False negative**: grade_completion is reviewed; router chose two topics, only the first (grading_scale) is retrieved |
| R4 | "pwde b mg overload?" (typo), "overload" (one word), "Paano mag-overload at magkano ang special class fee?" | bare "please clarify" | **Defect**: overload is a reviewed topic; routing failed before the sink (diagnostic not yet seen) |
| R5 | "Can I take Data Structures and Algorithms?" / "Can I take CS 999?" | bare "please clarify" (`unresolved_entity`) | **Defect**: should say the course name/code was not found and ask for the printed code |
| R6 | "How many units is CC 5 in BSCS 2018-2019?" | "temporarily unavailable, try again later" | **Misleading**: unit lookup is unsupported (`unsupported_requirement` -> evidence_unavailable) |
| R7 | Cebuano "Unsaon nako pag-overload?" | bare clarify (`model_ambiguity`) | minor: should say supported languages |
| R8 | "Thank you po!" | "Hello. Pwede akong tumulong..." | minor wording |
| R9 | "What is the passing grade?" | referral | coverage gap: only the grade 1.0 row of the scale is reviewed |
| R10 | First-year subjects of BSIT | referral | coverage gap: no curriculum-listing capability |
| R11 | Tuition per unit | "cannot verify the evidence answers" | safe; wording differs from the referral |
| R12 | Dean of CS / UP Diliman enrollment | out of scope / referral | acceptable |
| OK | Hi; capabilities; prereq without program (asks program + curriculum); "Hindi ako pumasa sa CC 4..." (CC 4/L not completed, CC 3/L unknown); BSIT CC 5 (BSIT has its own CC 5/L); "GRADE 1.0 ILANG PERCENT???" | correct or acceptable | — |

Also seen: a transformers warning "sequence length 692 > 512" during one request; check whether any encoder
input is truncated (likely token counting only).

## Proposed order (owner to choose)

1. R4 (diagnose the hidden routing failure; covered topic unanswered), 2. R1 (university-wide note on Charter
answers that name a college), 3. R2/E2 (list prerequisites for "what is the prerequisite of X"), 4. R5, R6
(name what was not found / unsupported instead of bare or "temporarily unavailable"), 5. R3 (retrieve every
chosen topic, not only the first), then minor R7, R8, R11. R9/R10 are coverage decisions.
