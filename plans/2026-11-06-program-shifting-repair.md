# Generic program-shifting answer repair

Owner report: “Pano po lumipat ng kurso?” quotes college-shifting guidance instead
of handling a general program change; owner identifies the failure as “Phase 4”.
This is a request-stage label, not reopening implementation Phase 04.

## Diagnosis and change

Saved trace `api-call-1793952085654434000.json` contains Handbook 4.1, 4.2 and 4.3,
but generation quotes only the cross-college branch. Record-level coverage does not
prove all relevant branches were explained. The Filipino wording also missed the
existing shifting FAQ companion cue. Host closing text unconditionally named both deans.

Reuse the existing source-quotation normalization for whole generic program-change
parts: quote complete required clean body records, retaining both printed college
branches and Registrar guidance, followed by ordinary support/relevance review.
Source values remain unchanged. Explicit college/department subcases keep the ordinary
narrow path; unresolved source limitations prevent the clean-body override.
The host closing labels the two college branches conditionally for generic questions.
Extend the existing companion cue for Filipino course/program changes and English plurals.

## Verification

- Synthetic RED reproduced seven failures; no source-derived text in tracked fixtures.
- Worker affected generation/routing gate: 309 passed, 6.55s.
- Parent: `pytest tests/test_generation_program_shifting.py
  tests/test_generation_shifting_referral.py tests/test_generation_shifting_companion.py
  tests/test_routing_companions.py tests/test_system_information.py -q -p no:cacheprovider
  --basetemp=C:/Coding-projects/bintanong_workspace/audit-evidence/benchmark-fixes-20261106/shifting-parent-final`
  using existing Python3.13 venv: 57 passed, 2.24s.
- No new dependencies, original-source edits, school approval or institutional activation.
- Dev API reloaded at `9830a030`; exact question through `3217/api/chat` returned HTTP200,
  status `answered`, language `taglish`, with 4.1/4.2/4.3, FAQ form/advising/approval/Registrar
  steps and conditional office closing. Observed HTTP duration19.93s, not browser end-to-end.
  Evidence: ignored `program-shifting-chat-live.json`.
- That observation exposed existing Taglish “sa ang” in the closing. Focused RED reproduced
  it; remove the redundant article at the office-name join, retaining all role names/conditions.
  Final parent gate57 passed,1.99s. Only this host-wording change follows the live observation.
- Final dev-only reload loads the wording fix: root52864 / server46896 ready200,
  monitor72532 active, all five service endpoints HTTP200. No additional inference pending.
  Full72 and rendered-browser acceptance
  remain pending; no whole-benchmark or institutional-readiness claim.
