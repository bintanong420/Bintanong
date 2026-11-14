# Phase11 focused correction: held malformed source conditions

Baseline: approved source-gap policy, undergraduate/advisory scope, Phase11 plan and owner direction
to finish pending quality fixes before frontend integration. This corrects existing behavior; no new
product requirements/PRD approval, source reading, model mode or release activation is introduced.

Observed defect: the saved expanded-release weapon question received an invented usable exception
despite an unresolved `malformed_source_condition` on the cited source. Both generation and the fallible
reviewer accepted it. A trailing defect notice did not make that unsupported interpretation acceptable.

## Scope and tradeoff

In the selected per-part path, before numbering claims/review, mark a model-authored answered slot
`source_gap` if any of its claims cites a document record with an unresolved malformed condition.
Validate all proposed citation identities first; never use suppression to accept foreign references.
Keep unaffected slots and canonical structured results. The final review/ledger binds the filtered
draft, so no reviewed claims are dropped afterward. Host-written fee/grade paths stay unchanged.
Source-gap slots explicitly say the reviewed source is incomplete/unclear in all three reply
languages; missing-corpus slots retain their separate unavailable-information notice.

Conservative record-level guard: a malformed field holds model interpretations of that cited record,
including otherwise usable details, until finer claim-to-field binding exists. Do not guess which
sentence interprets the defective field. Other defects, resolved limits and uncited affected records
must not trigger this hold. No semantic completeness/accuracy guarantee is claimed.

Student capability/evidence path: refuse an unsupported interpretation of a known malformed condition
while answering independent parts through their reviewed evidence. Phase exit advanced: source-gap
safety in g2 live quality. This does not fix router misses, omitted procedure steps, sanction progression
or admission-fraud precedence; preserve those failures and the inactive80-chunk draft.

## Tasks and verification

1. Synthetic regressions through real Generator: all-held slots withhold; mixed held/safe slots keep
   only safe claims, citations and review entries; Hybrid keeps canonical result; language variants;
   resolved/other/uncited limits remain usable; foreign reference still rejects. Run expected RED.
2. Small deterministic change in `part_answers.to_draft`; parse only recorded issue/resolution metadata.
   No question keywords, prompt sweep, extra model call, dependency or source-record change.
3. GREEN focused regressions plus existing generation/ledger/render suites; inspect scope/diff, commit.
4. Review and full `tests/` suite on final code. Reuse saved component/live fixture for a bounded
   current-pipeline safety check if its unchanged composition can be replayed without activation.
   No checker-experiment rerun. A component pass is not expanded-release quality approval.

Commands: shared workspace Python3.13 `-X utf8 -B -m pytest -q -p no:cacheprovider`, external basetemp
and logs under workspace `audit-evidence/p11-malformed-source-20261025/`. Full suite is required,
not substituted by focused tests. No linter installed; retain disclosed limitation. Update compact
current progress/checkpoint with actual RED/GREEN/review/full-suite results and remaining next action.
