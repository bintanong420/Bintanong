# Term explanation connective guard — 4 November 2026

Owner observed optional model prose saying OR while the checked term's host text
asked for both prerequisites. `TermCourseCheck` carries flattened violated and
missing conditions, but does not carry `checked.requirement`'s canonical tree.
`term_payload` exposes those flattened needs; the existing term explanation guard
checks names and verdict polarity, not prerequisite Boolean semantics. It cannot
distinguish reviewed conjunction, disjunction and same-term requirements from
that list alone.

Bounded correction: skip the optional model explanation for a term containing
any blocked or needs-information course, including retakes. Return the existing
host grouping, reasons, questions and citations. All-met summaries retain their
optional explanation. No conjunction is inferred, no source/rule is changed,
and no missing tree is reconstructed from a course code or phrase.

Future capability: carry the canonical reviewed prerequisite tree for each term
course through the assessment contract and validate course-local explanations
against it before restoring dependency paraphrases. That schema/host-rendering
work is outside this patch. Existing host rendering of complex prerequisite
expressions has not been expanded or independently certified here.

TDD at the generation seam: RED showed seven failures (model calls/accepted
dependency prose); fixtures exercise actual all-of, any-of and co-requisite
rules in two synthetic program scopes, plus retention of all-met explanations.
Verification commands use Python 3.13, pytest without cache and ignored
`audit-evidence/graduation-term-{red,green}` basetemp directories. Final GREEN
result on integrated main: **25 passed in 56.00s**. Resume also corrected five
new fixture failures: a changed rule/program requires a newly assembled release,
not replacing a term result inside an old sealed evidence bundle. Scope-aware
fixture construction now preserves the same integrity checks as production.
No live model/service/GPU checks.
