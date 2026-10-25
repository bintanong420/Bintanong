# Repeated prerequisite-coverage fallback diagnosis

Owner reported the Taglish candidate-preview/clarification reply listing21 unresolved
courses. This task diagnoses the response, without changing sources or product behavior.

## Reproduced causal chain

1. curriculum_runtime.pl dependencies/4 (lines83–94) finds known potential dependent
   courses, then collects EVERY unresolved/draft course in the supplied curriculum,
   even without a known dependency path to the requested course. This is conservative
   completeness accounting: an unknown rule can contain an undiscovered dependency.
2. Any such unknown marks the dependency listing partial. integration.py assemble maps
   partial to unknown; the rule gaps are distinct from missing student-supplied facts.
3. generator.py lines86–87 bypasses answer generation for non-ready evidence;
   render.py fallback_status maps unknown to clarification_needed.
4. render.py lines212–228 displays dependent courses only when evidence is ready and
   answer status is answered, but still displays all dependency unknown_conditions.
5. presentation.py humanizes rule_unresolved as the reported fully-reviewed wording.
   The preview disclaimer is a fixed research-mode prefix, not the failure cause.

Synthetic real-Janus -> integration -> Generator -> student_text reproduction passed:
known course-2 depends on requested course-1; unrelated course-unrelated has an unresolved
rule. Result retains known course-2 internally, status partial/unknown, zero missing
student facts, final clarification_needed, and only the unrelated course's warning.
No model inference was allowed in the reproduction. It exactly asserts that the known
SYN201 is hidden while the missing-rule warning for unrelated SYN999 is shown.
Two executions passed. Ignored workspace evidence:
audit-evidence/p11-20261025/prerequisite-fallback-diagnosis/reproduce.py and result.txt.

The saved real24Oct title-live-observation.json independently has the exact21-item
signature, Symbolic/list_affected_courses and control_fallback. It is historical evidence,
not a fresh live-model observation. Original question resolved CC4/L in BSCS2018–2019.
Current user question/curriculum not yet provided; the same output for EVERY question
could also involve routing, which this deterministic dependency reproduction cannot prove.
The exact-question clarification is pending; do not infer all routes are broken.

## Implication and correction boundary

Keep unknown prerequisite coverage unknown: blank/unresolved is not verified_none.
Students cannot fix institutional rule coverage by supplying grades or clicking a
clarification choice. The current response conflates those two kinds of unknown and
withholds useful verified relationships. An appropriate future change would distinguish
source-coverage limits from missing student inputs, show a clearly incomplete known
potential-dependency list where approved, and explain that additional dependents may be
unknown. This must preserve conditional/potential semantics, source citations and the
ban on asserting a complete list or definite enrollment consequence from partial evidence.
No Prolog, answer contract, renderer, source ledger or live service changes made here.
