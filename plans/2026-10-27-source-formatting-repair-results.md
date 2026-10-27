# Source formatting repair results — 27 October 2026

The three concrete packaging defects are repaired in a separate inactive derivative.
Source words and original PDFs remain unchanged;only printed footer110was moved
from policybody to audited page provenance. This is not activation or a Phase11exit.
[Plan](2026-10-27-source-formatting-repair-plan.md) · [Source comparison](2026-10-27-delegated-source-review.md).

## Changes

| Record | Correction | Rebuilt chunks |
| --- | --- | --- |
| Feedback,C114/printed110 | Separate heading and four feedback/complaint labels/values;retain monitoring text;move footer to provenance. | 3replacing2 |
| Borrowing,C78–79/printed74–75 | Separate metadata,paired checklist,headings and totals;join final action/person-office continuation across pages. | 5replacing4 |
| Computeruse,C81–82/printed77–78 | Separate metadata/checklist;split1minute,ComputerRoomStaff andLibrary using nativecharacter ranges and original glyph boxes. | 4replacing3 |

Current derivative:339candidates(177Handbook/162Charter),327byte-identical retained
plus12rebuilt replacing9. All required companionlinks complete. Fieldboundary splits
explain the increase from336;no new sourcecontent was added. Prior baselines and
human/assistant receipts remain unchanged.

## Evidence and identities

Evidence root:workspaceaudit-evidence/p11-omitted-chunks-20261026.
Current overlay:source-formatting-corrected/candidate-chunks.json.
OutputSHA256:`eaf38e555d8bcc5c7a282d2343ef614bd68fad6faaf5e5b8ff99a91131f20e69`.
Input336SHA256:`118e635ea17610be51f6b5c9b24e0c000c3ee826696f7f4fb04cb5aa3fd4f001`.
ScriptSHA256:`08d8b747e145650bbad2792df3eb726c38abf66ac766ec4a09395a9f2245d82c`.
ReviewmappingSHA256:`19ddacca00efc1f2b7eb55c0aa6b439ddaf7612c27664cd7f1f3ac5131187304`.
Artifactseal binds9files,including reviewmapping. Separate original336overlay preserved.
All9affected oldchunks were assistant-compared,not explicitly human-approved.
Current source-review lineage:213retained explicit human approvals+114retained
assistant comparisons+12source-backed rebuilt candidates=339. Newgovernance states
remain pending;no explicit human approval was invented for corrected IDs.

## Verification actually run

- Focused source-data assertions:3expected failures on baseline,then3passing on derivative.
  Checks cover footer exclusion/feedbackchannels,paired borrowingchecklist/cross-page
  action and person/office,and separate computertime/person/office plus one-hour slot.
- Every original span in the affected9chunks checked against nativePDFcharacters and
  original glyph-union boxes. All2573nonblank policyglyph positions conserved;only
  3footerdigits moved to provenance. No guessed geometry or other glyph loss/addition.
- All339contracts/chunk bindings pass;327retained records compare byte-for-byte;
  all prior source-limit payloads remain unchanged and full neighborclosure holds.
-12new exactE5counts:388/356/189;327/419/350/330/438;330/423/333/425.
  Newmaximum438;combinedmaximum469,all<=480,truncationdisabled.
- Existing builders repeated deterministically;fullscript rerun produced identical bytes
  for all8generated artifacts. Reviewmapping separately bound in the finalseal.
- Existing regressions:100tests/151subtests passed,2.71seconds,exit0.
- Documentation:git diff --check;phase_state validate. Fullproduction suite not rerun:
  no production behavior/code/dependency/runtime change in this data-only repair.

Commands used sharedPython3.13.7 at workspaceaudit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe:

```text
-X utf8 -B audit-evidence/.../test_source_formatting_repair.py
-X utf8 -B audit-evidence/.../rebuild_source_formatting.py
FORMAT_REPAIR_CANDIDATES=<339derivative> -X utf8 -B audit-evidence/.../test_source_formatting_repair.py
-X utf8 -B -m pytest -q -p no:cacheprovider tests/test_reviewed_policy_preparation.py tests/test_reviewed_policy_chunks.py tests/test_reviewed_service_context.py tests/test_reviewed_service_steps.py tests/test_reviewed_record_context.py tests/test_reviewed_descriptive_context.py tests/test_reviewed_flowchart_context.py --basetemp=<evidence>/source-formatting-pytest-tmp
```

Two ordinary authoring issues were resolved from direct evidence before success:
feedbacklabel wraps across a native newline,and reviewevent requires source_sha256.
No repeated sourcecontent question or owner exception was needed.

## Remaining gates

The three named repairs are complete. Broader labelled service reauthoring,
nativehyphen/URLnormalization and final image/service structural bindings elsewhere
in the corpus remain separate unfinished work. Keep known sourceholds,cutoffs,
conflicts and scope limits. Runtime contextbudget,embedding/answer regression and
activation gates remain;no hostedwrites,release/pin/rule/frontend/model changes.
