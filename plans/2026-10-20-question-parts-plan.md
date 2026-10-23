# Question-parts ledger implementation plan

20October2026;Phase09,p09,baseline8b03dd3. Execute inline with TDD and one fresh
whole-change review. No model observation in this bounded foundation task.

**Capability:** expose which declared part of a student question lacks an answer
or required structured check. **Evidence path:** question spans,request-pinned
prepared RAG evidence,documentary claims and individually mapped part reviews.
**Exit advanced:** master12.4/13.2/14.2 question coverage and decision withholding.
**Question:** can host checks detect a dropped/missing part mapping and prevent
stale/foreign evidence from satisfying it? Extraction completeness remains separate.
Spec:[saved failure](2026-10-20-question-coverage-results.md),scope/source-gap
policies,thesis17-18/39-44 and runtime PNG. Existing Python/Pydantic contracts only.

## Design and boundary

The prior model returned one complete verdict despite omitting a requested fee.
Another prompt edit on that verdict is not the next step. Build a small detached
ledger in generation/requirements.py;do not wire it into Generator or add a profile.
Declare1-8 Requirement records:r1..r8,exact original question quote with start/end
Python character offsets,and kind=document/structured/unknown. No keyword parser,
automatic split or institutional rule is introduced. Quotes are data,not commands.

QuestionPlan binds release and SHA256 of the EXACT original question;validate
offsets/quotes/uniqueness against that text. Host review identity additionally binds
request,language,full documentary cards,plan and canonical draft bytes. A review
contains these two digests,existing SupportReport and1-8 individual PartMappings.
Each mapping is mapped with claim IDs,or unavailable/uncertain with a fixed reason
and no claim IDs. Missing mappings remain explicit unresolved ledger entries;
unknown/duplicate/foreign mappings or claims are rejected. All draft claims must
be mapped to a part,and every part must have a mapping for the ledger to be fully
mapped. Existing draft/support guards and document-only evidence binding still apply.

Structured or unknown requirements always remain unresolved in this RAG-only
foundation;documentary claims cannot stand in for a Prolog check. Revalidate the
IntegrationResult through prepare on entry;nonready/non-RAG evidence is rejected.
An unavailable mapping is an unresolved answer part,not an answered question or a
negative policy decision. Return only a host ledger,never CandidateAnswer or text.

Ledger status all_declared_parts_mapped only states mechanical mapping/support
checks passed for the PROVIDED plan. Its semantic_completeness is ALWAYS unverified;
candidate_only/institutional_use_allowed=false/activation_allowed=false are fixed.
Missing question requirements or an erroneous semantic claim-to-part mapping can
still pass mechanically;write explicit limitation tests. Hash binding prevents
stale/foreign reuse,not malicious semantic false positives. No runtime selection,
source-content decision,latency claim or Phase09 completion follows from delivery.

## Tasks and verification

1. [x] tests/test_generation_requirements.py RED,then requirements.py minimal
   GREEN. Interfaces:create_plan(text,integration,parts),review_identity(text,
   integration,plan,draft),assess_parts(text,integration,plan,draft,review).
   Strict/frozen/versioned Requirement,QuestionPlan,PartMapping,RequirementReview,
   ReviewIdentity,LedgerEntry,RequirementLedger. Reuse AnswerDraft/SupportReport,
   prepare/validate_draft/validate_support;no independently edited policy facts.
2. [x] Cover declared location+fee mapping,mapping dropped/repeated/foreign,
   unavailable/uncertain,structured/unknown never satisfied from documents,unmapped
   claims,all claim support/language/scope failures,private namespace rejection,
   release/query/request/language/evidence/plan/draft replay,strict JSON/extra fields,
   bounds/duplicate spans and multilingual original-offset handling. Include tests
   documenting that omitted-plan parts or wrong semantic mappings remain unverified.
   Add pure helper to assess a supplied review;no renderer or inference caller.
   Verify focused/relevant regressions and commit cohesive code+module guide.
3. [x] Reuse the already saved failed actual-service output OFFLINE ONLY,with
   explicitly author-labeled location/fee requirements. Show missing fee mapping
   yields unresolved ledger even if the old aggregate checker said complete.
   Contrast a deliberately omitted fee requirement to disclose extraction risk.
   No new questions,benchmark execution,model call,DB or source modification.
4. [x] One independent review,one focused TDD fix pass for important findings,
   explicit55-selection regression gate,dated results and compact progress/
   checkpoint/index. Keep actual semantic failures open;preserve raw evidence.

Existing readiness Python3.13 -B pytest -q -p no:cacheprovider;ignored workspace
TEMP/TMP/basetemp under audit-evidence/p09-question-parts-20261020/. No installs,
downloads,DB/dependency/lock changes,model/service startup,training or latency sweep.
Selected scoped/canonical/separate stays;covered/guarded remain unselected. Read
[saved timing recommendation](../Context/response-time-recommendation.md);accuracy
first,one-week cap and all undergraduate/read-only/structured-Prolog/privacy/
source/release/phase boundaries persist. No Phase10,push,merge or deployment.

## Review focus and next gate

- A source-supported location claim must not mechanically erase the declared fee.
- No review may apply to a different question,request,draft or evidence release.
- Review/plan strings cannot invent a structured decision or runtime authority.
- A positive ledger must never be presented as semantic completeness or an answer.
- Extraction of every requested part and semantic correctness of each mapping need
  separate future evidence. This foundation supplies neither;do not promote it.

Ruling:owner continuation authorizes this bounded reversible implementation.
Cost if this foundation proves unsuitable:replace an unconnected helper;selected
runtime is unaffected. Prefer one tested interface over another speculative profile.

Tasks1-2:68expected missing-module assertion failures1.63s;GREEN68passed0.71s;
generation regressions296passed3.64s. Exact commands/logs in ignored question-parts
root:red.log,green.log,relevant.log. No selected runtime changes. Nested records
inherit their enclosing schema version,matching existing contract conventions.
Task3:assess_saved.py checked3author-labeled scenarios using only saved bytes;
missing fee unresolved,omitted extraction/wrong semantic mapping still mechanically
mapped and always unverified. Full receipts:saved-output-assessment.json. No inference.
Task4:one fresh review722cc6e..f106070 found no actionable defect;175passed2.59s.
No fix pass required. Explicit55-selection gate2156passed/66subtests90.82s,exit0.
See [results](2026-10-20-question-parts-results.md) for limits and recovery evidence.
