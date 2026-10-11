# Repository documentation and development rules

- Maintain Bintanong plans, specifications, decisions, progress and developer handoffs in this repository, including isolated repository worktrees. Do not keep the only current plan in an external scratch directory.
- Start from `plans/INDEX.md` for formal phase state and `plans/ingestion/README.md` for unified ingestion/Phase 6 plans and delivery status. Git and fresh verification outrank historical notes.
- Record implementation discoveries in repository decision records and current status. Preserve the master plan and historical plan snapshots; do not infer phase completion or institutional approval from candidate-code delivery.
- Keep original datasets, private inputs, generated conversions/Prolog/JSON, model caches, test temporaries and raw execution evidence outside Git. External scratch remains appropriate for those artifacts.
- `plans/progress_plans/` is an ignored bulk scratch-copy area. Curate text documents into `plans/` before explicit staging; never stage the bulk tree or use broad staging to publish documentation.
- Preserve owner changes and external workers. Use explicit staging, no attribution, system Python 3.13, pytest without cache and external basetemp. No installs/downloads or dependency/lock changes without an applicable owner instruction.
- Candidate output remains inactive. Runtime/API/Docker work, executable Prolog, release activation and institutional use retain their applicable approval boundaries.
