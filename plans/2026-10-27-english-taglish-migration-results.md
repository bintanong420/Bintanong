# English/Taglish reply migration — implementation and observations

Implemented at`28edea4`;[plan](2026-10-27-english-taglish-migration-plan.md),
[owner decision](2026-10-27-english-taglish-response-decision.md).
English input targets English;Filipino/Tagalog and Taglish inputs target Taglish.
Input families/accepted question wording remain supported. This implements the
new target policy;it does not establish universal language accuracy or faster
student-visible answers. Expanded465/selector remain inactive.

## What changed

- Style wirev2 offers english_only/taglish/unknown;Taglish requires literal Filipino
  evidence and allows zero English fragments. Oldv1 inference packets reject.
  Combined wirev4and promptv6use the same evidence rules;router promptv22separates
  the input-family label from reply style. Unknown/grounding guards remain.
- Removed the obsolete Filipino-versus-Taglish English-word injection floor. The
  existing English-only-with-Filipino-function-words floor remains;no keyword
  routing or invented English fragment is introduced.
- `generation.prepare()` maps legacy`fil` reply requests to`taglish` before draft,
  support and ledger identities. The original IntegrationResult is unchanged.
  All live host result/control/clarification/thank-you lines therefore use the new
  target. Old record parsers/detached rendering dictionaries remain for historical
  compatibility;they are not a new model reply choice.
- New model-generation schemas exclude`fil`;draft/scoped/parts instructions and
  repair guidance use English/Taglish while retaining accurate English terms and
  quotations. Unsupported-language notice distinguishes input languages/replies.
- Evaluation reports identify`english-taglish-20261027-v1`,authored versus policy
  expected reply style and optional authored input family. Missing input-family
  metadata stays explicitly unprovided;do not infer it from a Taglish reply.
  Historical raw traces/results/case wordings are untouched. Current synthetic
  expectations change only the owner-revised reply target;source/citation/decision/
  hold/assertion coverage remains.

## Test and review evidence

Regression-first tests cover Tagalog-only evidence without English fabrication,
English/Taglish/unknown targets,retired wire rejection,separate/combined routing,
control/Prolog/document outputs,source/canonical decisions,normalization before
review identity,and evaluation input/output separation.

Initial RED13included five invalid control fixtures missing understanding. After
repairing fixtures,generation-only RED7confirmed old output behavior. Additional
schema,prepare and input-family RED1each observed,then GREEN. One scripted reviewer
fixture incorrectly assumed schema_version on a confirmation packet;replaced with
the existing per-part model fixture before treating it as behavioral evidence.

Broad routing/generation/orchestration/API suites1235passed32.93s. Independent
review caught a stale router instruction claiming input language equals reply
style;fixed in routerv22. Final independent104tests pass7.27s,no blocking finding.
Subsequent broad1236passed/1old prompt-version assertion;updatedv21->v22without
changing operation/meaning assertions. Final changed-area114tests pass6.00s.
Full project suite at frozen28edea4:**6974passed/1595subtests,6skipped,2xfailed,
6warnings,1382.84s(23m02s),exit0**. Skips:four Windows symlink privilege checks,
one unavailable CUDA/OCR extra,one absent historical dataset. Two known refused
photo-layout cases remain expected failures. Existing Starlette/httpx/Docling
deprecations and root gpu-marker warning remain. Docs/phase30passed/14subtests15.40s.
No installs,dependency/lock/model changes or new lint tools. Static/lint tools
remain unavailable as disclosed in prior checkpoints.

## Bounded actual-model observations

Eight saved expanded-menu questions from the prior source-context run,one attempt
each. Three additional synthetic one-document generation cases,one per input
family. These are development observations,not final benchmark accuracy rates.

| Saved routing request | Current route/control | Reply target | Total routing seconds |
| --- | --- | --- | ---: |
| Another TOR copy,English | RAG,same visible service claim | English | 21.16 |
| Same task,Filipino | RAG,same visible service claim | **Taglish** | 15.55 |
| Same task,Taglish | RAG,same visible service claim | **Taglish** | 14.36 |
| Passing grade | RAG,printed3.0mapping | English | 18.49 |
| Borrowing and TOR copy | RAG,both visible service claims | English | 22.82 |
| Graduate admission | Unsupported-scope refusal | English | 18.16 |
| CC5prerequisites in BSCS | Clarify,no catalogue supplied | English | 21.98 |
| Step1after TOR | Invalid-reference withholding,one repair | English | 27.74 |

All eight reply targets match the authored input families under the new policy;
guarded failure is not a correct substantive answer. Raw Filipino TOR style has
english_fragments=[]and its exact Filipino question as evidence;no English was
invented. Source subject/claims remain the same as the preceding corrected run.
The existing document-only/course-reference failure remains;this migration does
not silently erase invalid references or claim that follow-ups are repaired.

Synthetic documentary generation:English13.05swithheld(`parts_unresolved`);Filipino
12.44sand Taglish11.19sreturned Taglish replies quoting the supplied English
“Fictional policy.” text. The English draft was source-supported but the independent
reviewer judged it did_not_answer;ordinary relevance validation withheld it.
Report this variation;do not count the withheld English result as answer success
or an established language regression from one case. Synthetic source text alone
does not validate institutional answers. Host/control/Prolog style coverage is
synthetic-test evidence,not a newly executed real Prolog/HTTP/browser observation.

## Capacity and response-time limits

Style input dropped by**95exact Gemma tokens**on each matched saved request:
now727–738versus prior822–833. Detailed routing added22tokens for the explicit
input/reply distinction;selector messages/counts unchanged. Normal request still
uses selection,routing and style calls;there is no removed validation/inference
stage. Eight routing cases used25calls,including one bounded repair;synthetic
generation used six calls.31physical calls total,zero transport/overflow failures.
Largest observed input5772(selector);largest repair5017. All fit8192with768output
and8margin. This is not proof that every long/multipart request fits.

Same resident Gemma4E4B UD-Q4_K_XL,llama.cppb11723-31288c9c6,one slot,8192context,
768output,temp0/seed0,prefix cache on,reasoning none with thought opener banned.
Stage style3.28–4.28s;total saved routing14.36–27.74s. No controlled repeated paired
latency comparison was run. Runtime/cache warmness and overlapping host tests vary;
fewer prompt tokens are measured,student response-time improvement is not.
Timers include local HTTP/template/token preflight/inference;exclude startup,
Supabase/retrieval/actual Prolog,HTTP API/session/queueing and browser/rendering.
Synthetic generation timers include its own draft/review calls only. No browser
end-to-end SLA or15–20s target achievement is claimed. Accuracy-first rules stand.

## Boundaries and next action

Active corrected78package/pin hashes freshly match their recorded identities;
no source/hosted/release,frontend,private-data or model/dependency changes.
New code applies the owner-approved reply targets without activating expanded
sources. Pending service/image bindings,context budgets,hosted normalized draft,
institutional-release and complete answer-quality checks remain.
Next focused correction:separate document-only context from course availability
in the follow-up grammar,then replay the exact saved step1failure and accepted
follow-up regressions. Preserve all source/unknown/privacy guards and phase gates.

## Recovery

Evidence root:`C:/Coding-projects/bintanong_workspace/audit-evidence/p11-reply-policy-20261027`.
RED/green/regression/review logs,`observe_policy.py`,11raw observation JSON files,
observation log/summary,full-suite log/exit receipt. SharedPython3.13with`-X utf8 -B
-m pytest -q -p no:cacheprovider`,external basetemp;full suite adds`-rs tests`.
No new source/benchmark wording approval is inferred. No Phase11completion,
Phase12advance,public deployment or school approval.
