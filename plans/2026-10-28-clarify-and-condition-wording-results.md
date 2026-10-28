# Router clarify and printed-condition wording:results

Follows the [printed-steps battery refresh](2026-10-29-printed-service-steps-results.md) next actions 1–2.
Evidence (ignored):workspace/audit-evidence/p11-clarify-20261028 (RED/GREEN/focused logs,battery-4/5).

## Added all-of wording (kept)

- d49aa27:`conjunction_errors` rejects a model claim that adds "must be met","all of the following"
  or an "and"/"at" joined to a list marker ("and e)") beyond its cited sources;failing drafts get the
  existing condition repair instruction,now naming both connectives. Shares one counter with the
  9990175 disjunction guard;host-written replies unchecked.
- TDD:RED5fail (missing function) -> GREEN12;wiring RED1fail -> GREEN13. Focused generation
  1354pass/372subtests.
- Live (battery-5,one attempt):cross-enroll-en now "the following conditions apply: a) … e)",
  no "must be met",no "and e)";one repair round,65.1s (was42–45s). Hybrid keeps printed "provided:".

## Shifting clarify (tried,reverted per stop rule)

Selector picks `handbook_shifting`,not ambiguous;router still returns `clarify`.

| Attempt | Change | Live result |
| --- | --- | --- |
| battery-3 (before) | — | clarify,nothing named -> office referral (owner E3) |
| ea6409a,battery-4 | menu grammar:clarify must name an operation/claim/ambiguity | invents ambiguity "Which college are you interested in shifting to?" -> bare "Paki-clarify muna" |
| 8109ccb,battery-5 | after settled selection,no ambiguity-only clarify | invents `list_affected_courses` on "ibang college" -> same bare clarify |

Both reverted (8cce770,eedbc07):each closed escape route moved the model to another,and the bare
clarify is worse than the E3 referral. Grammar-only forcing is not a fix here. Open owner decision
(see current progress). Other cases unchanged across battery-4/5:good moral,library card,entrance
health,leave,Hybrid answered;discipline abstains (long Handbook flow);regressions3/3match.
Warm inner pipeline only;not a benchmark,latency or activation claim. 559stays inactive.
