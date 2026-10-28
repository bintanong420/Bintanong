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
clarify is worse than the E3 referral. Grammar-only forcing is not a fix here. Owner then chose option A (below).
Other cases unchanged across battery-4/5:good moral,library card,entrance
health,leave,Hybrid answered;discipline abstains (long Handbook flow);regressions3/3match.
Warm inner pipeline only;not a benchmark,latency or activation claim. 559stays inactive.

## Shifting option A (owner 28Oct,kept)

- 04e913f:topic-menu instruction gains one fictional contrast example (moving a locker to another
  building):a procedure question whose topic fits routes RAG;a named destination is context,not an
  ambiguity,course or operation. Base router prompt/hash unchanged. RED1 -> GREEN17;focused692.
- Battery-6:shifting **answered** (Handbook p.45 request-to-shift form,both Deans) but cross-enroll
  dropped to insufficient:the example's "one document part" made the router merge its two questions.
  12ac411 says "document parts as requested" (RED1 -> GREEN18;focused693).
- Battery-7 (12ac411,one attempt):**7/8answered,3/3regressions**. Shifting 33.5s (one printed
  requirement;the checker accepted it as answering the question). Cross-enroll answered as printed
  "conditions apply: a) … e)",76.6s after one repair (slow). Discipline still abstains (long flow).
