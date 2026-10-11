# Phase E first-batch Spec fix ROUND1

### ROUND1 baseline reproduced — 2026-10-07T19:11:25.2366686+08:00
- Files: No repository production edits; only round1 evidence/progress.
- Command: py -3.13 <batch1>/spec-repro.py
- Result: exit0;baseline-repro.log; all five invalid full-field/ownership claims accepted by committed3c545630
- Next: Add authentic five regression failures plus complete-field/normalized/spanning controls before edits.

### ROUND1 authentic RED — 2026-10-07T19:11:28.7736268+08:00
- Files: tests/test_prospectus_chunks.py;progress ledger
- Command: py -3.13 -m pytest -q tests/test_prospectus_chunks.py -k "complete_own_field" -p no:cacheprovider --basetemp <batch1>/round1/red-temp
- Result: exit1;red.log; five new bypass regressions plus valid controls were written before production changes.
- Next: Minimum _course_source complete field and own-row/spanning admission checks.

### ROUND1 verified RED — 2026-10-07T19:11:56.2115877+08:00
- Files: tests/test_prospectus_chunks.py
- Command: py -3.13 -m pytest -q tests/test_prospectus_chunks.py -k "complete_own_field" -p no:cacheprovider --basetemp <batch1>/round1/red-verified-temp
- Result: exit1;red-verified.log; initialRED6failed2passed56deselected0.40s retained; supported whitespace-code control replaces mistaken slash-to-dash control. All five bypass assertions unchanged; production unchanged.
- Next: Complete own-field/row fix; controls now match the existing owner.

### ROUND1 focused GREEN check — 2026-10-07T19:12:55.4403994+08:00
- Files: rag.py;tests/test_prospectus_chunks.py;progress ledger
- Command: py -3.13 -m pytest -q tests/test_prospectus_chunks.py tests/test_prospectus_authority.py tests/test_prospectus_parser.py tests/test_prospectus_course_checks.py -p no:cacheprovider --basetemp <batch1>/round1/green-temp
- Result: exit0;green.log; authentic verifiedRED5failed3passed56deselected0.48s exit1 before minimum _course_source fix.
- Next: Read focused result, verify original five external reproductions now rejected, freeze and documentary report.

### ROUND1 original probes GREEN/FROZEN — 2026-10-07T19:13:29.1242176+08:00
- Files: rag.py;tests/test_prospectus_chunks.py;progress ledger
- Command: py -3.13 <batch1>/spec-repro.py
- Result: exit0;fixed-repro.log; original five claims now rejected explicitly; focusedgreen292passed13subtests from green.log. Production frozen.
- Next: Root broadgates and scoped Spec recheck then independent Standards; documentation only until yield.

## Phase E Spec ROUND1 frozen handoff — 2026-10-07T19:14:35.0015393+08:00

- Base3c545630e30f2e388f52880c8c54656d2825d097, isolated E worktree; production/tests frozen. Files: rag.py (_course_source only), tests/test_prospectus_chunks.py (five regression cases, three valid controls), docs/decisions/prospectus-rag-provenance.md and progress ledger. No stage/commit/installs/agents/push/main/dev writes.
- Baseline originalfive probes allaccepted, baseline-repro.log exit0. Initial authentic RED6failed2passed56deselected0.40s exit1: requiredfive bypasses plus one mistaken validcontrol slash-to-dash spelling. Existing loose owner preserves slash; corrected validcontrol uses supported whitespace-only spelling CS101/L. This is test-fixture correction, not weakened rejection. Initial red.log retained.
- Verified authentic RED before production edits:5failed3passed56deselected0.48s exit1, red-verified.log. Exact command in PowerShell from C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-e, PYTHONDONTWRITEBYTECODE1: py -3.13 -m pytest -q tests/test_prospectus_chunks.py -k 'complete_own_field' -p no:cacheprovider --basetemp "$round\red-verified-temp", with $round='E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\phase-e\batch1\round1'.
- Minimum source admission fix: every selected field cell must contain actual_source row in same table (genuine spanning cells remain valid); complete canonical code/title/prerequisite/unit field equality replaces regex containment, with existing complete-code loose normalization retained. Numericunits parsed from canonical printed unit field. Shared verify/parser/units/audit/PhaseC owners and prerequisite_phrase unchanged; no transformed/wrapped ownership guess.
- Final focused GREEN292passed13subtests12.05s exit0, green.log. Exact command: py -3.13 -m pytest -q tests/test_prospectus_chunks.py tests/test_prospectus_authority.py tests/test_prospectus_parser.py tests/test_prospectus_course_checks.py -p no:cacheprovider --basetemp "$round\green-temp". Existing PhaseC prerequisite assertion regression remains meaningful/green. Completefields/whitespace-code/spanning controls accepted.
- Originalfive probes afterfix allacceptedfalse with explicit code_not_in_source_text/title_not_in_source_text/prerequisite_not_in_source_text/units_not_in_source_text reasons; no course/term/overview emitted. Command py -3.13 <batch1>/spec-repro.py exit0, fixed-repro.log. git diff --check exit0 with existing LF/CRLF notices.
- Ruling (supersedes initial batch token-boundary claim): complete own-field equivalence is required, since token boundaries still admitted code/title/prerequisite/unit subphrases. Off-row cells are insufficient even when absent from section evidence_ids; tighten candidate chunk admission only. Cost if wrong: legitimate transformations/continuations without explicit parser-backed ownership may be rejected; report course/reason at the later corpus gate instead of weakening source proof for chunk counts.
- Root baseline1574passed1skipped13subtests/self80 was previouslygreen; implementer did not repeat broadgates. Root next: freshfull/self, explicitpathcommit, scopedSpec recheck then independentStandards. LayoutTask5, capturedPDF/schema/JSONL/rejectionpayloadTask6, corpus/human/source/photo gates stay deferred; no institutional approval or wholePhaseE completion.
### ROUND1 blank-adjacency authentic RED — 2026-10-07T19:15:12.8000514+08:00
- Files: tests/test_prospectus_chunks.py;progress
- Command: py -3.13 -m pytest -q tests/test_prospectus_chunks.py -k "blank_claim or genuinely_blank" -p no:cacheprovider --basetemp <batch1>/round1/blank-red-temp
- Result: exit1;blank-red.log;new blank-erasure regressions plus genuinely blank/missing prerequisite controls before production change.
- Next: Remove truthiness bypass; reject empty entity fields; preserve actual blank prerequisite wording.

### ROUND1 blank-adjacency focused GREEN — 2026-10-07T19:15:39.8349567+08:00
- Files: rag.py;tests/test_prospectus_chunks.py;progress
- Command: py -3.13 -m pytest -q tests/test_prospectus_chunks.py tests/test_prospectus_authority.py tests/test_prospectus_parser.py tests/test_prospectus_course_checks.py -p no:cacheprovider --basetemp <batch1>/round1/blank-green-temp
- Result: exit0;blank-green.log;authenticRED3failed2passed64deselected0.35s exit1 before blank-claim guard.
- Next: Freeze final same-guard patch; atomic final report/checkpoint; root full/self/spec/standards.

### ROUND1 root-confirmed blank-claim adjacency FINAL FREEZE — 2026-10-07T19:16:10.5917382+08:00

- Earlier292focusedgreen/freeze superseded by this same sourceguard adjacency. Root originalrepro showed blank raw prerequisite accepted while canonical owncell printedCS100, falsely rendering notrecorded. Blank claims had skipped full equality through value truthiness. No broadgates had started.
- AuthenticRED3failed2passed64deselected0.35s exit1, blank-red.log, before production edit. Cases: blankprerequisite erases printedCS100; emptycode/title erase ownprinted entity. Controls: actualblank ownprerequisitecell and missing ownprerequisitecell remain accepted/blank_unreviewed.
- Minimum _course_source fix enforces prerequisite canonical equality for blank claims and refuses emptycode/title entities. No PhaseC/parser/audit/verify/units owner changes; no wrapped/transformed ownership assumptions.
- ExactRED command: py -3.13 -m pytest -q tests/test_prospectus_chunks.py -k 'blank_claim or genuinely_blank' -p no:cacheprovider --basetemp "$round\blank-red-temp". ExactGREEN: py -3.13 -m pytest -q tests/test_prospectus_chunks.py tests/test_prospectus_authority.py tests/test_prospectus_parser.py tests/test_prospectus_course_checks.py -p no:cacheprovider --basetemp "$round\blank-green-temp". PowerShell cwdphase-e, PYTHONDONTWRITEBYTECODE1, $round='E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\publish_resume_2026-10-07\phase-e\batch1\round1'. Actual final count/time in blank-green.log, final checkpoint below.
- Production/tests FINAL FROZEN; fourchangedpaths remain rag.py,chunk tests,decision record,progressledger. Root full/self/scopedSpec then independentStandards required; allTask5/6/corpus/human/source/photo deferrals remain. Ruling: equality includes the empty prerequisite assertion; a genuinelyblank/missing source stays unreviewed, while a printed requirement cannot disappear. Costifwrong: an actual parser omission is rejected as a candidate rather than silently represented as notrecorded.