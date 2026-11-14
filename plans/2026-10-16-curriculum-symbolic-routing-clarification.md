# Curriculum facts, Prolog and retrieval — 16 October 2026

The owner's suggestion agrees with the intended architecture: reviewed curriculum
relationships and supported eligibility checks belong in structured knowledge and
the symbolic layer. They should not depend on vector similarity to decide whether
a prerequisite was satisfied. A whole prospectus also contains explanatory text;
its presence in retrieval is compatible with keeping its formalizable content as
facts/rules. No quantitative claim about “most” of the corpus has been established.

This is a reconciliation of existing requirements, not a new executable rule or
permission to start Phase 06. Baseline `d2abc8d`, unchanged product `232a418`.
The ledger's canonical master is
[master_implementation_plan_original_long.md](master_implementation_plan_original_long.md).
No tracked `master_implementation_plan.md` exists in this worktree; the named
original-long master is the one consulted. It remains unchanged.

## Evidence consulted

- Master section 3.1 separates embeddings from rule authoring; section 3.3 defines
  RAG, Symbolic and Hybrid. A supported predicate with sufficiently complete scoped
  facts can run without vector retrieval.
- Master sections 11.1–11.5 define the rule pipeline, source-supported prerequisite
  checks, versioned Prolog bundles, safe typed operations, decision statuses and tests.
  Section 11.1 makes reviewed structured records/specifications the authoring source
  and generated Prolog a reproducible output, avoiding independently edited copies.
- Master sections 13.1–13.2 permit exact provenance retrieval without vector search
  on the Symbolic route, give applicable symbolic results control of the corresponding
  decision, and preserve rule/document conflicts rather than trusting stale rules.
- Thesis physical 17–18 (printed 16–17) supplies scope/privacy/read-only limits.
  Physical 39–40 (printed 38–39) explicitly describes direct symbolic prerequisite/
  dependency checks and symbolic support for open-ended advice. Physical 41–44
  (printed 40–43), including the rendered physical 41 example, shows the illustrative
  CC5/L rule. Physical 55 and 58–59 supplies private-upload and processing context.
- Inspected the actual runtime routing PNG: separate RAG/Symbolic/Hybrid branches
  join evidence before generation. Master section 1.3 already resolves the thesis's
  older generation-before-validation prose in favor of this routing diagram.

## Intended division

| Content or question | Intended representation/use | Boundary |
| --- | --- | --- |
| Course identity, program/version, units, placement and reviewed prerequisite/co-requisite relationships | Structured institutional records; expose the facts needed by supported Prolog operations in the compiled bundle | Scope and original source spans remain attached; no separate hand-edited duplicate |
| Whether documented prerequisites are met, missing prerequisites and affected-course dependencies | Reusable reviewed Prolog rules over the applicable facts and request-local student context | Evaluate only supported checks with known coverage; do not imply official enrollment approval |
| A direct printed prerequisite-code/list lookup such as D1/D2 | Prefer an exact version-scoped structured lookup; a registered Symbolic operation can provide it with source references | The operation must exist and be reviewed before use; these are not newly implemented capabilities |
| Course descriptions, explanations and documented procedures | Retain cited source text for RAG where document context is needed | A paragraph does not become an executable policy merely because it can be retrieved |
| A prerequisite decision together with documented next steps/explanation | Hybrid: symbolic decision plus applicable document context from the same release | Neither path substitutes an unsupported conclusion for a missing result |

“Hard encoded” should mean explicit, reviewed facts and deterministic reusable
rules, not a separate custom rule per course or manually copying every PDF into
Prolog. Generate versioned fact/rule artifacts from the reviewed source records.
Keep originals and their cited text available for explanation and audit. Changes
to a curriculum edition must update the reviewed records and regenerated bundle
together; student-specific facts remain session-local and separate from public
institutional knowledge.

The thesis example is illustrative, not an authoritative PalSU prerequisite chain.
Its unproven-completion behavior must also retain the master's recorded correction:
missing grades or unknown curriculum/coverage produce `unknown`, distinct from a
documented unmet condition. An unknown course with no recorded prerequisites must
not pass by default. A proved failure under one supported prerequisite check is not
a complete enrollment determination. All-of, alternatives, co-requisites and
exceptions require their actual reviewed source semantics.

## Consequence for current Phase 05 work

The retrieval diagnostics and accepted D1/D2 wordings do not determine final
runtime routing. Their current purpose is to measure recovery of complete printed
evidence under explicitly supplied scope. They do not replace the future symbolic
eligibility checks or test an automatic router. The original Architecture/Nursing
eligibility questions remain unassessed here because no corresponding supported
symbolic result has been run; Nursing's course-name equivalence also remains open.

In the next evaluation plan, name curriculum retrieval tests as component probes,
separate from future Symbolic/Hybrid capability and route evaluation. Do not count
an unnecessary vector-search path as a final product requirement or force every
course question through RAG. Distinguish end-to-end routing performance from the
conditional retrieval metrics; do not choose final routes from gold evidence IDs.
No automatic interpreter, supported predicate, factual equivalence or eligibility
decision is created by these annotations.

The owner's actual approval separately settles D1–D4's 12 wordings/expectations:
[accepted packet](2026-10-16-development-calibration-proposal.md). Preserve all 75
accepted strings, existing 63 observations, vectors and seals. Next prepare the
versioned development evaluation plan with component-purpose annotations and
explicit source/register versions. No further wording confirmation is needed for
these exact variants. Formal Phase 05 Tasks 4/6/governance remain open; no Phase 06
advancement, generated executable Prolog or activation occurred.
