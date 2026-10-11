# Phase F recovery review package

Source pin: dd699958505996358864383ff9c184cb98aec985. Baseline:0caeaba8d8221a0f75b154e94bc3167b780f1407. Candidate is the complete pinned archive plus one standalone regression under tests/test_prospectus_adapter_digest_boundary.py. No production code change, repository writes or ref movement. Manifest f_candidate_hashes.json binds all files.

Review scope: Phase F committed Tasks1–7, the22 recorded plan corrections, and recovered M01 boundary regression. Docker Tasks8/9, real adapter conversion, and final docs Task11 remain unfinished/gated. Do not treat a bounded Spec pass as full Phase F or deployment completion.

Read current decision docs/decisions/draft-phase-f-tools-cli.md before old plan examples. Preserve pending-only authority, single snapshot/hash ownership, strict locator/source/output boundaries, safe verified publication, single/folder CLI semantics, per-PDF process isolation and CLI/API equivalence. Existing shared pipeline digest check must remain.

M01 baseline96pass; mutant without new regression96pass; external boundary test1fail on mutant and original augmented97pass. The latter pipeline guard masks the removed adapter guard for current end-to-end refusal. No production safety bypass was reproduced; classification is defense-in-depth boundary coverage gap.52/52 remains UNPROVED. All exact logs/commands/diffs are in sibling ../m01_recovery/M01_RESULT.md.

Root full suite completed at original worktree: 4133 passed, 1 skipped, 13 subtests, exit 0; root external regression against verified actual worktree import passed 1, exit 0. A combined C:/E: collection invocation failed before tests with pytest drive-root collection WinError1337; subsequent commands run separate roots. Broad gate belongs coordinator, not review child.

Independent runs must read reviewer role and appropriate template, read archive only, use systempy -3.13 with no pytestcache and external unique basetemp/PYTHONDONTWRITEBYTECODE1, do not install/download or change dependencies. Return actual source locations, reproducible case, severity orNONE. Never self-review; Spec before separate Standards; one recheck only confirmedHighfix. At most2activeincludingroot, no children. Nothing here is institutional approval.

Root gate completed: original draft-f full suite4133passed,1skip,8warnings,13subtests,exit0 in209.94s. External recovered regression importedactualdraft-f and passed1,exit0. Logs f_recovery_full_worktree.log and f_boundary_root.log at evidence root. No repository modifications.
