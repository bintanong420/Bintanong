# Controller verification evidence
Observed 2026-10-06, Asia/Manila. Main checkout preserved.

- Historical Task6 reconstruction: `python reconstruct_task6.py` archives f802c76 parent, overlays testfile+conftest from f802c76 outside Git, then runs pytest. Underlying pytest exit1;12failed2passed; full evidence task6-red-reconstruction.log. This is reconstruction, not an original historical test log.
- GUI Task9 reconstruction: `python reconstruct_gui_task9.py` archives ffe0a10 and overlays only current testfile. Underlying pytest exit2, expected ImportError missing CLI during collection; gui-task9-red-reconstruction.log. Four original untracked files backed up with SHA256 in gui-task9-original/; realworktree unchanged.
- API/embedding availability check from phase-d: `%TEMP%/gui-review-venv/Scripts/python.exe -m pytest -q tests/test_api_probes.py tests/test_embedding_service.py -p no:cacheprovider`. Tool exit0;6passed2upstreamwarnings in0.85s. Final identity comprehensive647 test log supersedes this availability check for coverage.
- Confirmed53e3c00 commit trailer and clean phase-d Git state after identity task. Review package covers641523d..53e3c00. Specification review pending; no completion claim for fullPhaseD.
- Path-only preflight all44 originals under finalized home-relative defaultroot: final181,stage202,temp137,failed251; no homeoutputs generated.
