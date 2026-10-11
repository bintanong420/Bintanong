# Coordinator broad gate — fixed external F candidate

Verified imports in root_import.log point to f_spec_fixes/candidate prospectus and pipeline, exit0. Root directly ran system Python3.13 with PYTHONDONTWRITEBYTECODE=1 and PYTHONPATH set to that candidate, from the candidate cwd after required initial worktree Set-Location.

Exact pytest command:
py -3.13 -m pytest -q -p no:cacheprovider --rootdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\f_spec_fixes\candidate" --confcutdir "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\f_spec_fixes\candidate" --basetemp "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\f_spec_fixes\bt_root_full" "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\f_spec_fixes\candidate\tests"

Observed: 4146 passed, 1 skipped, 8 installed-dependency warnings, 13 subtests passed in166.02s, exit0. Baseline4133 + unchanged M01 boundary1 + new folder regressions12 =4146. Logs root_full.log/root_full.exit.txt.

Five test-generated pyc files remain preserved in external f_spec_fixes/candidate. All352 manifest-listed files are byte-identical. Initial deletion command was rejected by automatic policy before execution; no files were deleted. Safer completion: copied only all352 manifest-bound files into NEW draft_review_archives/f_fixed and verified every resulting hash against f_fixed_hashes.json. No source file was excluded; only derived bytecode remains with test evidence. root_final_integrity.json records exact boundaries.

No repository writes or ref movement. No Spec/Standards PASS inferred from tests; F Spec remains FAILED pending permitted review gate. 52/52 UNPROVED.