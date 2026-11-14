# Independent session Spec review — 2026-10-10

SPEC FAIL; /root/session_spec_review. Pin3e0d6b361d83a965bf900dd6a41d6ea5c274bf54, baseadf5d5192396dd18e58174add83773f2a0ce4aaa, standalone session scope only.

High — backend/bintanong_session/store.py:211: upload deletion retains cached private answers. Reproduce SessionStore/create_session/add_upload with fx.Recorder('FICTIONAL-DELETED-GRADE'); cache_put(token,'answer',samevalue); delete_upload(token,upload_id). facts_for(token)==() but cache_get(token,'answer') returns removed private value and fx.holds(store,value)==True. Master16.1 upload/context deletion and15.1/15.3 safeguards require retained context removed. Minimal fix clear session cache on successful upload deletion (no cache provenance exists). Regression acceptance: deleted facts/cachecontent disappear; other upload facts and another session cache remain intact.

Medium — backend/bintanong_session/store.py:194–196: malformed extractor item bypasses fixed failure. BadOutput.fact_id=[]; add_upload(token,bytearray(b'synthetic'),lambda*args:[BadOutput()]) leaks TypeError unhashable list. Expected fixed ExtractionFailed, no accepted facts. Bytearray cleanup still works. Minimal fix reject non-SessionFact before ID access/hash. Regression acceptance: fixed ExtractionFailed, no commits, workspace removed, bytearray cleared.

Independent56passed0.44s, py3.13/importassertions/no-bytecode/no-cache/uniqueexternalbasetemp. Allsixaddedfiles reviewed, threecommits946addedlines. Candidate348hashes before/after match. Baseline342files verifiedpinnedrawGitblobs; candidate minus sixadditions same baseline. AllGit differences exclusivelyCRLFnormalization. Archivesunchanged.

Standards NOT RUN untilSpecPASS. Broad suite/realparser/restart/deployment/memoryforensics/institutional approval NOT RUN. Uploaddeletion privacy defect open atreviewtime. One confirmedHigh-fix recheck allowed after rootgates; no selfreview.