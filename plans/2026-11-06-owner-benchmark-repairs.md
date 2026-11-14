# Owner benchmark repairs — 6 November 2026

Bounded repair work on `p12-dev` / `p12-post-gathering-fixes`, starting `730344e7`.
No new numbered phase, corpus activation or dependency/model change. Main gathering checkout stays separate.

## Evidence and acceptance

- Owner CSV: `E:/Hawksprey/Downloads/1_Bintanong 72 bench queries test log.csv`, SHA-256
  `293bc578ab3a41066825bdf3544596abe6e95f0f974d8eb70bf2322fba950273`.
- PDF edition 4: SHA-256 `be467633c1429dc72b49e473d4633f81045f340859dd86f0d167ff368577a9a3`;
  same 24 rows / 72 variants as the [existing run](2026-11-05-live-language-browser-results.md).
- Marks: 47 Y, 8 P, 14 N, 3 blank. Row 7 was not tested because program selection is mandatory.
  These are owner marks, not independent adjudication or a newly measured accuracy score.
- Owner confirmed these results came from 3217, whose temporary rate-limit override works.
  Do not modify main/public limits or reopen that resolved issue.
- Second CSV is the same run's fix-handoff export, SHA-256
  `247ad9efd335565c53a070e8d8727165d93b85e0481a918daa973bf3a3b9637c`.
  Its row 15 TG fix-log cell is `#REF!`; original checklist and exported prompt both say Y. Not a second evaluation.
- Consulted thesis physical 17–18, 39–44, runtime routing PNG, master section 3, current handoffs,
  undergraduate/source-gap policy and owner decisions. Preserve advisory scope, structured course reasoning,
  English/Taglish replies and existing deadline discrepancy readings. No architectural discrepancy identified.

## Repair order and reach

1. Course identity: row 9 cannot list a reviewed named course's prerequisites. Inspect literal extraction,
   scoped catalog binding and router validation; reuse existing routing tests with synthetic curricula.
2. Document selection: rows 10, 13–19 vary by language or choose the wrong topic/claim. Trace selector,
   interpretation and evidence separately; fix a demonstrated shared failure, not benchmark phrase routing.
3. Procedure completeness: rows 23–24 omit application requirements or substitute a library-specific service.
   Preserve original source limitations; establish applicable service coverage before changing claims.
4. Reply quality: row 8 should answer listing directly; Taglish wording and unrelated service prose need
   review at the shared generation seam. Source quotations retain their printed English.

For each slice: reproduce, failing public-boundary regression, smallest fix, related regressions, then a
bounded live rerun of affected variants. Keep evaluation questions out of prompt examples. Do not infer
source approval from a CSV expected-answer cell, or count a clarified source ambiguity as a fixed procedure.
Raw traces and original-source evidence remain ignored under workspace `audit-evidence/benchmark-fixes-20261106/`.

## Current state

Row 9 live router trace resolved `Forensic 3/L` but rejected the program phrase `BSCrim student`: the catalog
contains `BS Crim`, not its compact spelling. Shared program-alias matching now allows omitted whitespace
within a reviewed alias; whole-word boundaries, ambiguity and selected-scope checks remain. No course alias
or source data changed. Synthetic public validation regressions: corrected RED 6 failed / 5 passed;
GREEN 11 passed. Related validation/compiler/program-switch/catalog suite: 217 passed.
Commands use existing Python 3.13 venv, `-m pytest`, `-p no:cacheprovider`, external `--basetemp` beneath
the raw evidence directory. Bare `python` resolves to an unrelated environment; system Python lacks pytest.
No install was performed. Test files: `test_routing_program_spacing.py`, `test_routing_validation.py`,
`test_routing_compile.py`, `test_routing_program_switch.py`, `test_routing_catalog_separation.py`.

Forensic: real router resolves all three variants; full HTTP English turn lists Forensic 2/L.
Listing prose: removed the unrelated eligibility invitation (row 8). RED 6 failed / 18 passed;
GREEN 50 passed across listing/eligibility/course-fact tests. Rule trees, citations and unknown conditions stay.

General policy (row 10): compiler bypassed the existing topic-backed non-course correction, creating a
fake term target. Reuse that correction only without declared course/term mentions; named targets and
existing structural reconstruction remain. RED: compiled path asked for a term while normal path dispatched
RAG. GREEN 195 compiler/wire/understanding tests; larger routing group 282 passed. Hybrid tests retained.
Filipino: all-unknown fragments are retried once using the existing repair budget. Do not repeat the wrong
assistant interpretation in that retry. Complete review-bound body fields up to existing context bounds
now inform selected topics; no truncated body is added. Metadata fallback exposes reviewed claim names
when printed descriptions are unavailable; redundant selector labels removed. Context/selection group 143 passed.
Latest targeted router traces: EN/TG validated; Filipino validated after clean retry. Full answer rerun pending.
No benchmark wording was added to prompts. Source policy/guards remain; general policy alone is RAG,
while a checked course/term request plus documentary explanation remains Hybrid.

## Current repair snapshot

Ownerrequestedpublishingrepairstoorigin/p12-evaluation-harness. Integrationcheckoutp12-eval-publish
mergesp12-post-gathering-fixes@d2ad9fefwithorigin/eval@abd007b4, preservingthearchitectureimageblob
489502f73117f63eb3272ca5dc2dd2e1e0077d53. Freshmergedcheckoutgate585passed26.97s;nofull72rerun.
Regularfast-forwardpushonly;runningp12/p12-devcheckoutsandowner'sdirtygatheringnotesremainuntouched.
Ignoredlaunchers/rateoverride/contextbudget/keepalivestaymachine-local,notpartoftheGitdelivery.

R3remainingwork: `f5c7a264` rejectsunstatedfreshmanaudiencewithboundedsemanticrepair/generalservice
companion (RED3;341tests). `3b522271` resolvesTaglishinstructionconflict: exactquotes/termskept,
paraphrasedstudentactionusesnaturalgrammar (78tests). `8c3b3b60`,`a52c73c1` compactmarkquotes:
INCmethodsentencefirst,fullapproval/forfeiture,originalsource-limitmessagesdeduplicatedonce.
Independentreviewcaughtfullnoteomission;fixedwithREDregression. Integrated133pass; canonicaltext+refs
andordinaryreviewremainrequired. Ownerallowedjudgmentontimingafteraskingbothhold/reload; announced
development-onlyreloadthenlaunchPID62928, warming. Keepalivepause-dev-apiexistsuntilready.
Nextlive: exactB13TL+INCEN/Taglish+grade4EN+IDTG, briefserialcalls; nofull72claim.
Livea52c73c1: exactB13TLnowCharterregistrationnotfreshman; IDTGnatural'mag-reportkasaOSAS'; INCEN/TG
methodfirst, grade4stilloverlong. `bdf6d50a` removesunaskedno-improvementsectionfromgrade4method,
redundantmachinewarningwrappersandsecondreferralonlywhenallcanonicalsource-limitclaimsarepresent.
Fullsourcequalificationmessagesremain, ordinaryreviewunchanged. Finalintegrated174tests pass.
Announcedlastdev-onlyreloadfrombdf6d50aPID63020;pause-dev-apiheldwhilewarming. NexttwoEnglishgrade
checksmeasureactualbrevityandretainedconditions,thenrestorekeepaliveandhandofffree3217forowner.
Finalfocusedliveproof: candidatea52c73c1 exactB13TLansweredChartercontinuingregistration;IDTG
usesnatural'mag-reportkasaOSAS';INCEN/TGanswered. Candidatebdf6d50a grade16ENanswered1399chars
(prior9581output2948,52.5%shorter);grade15ENanswered1625chars(prior2179,25.4%shorter).
Bothretainmethod,approval/fee/prerequisite-enrollment/forfeitureclauses,allsourcequalificationnotesand
explicitdeadlineconflict. Nooveralllatencyspeedclaim. Final174focusedtests pass;registration341.
CurrentAPI PID63020wrapper,bdf6d50a+gradebudget5120. pause-dev-apiremoved,monitorrecoveryenabled.
Freshmain3216/chat,dev3217/chatand8022/health/ready200. Three-secondhealthproxyprobestimedout,
but15swebchecksreturned200; do notcalltheseanoutage. Noautomatedmodelbatchcontinues.
RemainingR3engineeringworkdelivered;fulllanguages/curricula/72-casefrozenevaluationremainsunperformed.

Roundthree export received `E:/Hawksprey/Downloads/Bintanong_AI_Export_2026-11-06_1227.csv`, SHA256
`e7f9bb65ed9a3b339bb550221e786c6725bd3dddb328ddd35da580715fd70402`. 72rosterrows,21retested:
20Y/1N,51untested;13fixed/7unchangedpass/1regressed. OnlyN B-13-TL returnsfreshmanadmissioncredentials
fornext-semesterenrollment. Sixgrade4/INCYmarksareconditionalpassespernotes: reduceverbositywithout
hidinginconsistency. IDTaglishwordingneedspolish. Policy10notecorrectsinitialprod/mainmixuptodevY.
Preserveallmarks,donottransformsharedrownoteintoanotherlanguagefailure. Sourceaudiencefreshmanundergrad
isnotSHSmerelybecausehighschoolcredentialsarelisted;wrongcontinuing-studentcontextistheregression.
Ownerstilltests: noautomatedmodelqueries/restarts. OfflineworkertracesB13TL. Notanoverall72accuracy.

Last full snapshot: `29e0945b` (`git show` recovers the earlier diagnosis). No new phase or push.

- Round two: 33 retested, 20 Y / 13 N, 39 untested. Export SHA-256
  `ac426d1b43ec172b7beff9854ed225e44cf42ca051549b1e88c14b2a1d7d7268`.
  Three regressions: B-14-TG and B-15-TL/TG. Marks are owner observations, not adjudicated accuracy.
- Owner requested parallel repairs. Workers covered generation, runtime context, registration/ID and review.
  Shared inference stays serial. Main gathering checkout/server code and sealed sources remain unchanged.
- Owner audit proposal is preserved unchanged in `2026-11-06-deferred-audit-remediation-proposal.md`,
  hash `93a06cce464e5d69a1647d81a2bf46b61e5a9fa02a3554412309a9f148a20a95`.
  Its wider PR, corpus and integration work is explicitly deferred.

### Delivered code

- `5c5f1093`: compact reviewed program aliases; Forensic target works. Related gate 217 passed.
- `53e4fd81`: prerequisite listings omit unsolicited eligibility invitation. Gate 50 passed.
- `29c7c1a3`: compiled generic policies stay documentary; named course/term Hybrid checks preserved.
- `1ba98d82`, `1bebd24e`, `ac5d4f65`: reviewed document context, procedure preference, compact menu,
  bounded meaning summary, Filipino possession hint with calendar-date negatives. No verified grade invented.
- `e1abe4d3`, `07528080`: bounded completeness retry, facilities companion quotations and style repair.
- `e5cfce72`: more than four routing contexts no longer erase the subject; prioritize distinct reviewed
  purposes within the same four-item budget. Conflict notes stay attached; source fields are not truncated.
- `3991688e`: full grade procedure coverage and honest inability-to-verify fallback instead of claiming
  that a policy is absent from the corpus.
- `9bef074e`, `f110e9b6`: exact original-span Pano/Paano and style-only initial-capitalization repairs.
  Codes, grades, changed words and ambiguous spans remain strict. Related gates 190 / 172 passed.
- `9ef5b0e8`, `6f830de2`: preserve claim-to-record purposes; after a failed coverage check, quote requested
  records separately before ordinary conflict/context/cutoff rewriting and relevance/support review.
  Mixed citations previously lost independent approval text during timing-group replacement.
- `5b162803`: whole prerequisite policy uses its complete clean reviewed body; ordinary review remains.
- `9581df1f`: owner pointed to INC section 3.4. Select the requested mark's printed removal heading plus
  shared approval/forfeiture conditions: INC two records, grade 4 four records. Unasked duplicate timing
  group is excluded. Deadline detail requests and explicit source-gap questions retain their limits.
  RED 3 failures; worker 150 passed; final combined routing/generation gate 159 passed.
  Live scope selection is correct, but reviewed required neighbors still include the other mark's text.
  INC EN draft incorrectly paraphrased grade-4 re-examination outcomes as INC. Do not count the `answered`
  status as correctness. Worker is fixing source-bound mark quotation; grade4 reply length fell to ~2200
  characters, but INC correctness must pass before calling the cleanup complete.
  `af770128` nowconstructsmark-specificexactbody+sharedapprovalquotations beforeexistingrewrites,
  preventingneighborgrade4paraphrasesfrombecomingINCrules. SyntheticREDreproducedwrongINCrule;
  focused79checks pass. LoadingonlydevAPI PID46352; liveconfirmationpending.
  OwnerrequestedLunasubagentCodexstatusandbothstackkeepalive;Lunamonitorshealth/restoresmodel/frontends,
  rootownsdevAPIreload. CodexCLIhasno`status`subcommand; supportedauth/doctorchecksnotusageUIclaims.
  Liveaf770128: EnglishINC andgrade4answered withcorrectexactsections; TaglishINCreviewer rejected
  completequotedmethodwhileaskingneighboringcontext. `e7e6b2a0` clarifiesmark-specificreview scope,
  preservingallclaimsupport/source-limit checks;95relatedtests pass. Reloadwarming.
  Luna: Codex0.166.0ChatGPTlogin; doctor0failedchecks (notusageallowance). Four-hour monitorPID9452
  atignoredp12dev-language-20261105/keepalive-monitor.ps1, logkeepalive-health.log. Two misses,
  absentlistener/ownerprocess and180scooldownbeforerecovery; no503warmingrestart. Main3216/8021,
  model18088 anddevfrontend3217fresh200;8022warming. pause-dev-apisentinelmustberemovedafterreload.

### Runtime and live evidence

- Candidate launcher is ignored `audit-evidence/p12dev-language-20261105/start-candidate.py`.
  Temporary rate window stays zero on 8022 only; main/default limits are unchanged.
- Measured all nine grade records: budget 3072 and 4096 emitted only five; 5120 emitted nine,
  4367 SEA-LION context tokens, no gaps. Launcher derives a package copy with grade budget 5120.
  Sealed package unchanged; computed research release becomes `1d4eeb3b6bb7b8e0`.
- Model and development API/frontend were restored after being stopped across runtime changes.
  Some combined startup commands were policy-rejected without a specific rationale; separate narrow
  starts succeeded. Do not claim a continuing approval block. Current 9581df1f API is warming.
- On `6f830de2` + budget 5120, all 13 prior failure variants returned `answered`: rows 10 Fil/TG,
  13 EN, 14 all, 15 all, 16 EN/TG, 17 TG, 18 TG. These are runtime acceptance observations, not a
  new accuracy score. Source conflicts and missing removal-form location remain explicit.
- General-policy paraphrases still omitted conditions despite an accepted review. `5b162803` was then
  live-verified EN/Fil/TG with the complete policy body. Do not grade status alone as correct.
- Grade and INC answers were very repetitive. The newest mark-scoping fix needs live verification;
  it addresses excessive source selection, rather than stripping validated text in the frontend.
- Evidence: ignored `benchmark-fixes-20261106/candidate-*` JSON/SSE, `api-call-*`, `api-error-*`,
  retrieval trace and `grade_budget_probe.json`. HTTP timings exclude browser/network end-to-end claims.
- Integrated suite was segmented: 697 passed before an old attempt-count assertion; corrected group
  passed. Remainder 723 passed before a pre-existing unknown-course wording assertion; later tail 598 passed.
  No single full-suite pass. New focused gates passed; no full 72-query rerun or browser acceptance yet.

### Next action

INC/grade-4 scope and brevity were subsequently verified through `bdf6d50a` (174 focused tests;
English grade4/INC outputs 25.4%/52.5% shorter). Registration B13-TL and natural ID Taglish also
passed targeted live checks. Final repair handoff `d2ad9fef`; integrated publication to
`origin/p12-evaluation-harness` at `c8cd43c8` passed 585 tests and preserves the remote image.
The frozen full72 run remains pending; no whole-benchmark accuracy or institutional-approval claim.

Continue the [chat self-information index](2026-11-06-system-information-index.md) and
[generic program-shifting repair](2026-11-06-program-shifting-repair.md) from current progress.
Keep source qualifications, undergraduate advisory scope and English/Taglish replies.
Ignored runtime message instrumentation remains diagnostic; remove it after live diagnosis while
preserving benchmark-only rate override and measured grade budget5120.
