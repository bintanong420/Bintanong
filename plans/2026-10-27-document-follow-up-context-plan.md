# Document follow-up context correction plan

**Goal:** a clear documentary follow-up such as “What is step1?” can use its saved
document subject without exposing a nonexistent course-reference capability.
**Baseline:** master23,existing Phase11plan and saved step1failure in
[reply migration results](2026-10-27-english-taglish-migration-results.md).
Existing undergraduate/advisory requirements and owner27Octreply policy retained.
This is a scoped bug fix,not new product requirements or source approval.

## Root cause and design

Router uses previous_turn!=None to enable previous_course_quote. A saved document
subject makes that true even without course_available. The display schema also
uses this broad flag. The model then copies the internal subject ID into a quote;
normalization rejects it and the bounded repair repeats it. Keep that rejection.

Enable the course-reference property only when the existing previous_turn helper
finds a catalog-matched course inside the request curriculum. Document-only context
uses separate guidance:reuse the prior subject only for a clear documentary
continuation;never create a course quote,grade or operation from the subject ID.
Course+document context retains both capabilities and ordinary host validation.
Host rejects nonnull unsolicited previous_course_quote when no course is available,
even if a transport ignores the decoder grammar;one named reference repair only.
Do not silently erase the field,guess antecedents or override a semantic hold.

## Tasks and checks

1. [x] Add synthetic follow-up regressions,observe RED,then minimally correct
   Router/schema display/prompt guidance. Cover document-only/no context,valid
   course,mixed context,stale/out-of-scope course,missing current scope,topic switch,
   ambiguous proposal,repair,unsolicited quote and English/Taglish targets. Preserve
   unchanged single-turn prompt/schema and invalid quote/operation rejection.
2. [x] Replay saved actual step1with same inactive146topics,then bounded natural
   English/Filipino/Taglish document follow-ups,one course control and a topic switch.
   Score subject,claims,operations,route/style separately. Exact token guards apply;
   do not turn routing success into answer-quality evidence. Reuse saved failures.
3. [x] Independent review,focused routing/private-context/orchestration/API tests,
   full project suite at frozen code,docs/phase/diff checks. Update compact progress/
   checkpoint/results and commit verified units. No activation/frontend/phase advance.

## Verification and constraints

SharedPython3.13 `-X utf8 -B -m pytest -q -p no:cacheprovider`,external basetemp
under workspace/audit-evidence/p11-document-follow-up-20261027;full adds`-rs tests`.
No dependencies/models/source/hosted/pin changes. English/Filipino/Taglish inputs,
English/Taglish replies;no private raw transcripts. Thesis17–18scope/routingPNG and
master23consulted on resume. Preserve missing facts as unknown and all source holds.
