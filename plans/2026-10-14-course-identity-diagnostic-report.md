# Curriculum course-identity diagnostic — 14 October 2026

An explicit target-course filter removes the recorded CC5/practicum mismatch in
the six existing controlled edition tests. This establishes a candidate approach;
automatic query-role extraction and reusable runtime integration are still absent.
No product code, question, source payload or school approval was changed.

## Correct question attribution

The exact thesis question **“Pwede ko bang kunin ang CC5 kahit bumagsak ako sa
CC4?”** is case `cs-cc5-failed-cc4-tl` and already ranked old CC5 first (0.534219).
The failed paraphrase is **“CS student ako: pwede ko bang i-take ang CC5 kahit
failed ako sa CC4?”**, case `cs-cc5-failed-cc4-taglish`. Its unfiltered top row was
old practicum (0.583309), ahead of proposed CC5 (0.582294) and old CC5 (0.571793).
The preceding report incorrectly attached the latter scores to the exact thesis
wording. Commit `01d30b7` corrects that narrative; sealed observations and queries
were already correct and remain unchanged. This is a reporting correction, not an
extraction error or a revised benchmark expectation.

## Mechanism and measured comparison

The existing catalogue filters program and curriculum, leaving two BSCS rows in
each edition; cosine alone prefers practicum for the Taglish paraphrase under the
old edition. A separate identity view binds each of the eight reviewed candidates
to its `course_code` field, original spans and review event. It does not use course
codes from prerequisite or condition fields. Metadata keys normalize case and
whitespace only, preserving punctuation and leading zeros. For combined printed
codes such as `CC 5/L`, the diagnostic also exposes the base `CC5` key while retaining
the complete printed code and row. These are experimental matching keys, not
university canonical IDs or separately invented lecture/laboratory requirements.

The three accepted CC5 questions receive an explicit researcher target hint `CC5`
from their wording. They retain exactly the same vectors and cosine scores. Each
old/proposed-edition hypothesis runs the existing scope selector first and then
matches the target code against the reviewed identity field before ordering by
the saved cosine scores. No gold chunk ID is supplied to the filter.

| Existing variant | Old edition: top row before → after | Proposed edition: top row before → after |
| --- | --- | --- |
| English | Old CC5 → Old CC5 | Proposed CC5 → Proposed CC5 |
| Exact Filipino thesis wording | Old CC5 → Old CC5 | Proposed CC5 → Proposed CC5 |
| Taglish paraphrase | Old practicum → Old CC5 | Proposed CC5 → Proposed CC5 |

Expected-course top-one recovery improves **5/6 to 6/6 controlled branches**.
These reuse three questions twice and are not six independent student cases.
Six complete CC5 candidate contexts reproduce the prior complete rendered strings
and 78 citation bindings, fitting 2048 tokens at **1209 or 1680 tokens**. Context
assembly reused prior exact token counts only when the entire rendered string was
identical; the encoder was not reloaded and no token count was approximated.

Eleven executed technical controls check formatting, code boundaries,
prerequisite-only mentions, wrong program/version and curriculum ambiguity.
`CC4` matches no target-course row despite appearing in an old CC5 prerequisite
field; this does not establish that CC4 has no prerequisites or is absent from the
full curriculum. `CC50` and `CC05` do not match `CC5`; `AD2` does not silently become
`AD-2`. A twelfth design case records the requirement that unresolved roles return
`needs_target_course` rather than choosing the first mentioned code; this is not an
executed query-role extractor test. Controls are not added owner benchmark questions.

## Verification and remaining limits

Independent checks bind eight course rows to 13 course-code source spans, reproduce
all six score selections, check 78 complete citation bindings and verify the exact
question-to-case attribution. All six original prospectus hashes and **1333 current
dependency/artifact hashes** remain unchanged, including the preceding 30-file seal.
The prior 12 explicit-edition positive rankings remain unchanged. No new vectors,
global threshold, runtime release, Prolog rule or eligibility answer was produced.
Documentation/ledger checks: **453 passed, 11 subtests passed in 10.80 seconds**.
Phase validation exits0; advancement exits1 as expected while formal gates remain
blocked. Twenty-four files and five unchanged product digests are sealed; manifest
SHA256: `f14071290077f54d2bcb1ae45bbc906859f8bf3525a700e065574e245554d454`.

Executed with the existing Python3.13 environment: ignored `run_diagnostic.py`,
`replay_contexts.py`, `verify_diagnostic.py`, and `seal_evidence.py`; each result/log
is retained in the evidence folder. Documentation command:
`python -B -m pytest tests/test_docs_hygiene.py tests/test_contracts_fix3_docs.py
.agents/skills/bintanong-phase-handoff/tests -q -p no:cacheprovider --basetemp
C:/Coding-projects/bintanong_workspace/audit-evidence/p05-course-identity-diagnostic-20261014/pytest-doc-ledger`.
No product changes warranted repeating the product suite.

All six actual Q2/Q12 BSCS cases still need curriculum clarification. Researcher
course hints do not supply a student's edition. The 18 policy variants remain
unranked with unresolved candidate applicability. School authenticity/current-SY/
source-use validation remains deferred; prior owner content/cohort decisions stay
settled. No new human verification is required for this diagnostic.

Next implement a reusable offline candidate course selector under synthetic TDD,
binding its identity index through the existing fully reviewed preparation contract
and accepting a separately supplied target-course hint. Test source/binding changes,
unknown codes, target-versus-prerequisite roles and curriculum ambiguity. Preserve
the existing selector's default behavior. Automatic multilingual extraction and
institutional runtime activation remain separate work; no regex guess should be
presented as a completed intent/entity pipeline.

## Evidence and recovery

Plan: `2026-10-14-course-identity-diagnostic-plan.md`, commit `01d30b7`.
Product baseline is unchanged `093ea4a`; the previous experiment closure is
`0456ba6`. Scripts/results/identity views and logs stay ignored under
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-course-identity-diagnostic-20261014/`.
[All three existing CC5 questions and six controlled results](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-course-identity-diagnostic-20261014/CC5-QUERIES-AND-CONTROLLED-RESULTS.md>)
show exact wordings and scores. Source matching keys can be rebuilt or discarded
without changing original evidence, vectors or the recorded baseline.

Context consulted: actual thesis physical17–18 (printed16–17), runtime routing PNG,
master section10.2, undergraduate scope/source-gap policies and dataset-location
guide. No discrepancy. Existing PDFium was used after unavailable PDF reader imports;
no package was installed. Incoming memoranda remain pending; further college-specific
Charters are excluded. Formal Phase05 completion and Phase06 advancement remain gated.
