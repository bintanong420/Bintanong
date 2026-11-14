# Broader multilingual check: six owner-approved fictional questions

21 October 2026. Owner approved all six wordings ("yep i approve all") after
seeing them with expectations. Code at `d75f4d1`. Fictional fixtures only:
the fixed document "Students submit slip S to Office K. The listed charge is 7
tokens." and the synthetic ZX101 -> ZX201 rule bundle, run by the real model and
the real Janus/SWI-Prolog engine. Retrieval is bypassed (the fixed document is
returned for every question). Not real PalSU data; not an accuracy rate.

Inputs: workspace `audit-evidence/p09-broader-20261021/broad-inputs.json`
(SHA256 `32ebdd412359b82cbc49d39abebc8de9b6c7fe5a6c4d287fbeecd1f7a224b375`),
same runner as the per-part observations. One attempt per case, fixed order.

| Case | Question | Expected (fixed before running) |
| --- | --- | --- |
| b1 fil Hybrid | Pwede ko bang kunin ang ZX201 kahit bumagsak ako sa ZX101, at saan ko ibibigay ang slip S? | Hybrid; Prolog ineligible (not_completed course-1); Office K; Filipino |
| b2 taglish Hybrid | Pwede ko ba i-take yung ZX201 kahit failed ako sa ZX101? Tapos saan ko i-submit yung slip S? | Same, in Taglish |
| b3 taglish missing | Magkano yung charge sa slip S, tapos kailan yung deadline? | No invented deadline; under the current contract withheld as insufficient_evidence with the deadline part unavailable |
| b4 en missing | Where do I send slip S, and who has to sign it? | No invented signer; withheld the same way |
| b5 taglish unrelated | Paano mag-drop ng subject? | No slip S prose released; unavailable/insufficient or clarification |
| b6 fil unrelated | Saan ko makikita ang grades ko? | Same as b5 |

Pass requires the expected outcome, no invented information and the requested
language. Withholding a supported answer counts as a failure. b3/b4 also
show the all-or-nothing contract behaviour that the owner may want to change.

## Result (one attempt each, code `d75f4d1`)

| Case | Outcome | Assessment |
| --- | --- | --- |
| b1 fil Hybrid | Prolog ineligible kept; "Ang slip S ay isusumite sa Office K." | Content PASS; style miss (owner-named deep word) |
| b2 taglish Hybrid | Prolog ineligible kept; "Ang slip S ay i-submit sa Office K." | PASS (slightly stiff grammar) |
| b3 taglish missing | Model correctly marked the deadline not_in_evidence, but added a placeholder claim; draft rejected twice -> repair_exhausted | FAIL (host defect); no invented deadline. Router labelled it fil, not taglish. |
| b4 en missing | Same placeholder defect for the signer | FAIL (host defect); no invented signer |
| b5 taglish unrelated | Slip S prose not released; insufficient_evidence | PASS: relevance confirmed on the per-part reviewer |
| b6 fil unrelated | Router asked for clarification | PASS by criteria; generic, unhelpful wording |

Full suite at `d75f4d1`: 6016 passed, 6 skipped, 0 failed (990 s).
Fixes in `838f6d4`: unavailable slots ignore placeholder claims; owner-named deep
Tagalog (isusumite, nakasaad, ihahain) triggers the existing style repair.
A post-fix observation of b1, b3 and b4 follows (one attempt each).

## Post-fix observation (code `838f6d4`, one attempt each)

- b1: "Ang slip S ay kailangang i-submit sa Office K."; Prolog ineligible kept.
  The style repair fired once (five calls). PASS.
- b3/b4: insufficient_evidence / parts_unresolved; deadline/signer recorded
  unavailable (not_in_evidence); nothing invented; 28 s, no review call. PASS
  under the current all-or-nothing contract, which still withholds the available
  charge/office. Partial answers that name the missing part are a pending owner
  design choice.
Evidence: workspace `audit-evidence/p09-broader-postfix-20261021/`.
