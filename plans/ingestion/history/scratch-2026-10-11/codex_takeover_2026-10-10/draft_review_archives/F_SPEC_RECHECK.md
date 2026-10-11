# Single authorized F Spec recheck — 2026-10-10

SPEC FAIL. Finding2 ADDRESSED; Finding1 NOT FULLY ADDRESSED. The single owner-authorized Medium recheck is consumed. No second recheck or Standards dispatch authorized on this FAIL.

Medium — backend/bintanong_tools/prospectus.py:335–343,433. Original missing-semantic-map reproducer passes, but native Windows filesystem errors represent filenames with escaped backslashes. _scrub matches only native/slash forms, leaving declared semantic map absolute path in decoded index error.
Exact reproduction: valid one-PDF folder/record; _run_child raises OSError(13, 'Permission denied', str(external_semantic)); run_candidates(..., ExtractionSettings(semantic_doc=external_semantic)). Actual PermissionError Errno13 diagnostic retains repr-escaped E:\\...\\private maps\\meaning.md. Expected useful error+filename without absolute directory. Acceptance: native filename-bearing OSError -> processing_error, no candidate artifacts, diagnostic contains filename but neither native/slash/escaped absolute directory.
Reproducer retained: evidence-root bt_f_spec_recheck_oserror_yqlqwg3o/.

Finding2 addressed at prospectus.py:403–418. Missing/invalid audits/non-object manifests rejected before summary; original bad first child indexed processing_error and second candidate produced.

Independent verification12passed13deselected2installedTyper/Clickwarnings exit0 7.64s. Adapter/pipeline imports bound to clean f_fixed archive. Both352-file manifests passed. Changes limited to prospectus.py and add-only foldertests. Read authorization/originalreview/results/completepatches/rootgate/code/tests/role/template.
Skipped broadgatererun/unrelatedsurfaces/Standards/Docker/realDocling. Remaining Medium prevents Spec PASS. No institutional approval.