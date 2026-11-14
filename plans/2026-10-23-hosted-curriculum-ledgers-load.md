# Hosted curriculum ledgers load

23 October 2026. Owner: "make sure this is also being made on the supabase hosted"; approved applying
the migration and loading ("Yes, apply and load").

## Delivered

- Migration `supabase/migrations/20261023090000_phase9_curriculum_ledgers.sql` (`23882db`): tables
  `curriculum_ledgers` (verbatim reviewed ledger; check binds digest, program/curriculum scope and
  `activation_allowed = false`) and `release_curriculum_ledgers` (release link, one ledger per
  curriculum). Runtime roles (anon/authenticated) may only SELECT rows linked to an active research
  release; no runtime writes. Applied to hosted project `jyrudbiuajahsucsorco` via Supabase MCP; the
  stamped version was reset to `20261023090000` (repo file version). Security advisor: no lints.
- Runtime reader `backend/bintanong_runtime/hosted_curricula.py`: `load_release_curricula` reads the
  active research release's ledgers as runtime and rebuilds each one; altered/mislinked ledgers are
  refused. Tests: 5 database (actual roles), 6 reader.
- Loader `audit-evidence/p09-curricula-load-20261023/load_curricula.py rehearse|hosted`: inserts the
  reviewed ledgers (service role), links them to the release, reads back as runtime, checks each
  ledger and Prolog bundle equals the reviewed file. Inputs byte-checked before/after.

## Result (hosted, release `p09-research-selected-20261022`)

9 curricula, 502 courses, all read back equal with equal Prolog bundles (rehearsal identical):
BSA 77 (`a5f4e220`), BS Criminology 65 (`2561f3e6`), BSIT 53 (`79c02726`), BS Env Sci 50 (`a4d2bc85`),
BS Bio Med Bio 48 (`8448bbba`), BS Marine Bio 50 (`ae315f58`), BSCS old 54 (`8673e40d`), BSCS proposed
55 (`8131643a`), AB Communication 50 (`0a0e0fd1`). Full BSCS ledgers supersede the Phase 06 subsets
for loading. Sources were not marked approved; nothing existing was changed.

## Not yet done

The chatbot pipeline still builds its curriculum runtime from the Phase 06 BSCS ledger files; wiring
it to `load_release_curricula` (all hosted curricula, program/curriculum selection) is the next step.
Later program reviews are loaded with `load_curricula.py hosted <name>` after review.

## Chatbot wiring (23 October 2026, owner: "ye lets proceed")

- `fb2866b`: one research release serves several reviewed curricula. `build_multi_research_resources`
  (backend/bintanong_runtime/research.py) builds one runtime per curriculum; the pin lists each
  curriculum's own release identity and rule-bundle version (`ReleasePin.curricula`); checks run on
  the curriculum named by the request (`MultiCurriculumSymbolicAdapter`); integration admits a result
  only with that curriculum's pinned identity. Catalog = union of reviewed curricula (course matching
  stays program/curriculum scoped; program/curriculum come from the request context, else clarify).
- `6f03016`: answers carry printed-code labels only for courses they mention (502 labels exceeded the
  256 an answer may carry; every request failed before this fix).
- Wiring check (workspace `audit-evidence/p09-multi-curriculum-20261023/smoke_hosted.py`, not a counted
  benchmark): curricula loaded from hosted with the runtime role, accepted thesis wording "Pwede ko
  bang kunin ang CC5 kahit bumagsak ako sa CC4?": BSCS old -> ineligible (CC 4/L failed); BSCS
  proposed -> clarification (its CC 5/L needs CC 3/L + CS 2, not CC 4/L); BSIT -> ineligible. Warm
  component 20.7-24.1 s each (student end-to-end latency not measured).
- Counted roster runner still uses its recorded file-based setup; switching counted runs to the
  hosted multi-curriculum release needs a protocol update before the next counted run.
