# Document-only follow-up context correction

Implementation:`4ba0f41`;baseline:`8394a30`. [Plan](2026-10-27-document-follow-up-context-plan.md).
The default Router now distinguishes a saved document subject from an available,
scoped course. The saved TOR “What is step 1?” failure now selects its reviewed
document claim without producing a course reference or requiring repair.

## Change and regression evidence

Routerp11v23and the displayed schema both enable previous_course_quote only when
the existing previous_turn helper finds a catalog course in the request scope.
Document-only guidance permits a clear continuation,keeps current question quotes,
and requires fresh retrieval. No subject ID becomes a course,grade or evidence.
The host also rejects unsolicited nonnull course quotes when no scoped course is
available,using the existing one-repair budget before withholding a repeated error.
No invalid field is silently discarded and no route is forced.

New12synthetic tests cover document-only/stale/out-of-scope context,display/decoder
agreement,mixed course+document context,missing current scope,unsolicited literal
or internal-ID quote,bounded repair,topic switch,semantic ambiguity and Taglish.
Initial RED:`7failed,5passed,0.94s`,expected schema/reference failures.
First broad GREEN exposed one old scripted fixture exhausting after its newly
required repair;gave it a second output,keeping its never-route assertion.
Updated the old prompt-version assertion to23. Final focused routing/private-
context/orchestration/API/reply-policy suite:`778passed,2xfailed,1warning,27.59s`.
Independent read-only review:`48passed,4.76s`,no blockers;covered existing course,
document and experimental combined tests. Docs hygiene:`10passed,0.85s`.
Full project suite at frozen4ba0f41completed with exit0:
`6986 passed, 6 skipped, 2 xfailed, 6 warnings, 1595 subtests passed in 1379.40s (0:22:59)`.
Six skips:four Windows symlink-privilege checks,one CUDA/OCR extra,one historical
external dataset. Two known refused photo-layout xfails remain;existing deprecation/
marker warnings are retained. No production changes after freeze.
Final docs/phase regression:`30passed,14subtests,12.89s`;phase validation valid,
can-advance remains blocked as expected because Phase11has no complete handoff.
Ruff/Black/mypy/Bandit are unavailable in the existing environment;no installs.

## Bounded actual-model observations

These six author-inspected development probes use the existing inactive146-topic
menu from the normalized465candidate. They are not new accepted benchmark cases
or a routing/answer accuracy estimate. No generated source answer is scored here.

| Request and context | Validated result | Reply target | Calls / seconds |
| --- | --- | --- | --- |
| Saved “What is step 1?”,previous TOR | RAG;charter_tor_copy,printed tor copy fields;no operations/reference | English | 3 / 27.11 |
| “Ano ang unang hakbang?”,previous TOR | Same TOR claim;no operations/reference | Taglish | 3 / 14.38 |
| “Ano yung step 1?”,previous TOR | Same TOR claim;no operations/reference | Taglish | 3 / 13.71 |
| “What is the passing grade?”,previous TOR | RAG;grading_scale,printed grade 3.0 mapping;no TOR carry-over | English | 3 / 18.04 |
| “What is step 1?”,no context | Withheld:topic_selection_unavailable/evidence_unavailable | unknown;no style inference | 1 / 2.74 |
| “What are its prerequisites?”,synthetic scoped course | Literal “it” course reference resolves;proposed list_missing_prerequisites is unsupported and withheld | English | 2 / 14.37 |

The course control demonstrates retained reference handling,not a successful
prerequisite answer. Its operation mismatch remains a disclosed model outcome;
the host did not substitute another operation. Synthetic regression controls
exercise the registered eligibility operation successfully.

Fifteen physical calls,zero repairs,zero transport/overflow errors. Largest input
5772tokens;document interpretation4618and topic-switch5073;style727. All observed
calls fit8192with768output and8margin;not a universal long-request capacity claim.
Same resident Gemma4E4B UD-Q4_K_XL,llama.cppb11723-31288c9c6,one slot,temp0/seed0,
prefix cache on,reasoning none. Model/dependency versions were not changed.

These are local routing wall times including HTTP/template/token preflight and
inference. They exclude retrieval,Prolog execution,generation/review,Supabase,
backend API/session/queueing,cold startup and browser/network/rendering.
No controlled repeated latency comparison or student-visible speedup established.
The prior saved step1used one repair;this replay used none. Do not generalize that
single observed call reduction into the owner’s response-time target achievement.

## Boundaries and recovery

Experimental CombinedRouter remains opt-in/inactive and outside this default-path
fix:its existing schema/prompt path does not implement dynamic course follow-ups.
No source,claim inventory,rule,threshold,private-session or active-release change.
Corrected78research release/39curricula remain active;expanded465/selector inactive.
Active runtime seal SHA256:
`22ceaa15c300a5fc2d8778062a9f19ebb175bee34700f68267ec651a07b34c0a`.
Active pin SHA256:
`5dd2d9c95c3cc96181bdd11d3a24481f1c18a4a5c71284a55316c7d60acecc74`.
Both freshly rechecked unchanged. Existing source mappings/gaps,capacity,hosted-
draft,full-answer quality and institutional/public release gates remain.
No frontend,Phase11completion or Phase12advancement.

Ignored evidence root:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p11-document-follow-up-20261027`.
Contains RED/focused logs,observe_follow_up.py,six raw request/response receipts,
observation summary,full-suite log/exit receipt and verification-seal.json. Tests use existing
Python3.13.7:`-X utf8 -B -m pytest -q -p no:cacheprovider`,external basetemp;
full suite adds`-rs tests`. This correction's plan is verified;phase/release and
complete-answer gates above remain separate.
