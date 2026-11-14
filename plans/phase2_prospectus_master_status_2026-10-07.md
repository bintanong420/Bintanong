# Phase 2 prospectus workstream: master status and hand-over

**Snapshot:** 2026-10-07 (evening). **Written for:** a fresh Claude or Codex session (and the project owner) that must continue the PalSU prospectus extractor work with no memory of the earlier conversation.
**This file is a status record, not completion evidence and not institutional approval.** Git state and fresh test runs outrank every number below. Re-run a gate before relying on its count.

## 0. How to use this file

1. Read section 1 (rules). They override plans, skills and agent files.
2. Read section 3 (the ledger) to see what exists, then section 8 (what is next).
3. Read `C:\Users\Hawksprey\source\repos\Bintanong-wt\CODEX_PICKUP.md`. It has the live queue, exact test commands, Codex prompts and the "UPDATE 2026-10-07" block.
4. Read the memory index `C:\Users\Hawksprey\.claude\projects\c--Users-Hawksprey-source-repos-Bintanong\memory\MEMORY.md` and every file it links.
5. Verify before acting: `git -C <worktree> log -1` and `git -C <worktree> status --short`.

## 1. Standing rules (the owner's decisions; they override everything else)

| Rule | Detail |
|---|---|
| **No AI attribution** | Never add `Co-Authored-By:`, "Generated with ..." or any AI trailer to commits, merge commits or PR text. On 2026-10-07 the trailers were stripped from all local branches and from the 4 public GitHub branches. Older plans still say "add the trailer": ignore that. |
| **No pushing, no force-push** | The owner runs any push themselves. The safety classifier blocks force-push and history rewrites by agents; do not work around it. `dev` is local only. |
| **The main checkout is the owner's** | `C:\Users\Hawksprey\source\repos\Bintanong` is on `dev`. It holds the owner's uncommitted `.gitignore` edit and untracked handoff files. Never `git checkout` there, never `git add -A`, never stage `.gitignore` or `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md`. Do work in worktrees under `C:\Users\Hawksprey\source\repos\Bintanong-wt\`. |
| **Test first** | Write the test, show it red, fix, show it green, run the full suite. Mutation-check critical guards in a scratch copy, never in the worktree. |
| **Strictness** | When ambiguous, refuse: make no proposal, mark the item non-executable, or flag it for a human. Never drop an item silently. When the same area fails a third review, fix the root cause instead of adding another patch. |
| **Nothing approves a curriculum** | Extractor audit success, `EXTRACTED`, `VERIFIED`, or a human review in the ledger is never institutional approval. `eligible/2` must never accept a prerequisite rule that is not fully understood. |
| **OCR review is user-side only** | OCR-derived data becomes "reviewed" only through the uploading user's own decisions, for that user only, session-only. It never touches or promotes into the institutional knowledge base. No staff promotion path. |
| **Question-style review** | User-facing review is one question per item ("Is the subject X with course code Y correct?" Yes / No / Other). The B2 Markdown sheet stays a maintainer tool. |
| **Portable code** | Windows, Linux and macOS: pathlib, LF output, no shell-specific paths. Only Windows has been run. |
| **Docling policy** | Track the latest Docling; any upgrade must pass the 44-input gate. The repo is pinned to 2.133.0. |
| **GPU** | CUDA is wanted (RTX 4060 Laptop, 8 GB). CPU is the default; the GPU path is set up and measured. |
| **PowerShell only** | Git Bash cannot fork on this machine. |
| **pytest temp** | Never put `--basetemp` inside a repo (the fixer's outside-Git guard then fails 11 tests). Use a folder under `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\`, and create the parent first. |
| **Outputs outside Git** | PDFs, generated outputs, images and review folders live on `E:` and never in a repo. |
| **Codex** | Use GPT-6.1 Sol in the VS Code extension (works there). CLI with a ChatGPT login refused 6.1, so `gpt-6-sol` is the fallback. Codex is the overflow when Claude usage is at 90–95%. |

## 2. Where everything is

| Thing | Location |
|---|---|
| Repo (owner's `dev`) | `C:\Users\Hawksprey\source\repos\Bintanong` (`dev` tip `5c34fd7` at snapshot) |
| Worktrees | `C:\Users\Hawksprey\source\repos\Bintanong-wt\` : `b2`, `task13`, `phase-c`, `phase-d`, `gui`, `gui-plan`, `ocr`, `integration`, `d-baseline-641523d` (old baseline, stale hash) |
| Data and outputs | `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\` (prospectus PDFs under `PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main`; cached Docling JSON in `docling_jsonified_output\task2b_standing_isolated_2026-09-29\`; trial folder `review_trial_2026-10-04\`; scratch under `scratch\`) |
| Python | Main venv `C:\Users\Hawksprey\source\repos\Bintanong\backend\.venv\Scripts\python.exe` (the package is not installed, so the worktree's own code is imported when run from its root). FastAPI is missing there, so ignore `tests/test_api_probes.py` and `tests/test_embedding_service.py`. Web tests use `%TEMP%\gui-review-venv`; OCR GPU experiments used `%TEMP%\bintanong-ocr-gpu-venv`. |
| Tools | SWI-Prolog `C:\Program Files\swipl\bin\swipl.exe`; Tesseract 5.5.3 (winget) with the pinned `fil.traineddata` in `%LOCALAPPDATA%\bintanong\tessdata`; Docker Desktop (CPU and GPU OCR images built) |
| Plans | In each worktree's `plans/`. Phase plans: `2026-10-03-prospectus-extractor-package-split.md` (Phase A plus the cross-phase rules), `...-phase-b-markup-twin.md`, `2026-10-04-prospectus-phase-b2-section-fixer.md`, `...-phase-c-status-separation.md`, `...-phase-d-safe-cache.md`, `...-phase-e-rag-provenance.md`, `...-phase-f-tools-cli.md`, `2026-10-04-prospectus-ocr-measurement.md`, `2026-10-05-prospectus-review-gui.md`. Progress: `plans/plan_current_progress/extractor_split_progress.md` (one section per phase). Decisions: `docs/decisions/`. |
| Master plan and sources | `plans/master_implementation_plan_original_long.md` (Phases 0–13); `Context\bintanong_full_runtime_routing_architecture.png`; `Context\bintanong_thesis_for_context.pdf` (extract text with pypdfium2; no poppler) |
| Formal phase ledger | `plans/INDEX.md`: Phase 0 complete, Phase 1 ready, no active formal phase. The prospectus work is a parallel review-only workstream and does not advance this ledger. |
| Backups before the history rewrite | `...\scratch\handoff_0710\prerewrite\` (bundle of all refs, mirror, tip lists, `.gitignore` patch) |

## 3. Sub-phase ledger

Package: `backend/bintanong_tools/prospectus_extractor/` (a shim `bintanong_prospectus_jsonifier.py` re-exports every name).

| Sub-phase | Goal | What was built | Evidence | Status | Branch / worktree |
|---|---|---|---|---|---|
| **A: package split** | Split the 6k+ line jsonifier into modules, 1:1 | 26 modules plus shim, an AST gate, a golden-output check; the only code change is the Docling env re-launch line; legacy parsers in `legacy.py` | 44/44 outputs identical; self-test 80/80 | **Done**, in `dev` | `refactor/prospectus-extractor-package` |
| **B: markup twin** | A computer- and markup-friendly copy of each PDF | `markup.py`: HTML tables with real rowspan/colspan, `data-cell` ids, original Docling text, `--export-md`; reading-order frame fix (table cells TOPLEFT vs text BOTTOMLEFT) | 44/44 course fields identical, exact cell ids | **Done**, in `dev` | `feature/prospectus-markup-twin` |
| **B2: verifier and fixer (HITL)** | Fix broken year/semester rows after ingestion, with a human in the loop | `verify.py` (section health), `fixes.py` (proposals: `strip_banner`, `move_term`, `title_from_pdf`), `placement.py`, append-only JSONL decision `ledger.py` (tamper-evident ids, stale and orphan handling, units and prerequisite corrections, write lock planned in GUI), `sheet.py` Markdown review sheet, `fixer_cli.py`, `materialise`; the raw JSON is never modified | Triage of the 39 distinct PDFs: clean 1 / warnings_only 3 / mixed 18 / broken 17; 67 title proposals, 0 strip proposals; ~12 review rounds; suite 329 on the B2 branch | **Code complete.** Tasks 12 (owner's trial), 13 (banner split go/no-go) and 14 (closeout) pending | `feat/prospectus-phase-b2-section-fixer` (in `dev` via D) |
| **Task 13: banner split** | Split banner words out of code/title cells in the parser | `sections.py` change plus comparer options | 1 title changes (BSEE `AS 1`), 54 courses gain `discarded_fragments`, `banner_leak` 3 to 2, 1 audit message changes | **Built, waits for the owner's go** (after the trial) | `feat/prospectus-b2-banner-split` |
| **C: status separation** | An audit `ok` must never read as approval | Prerequisite states, `authority.py`, `extraction_audit` / `content_review` / `source_verification`, `rule_complete/1` guard, metadata as observations, RAG prerequisite wording, schema v3.1 | 44/44 identical; states: blank_unreviewed 1005, resolved 689, unresolved_reference 253, standing_condition 59, unreadable 20, alternative_or_exception 3, stated_none 2; 494+ tests; last Codex gate NONE | **Done**, in `dev` via D | `feat/prospectus-phase-c-status-separation` |
| **D: safe cache and publish** | Never reuse or publish output built from the wrong PDF or settings | `identity.py` (single PDF-hash owner), identity-checked Docling cache, staged publish with `_publish.json` manifest (cache pair after the main JSON), `failed/` diagnostics with a marker written first, context-sensitive `--skip-existing`, one PDF read per run, LF outputs, short staging paths, schema v3.2 | 986 tests (main venv); 44/44 identical; independent review approved | **Done**, in `dev`. Handoff `plans/prospectus-phase-d-handoff.md` | `feat/prospectus-phase-d-safe-cache` |
| **OCR measurement** | Measure OCR accuracy on photographed prospectuses | `ocr_bench` (seeded photo simulator, scorer with the strict Q11 criteria, engine grid), adapters for Tesseract and RapidOCR, CUDA setup (`ocr-gpu`/`ocr-cpu` extras, CUDA 13.0 torch), pinned `fil` model fetcher, CPU and GPU Docker images with baked models that run offline | All 6 configs ran on a real page; RapidOCR GPU is 2–4x faster than CPU (3 pages); Docling layout and table models ~3x faster on CUDA with identical course fields; 322+ tests | **About 50%, in `dev`.** Remaining: tasks 4b (engine output into the payload through the Docling chain), 4c (bench), confidence matching (Q16), review adapter (question-style), edition matcher, real-data gates, decision record, real phone photos (the owner takes these later) | `feat/ocr-measurement-harness` |
| **Review GUI** | The local researcher GUI the master plan requires (§7.1 step 7) | Tasks 1-11 plus C/S/D/M review fixes committed at `61d251d`; shared builder, ledger lock, question queue, PDF/twin/JSON panes, loopback/token/Host/Origin guards, CLI, Phase C prerequisite review and valid accepted-blank stamping; scripted real-data copies and sheet equivalence | Fresh integration `cf8b11c`: main **1259 passed + 6 skipped + 13 subtests** (4 warnings); web **266 passed** (1081 deselected, 3 warnings); self-test **80/80**; comparer **44/44 identical** vs `5c34fd7`, only package_sha256/run_key changed; B2 **21/3/19/1**, title_from_pdf **67**, strip_banner **0**, unclaimed_code **316**, banner_leak **3**; trial sheets **01/16/33: 0 errors**; diff/trailers **0**; **107 originals unchanged** | **Integration built and gates a-g GREEN; NOT in dev.** Spec: **2 Medium source-pane defects + 1 Low wording ambiguity, no High**; Standards **1 Medium** (no visible transport/save failure), no High. Findings remain open; concurrent materialisation suspicion is UNVERIFIED. Browser/Lighthouse (Task 11 steps 6-7), human Task 12 and owner fast-forward sign-off pending. Nothing here is institutional approval. Evidence: external `scratch\gui_integration_2026-10-07\`; pickup LATE block | `feat/prospectus-review-gui` / `integration/gui-0710` (`Bintanong-wt\integration-gui`, `cf8b11c`) |
| **E: RAG provenance** | Chunks traceable to exact cells and the PDF hash | Plan only: stable chunk ids, token cap (512 with 32 reserve), rejected chunks, schema v3.3 | none | **Planned, not started.** Start from `dev` | plan `...-phase-e-rag-provenance.md` |
| **F: tools boundary** | One CLI, plus Docker and CI | Plan only | none | **Planned, not started** | plan `...-phase-f-tools-cli.md` |
| **Master Phase 1 and Phase 2** | Source manifest and contracts; chunking; ingest Handbook, Citizen's Charter, USG documents; the 10-document OCR check | none yet | none | **Not started.** Phase 1 is "ready" with no plan. Do the prospectus line first (owner's order) | master plan §6–§7 |

**Integration:** `integration/prospectus-0710` merged D (with B2 and C), OCR and the GUI plan into a copy of `dev`; gates passed (1040 passed + 1 skipped, self-test 80/80, 44/44 identical, B2 triage unchanged, 0 trailers), then `dev` was fast-forwarded to `5c34fd7`. The GUI branch and Task 13 are not in `dev`.

### 3b. Master plan Phase 2 (§7) broken down by its own steps

The master plan's Phase 2 is "Data ingestion and chunking" for **all** institutional sources. Only the prospectus slice has been worked. Status of each step, for prospectuses and for the other sources (Handbook, Citizen's Charter, USG/CSG documents, Procedures, photographed posters):

| §7 step | Requirement | Prospectuses | Other sources |
|---|---|---|---|
| 7.1-1 | Validate the manifest entry and keep the original bytes | **Partial.** Originals kept; the PDF hash has one owner (Phase D `identity.file_sha256`) and every run records it. No formal manifest (that is master Phase 1). | Not started |
| 7.1-2 | Inspect whether a document has text, scans, photos or mixed pages | **Not built** as a step (Docling decides). The OCR harness measures photographed pages. | Not started |
| 7.1-3 | Convert with Docling, pinned OCR backend and language; record settings | **Done.** Docling 2.133.0 pinned; conversion settings are part of the cache and run identity (D). OCR language grid and engines built, accuracy not yet scored. | Ad hoc only: earlier `redocling_handbook.py` output exists as Markdown in the Handbook folder's `_rag_index`; not under the pipeline |
| 7.1-4 | Export structure: headings, tables, page locators, provenance | **Done.** Raw Docling JSON, cell ids, page and bbox per course, markup twin. | Not started (formal) |
| 7.1-5 | Clean repeated headers and footers without changing meaning | **Not applicable to tables so far.** Banner words handled by B2 and Task 13 (pending go). | Not started |
| 7.1-6 | Preserve course-code punctuation, numbers, units, table associations | **Done and measured** by the course audit (checks A to D) on 44 inputs, 2031 courses. | Not started |
| 7.1-7 | Review low-quality pages and executable fields; local GUI with PDF, cells and JSON; decision ledger; derive corrected candidates separately | **B2 done** (sheet, ledger, materialise). **GUI in progress** (Tasks 1–9 built, fixes under way, Tasks 10–11 and the owner's trial remain). | Not started |
| 7.1-8 | Chunk by sections, clauses, procedures, coherent table units | **Partial.** Semantic and hierarchical RAG chunks exist; stable IDs, the token cap and rejection of unsourced chunks are **Phase E (planned)**. | Not started |
| 7.1-9 | Export versioned chunk artifacts and an ingestion report | **Partial.** Publish manifests and run identity (D). Chunk artifacts and report: Phase E. | Not started |
| 7.2 | Chunk policy: about 300–400 tokens, hard cap 512 including prefix and special tokens, stable IDs, parent references | **Planned** (Phase E: estimator plus 32 reserve, `estimate-v1`). | Not started |
| 7.3 | Ingestion check: 10 representative scanned documents, manual transcripts, character error rate plus critical-field errors | **Not started** as specified. The OCR harness covers 43 prospectus pages instead; the 10-document check on scanned Charter posters and similar remains a Phase 2 task. | Not started |
| Deliverables | A 39-distinct-PDF prospectus reference set; a two-PDF pilot | **Met:** 39 distinct PDFs (44 paths) are the reference set; 4 prospectuses are the pilot. | n/a |
| Exit gate | Each sampled chunk resolves to the right page and section; no unreviewed critical error reaches rule authoring | **Not met.** Needs the owner's review, the GUI, Phase E and the Phase 1 contracts. | Not met |

**Not-yet-built sub-parts of Phase 2 that need their own plan** (nothing exists for them): the Handbook, Citizen's Charter and USG/CSG ingestion into the pipeline, policy-document chunking, the document inspection step, the 10-document scanned-document OCR check, and the ingestion report for non-prospectus sources.

## 4. Key decisions taken (all recommended options unless noted)

- **Split:** 1:1, cross-platform, mirror repo conventions, legacy code in its own file, self-test moved as-is.
- **B2 (D1–D9):** a Markdown review sheet plus a decision ledger; sheet decision words `ok`, `fix`, `edit: reason`, `unresolved: reason`; the verifier reports section health (clean/review/broken) and prospectus health (clean/warnings_only/mixed/broken); bulk `confirm: yes` only on unflagged rows; the raw file is never modified, corrections are materialised separately; Task 13 needs a human go.
- **C:** `stated_none` (a printed "none", exact forms first, then whole-phrase matching) counts as executable; blank cells are `blank_unreviewed` and never executable; `reviewed_empty` is written only by a human decision; `promotion_status` keeps the legacy `VERIFIED` label.
- **D:** the cache pair publishes after the main JSON (a deviation from the original plan, for crash-consistency); `force_reconvert` defaults to False; a failed audit publishes but is never skipped.
- **OCR (Q8–Q16, O1–O3):** identify the edition, never snap text to a known value; simulated plus real photos (real ones later); the strict four "supported" criteria; the same chain and review format as born-digital; Tesseract eng/fil/eng+fil and RapidOCR en/latin/iso:fil (6 configs); pinned `fil` model from tessdata_best; onnxruntime plus Tesseract installs recorded; confidence by matching OCR text lines to cells; the decision log extended to units and prerequisites; keep the combined `hard` photo condition; score both downscaled and full-size photos; decisions are session-only; edition matching is a Phase 10 deliverable.
- **GUI (D1–D13):** FastAPI plus a static HTML/JS page, loopback only, per-launch token, a ledger lock file (`msvcrt`/`fcntl`, stdlib), a section Yes never overrides a decided row, the GUI and sheet write byte-identical entries, a CI matrix (ubuntu, macos, windows) later.

## 5. Technical facts a newcomer will trip over

- Docling table cells use TOPLEFT origin; text items use BOTTOMLEFT. `SourceBBox.origin` and `page_sizes` carry this.
- The markup twin renders Docling's cell text, not the parser's JSON. A broken row in the twin is a Docling merge, not a JSON bug.
- `own_role_cells` is the one definition of a course's own cells. Strip evidence must be a code/title cell on this row alone, in no other course's provenance, equal to the whole remainder, with no banner wording; the PDF counts only as an anchored span with the code and the remainder each printed once.
- The ledger entry id is a fingerprint of its contents: it catches accidental edits, not a deliberate forger. Float units are invalid (ints 0–99). Stale (old value changed) and orphan (course absent) decisions never count towards review.
- OCR: RapidOCR needs `cudnn_conv_algo_search=HEURISTIC`, `torch` imported first, and a one-crop warm-up, or the GPU is slow or crashes. Tesseract's `tsv` config silently fails when the data folder holds only models; use `-c tessedit_create_tsv=1`.
- Corpus: 43 pages across 39 distinct PDFs (44 paths), 2031 courses.
- Windows: path length (default output root falls back to `<drive>\Bintanong\output` when the home path is long), LF output, byte-0 file lock (the holder text lives at byte 1).

## 6. Gates (commands and the numbers to match)

From a worktree root, with the main venv (`$py`):

- Suite: `& $py -m pytest -q tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider --basetemp "<scratch folder>"`. Expect 1040 passed + 1 skipped on `dev`.
- Self-test: `& $py backend\bintanong_tools\bintanong_jsonifer_prolog\bintanong_prospectus_jsonifier.py --self-test`: 80/80.
- 44-input comparer: `& $py scripts\prospectus_course_compare.py --base-ref <ref> --status-report`: 44/44 identical (only `package_sha256` and `run_key` may change). Put its base worktree outside the repo and remove it.
- B2 triage (scripts in `...\scratch\b2_1_banner_evidence_2026-10-06\`): mixed 21 / warnings_only 3 / broken 19 / clean 1; `title_from_pdf` 67; `strip_banner` 0; `unclaimed_code` 316; `banner_leak` 3.
- Trial sheets 01, 16, 33: a read-only `check_against` gives 0 errors.
- `git diff --check` and "0 trailers" before any merge.

## 7. Review history and what it cost (lessons)

- Reviews were run by Claude `extractor-reviewer` agents and by Codex read-only, in rounds. B2 took about 12 rounds, mostly on one rule (banner-strip evidence) that yields **0 suggestions on real data**. Patches kept finding contrived inputs; the root-cause rewrite (one guard) finally closed it.
- **Rule going forward:** one independent review per batch plus one re-check; send reviews to Codex; stop when real data shows no effect.
- Real defects the reviews caught are worth remembering: forged ledger values accepted; fractional and huge numbers crashing materialise; `none?` and `C.S 1.` read as complete prerequisite rules; unknown source-verification values clearing the eligibility block; a publish crash leaving a set that verified as complete with the wrong raw JSON; the GUI server crashing under concurrent PDF rendering.
- `Reading the docs`: the Claude docs say subagent usage adds up (it does not multiply), the cache lives 1 hour on a subscription plan so a long idle conversation is re-read at full price, `/usage` shows the split by agent, and `model:` can be set per subagent.

## 8. What is next (ordered)

1. **Owner's gates (human):** B2 Task 12 trial review (start with `...\review_trial_2026-10-04\HOW_TO_REVIEW.md`), then the Task 13 go/no-go, then B2 Task 14 closeout.
2. **GUI integration completed at `cf8b11c` (`integration/gui-0710`), 2026-10-07T04:04:36.9127748+08:00:** fresh a-g gates all match: main 1259+6 skipped; web 266; self-test 80/80; comparer 44/44 with only package hash/run key changes; triage 21/3/19/1 and 67/0/316/3; trial sheets 01/16/33 zero errors; diff/trailers zero; 107 originals unchanged. Spec: 2 Medium source-pane defects and 1 Low bulk/prerequisite wording ambiguity, no High; Standards: 1 Medium transport-error visibility defect, no High. Both axes complete; three Medium findings and one Low ambiguity remain open. Report and handoff complete: STOP and ask the owner before any dev fast-forward; recommend holding dev pending fixes. Dev remains `5c34fd7`. Browser/Lighthouse and GUI Task 12 remain pending; no institutional approval. Recovery/evidence: `scratch\gui_integration_2026-10-07\` and pickup LATE block.
3. **Phase E** from `dev` (Codex Prompt 4 in `CODEX_PICKUP.md`; schema v3.3).
4. **Phase F**, then the **OCR leftovers** (after D, as planned).
5. **Master Phase 1** (source manifest, contracts) together with **Phase 2 prep** (chunking, Handbook, Citizen's Charter, USG documents, the 10-document OCR check), following `.agents/skills/bintanong-phase-handoff` in the repo.
6. **Master plan gaps still to close** (found by mapping the OCR plan onto the master plan): no edition-matching in Phase 10 (decided to add), no question-style review endpoint in §16.1, no multi-question Yes/No/Other in §16.2, the master plan pins Docling 2.93.0 (repo uses 2.133.0, policy recorded), no GPU memory budget for Bintu-1 plus embeddings plus OCR on 8 GB, no photo quality gate, no place to record the winning OCR language configuration and the `fil` model as a versioned artifact, privacy rules for a user's decision log (session-only was chosen).

## 9. Skills, agents and tools used (what to load again)

**Skills (superpowers 5.1.0, under `C:\Users\Hawksprey\.claude\plugins\cache\claude-plugins-official\superpowers\5.1.0\skills\`):** `using-superpowers`, `subagent-driven-development` (with its implementer, spec-reviewer and code-quality-reviewer prompts), `test-driven-development`, `verification-before-completion`, `writing-plans`, `executing-plans`, `requesting-code-review`, `receiving-code-review`, `systematic-debugging`, `finishing-a-development-branch`, `using-git-worktrees`.
**Other skills applied:** `grill-me` (decision grilling with recommended answers), `tdd`, `writing-for-agents` (handoff structure), `code-review`, `ponytail` (lazy-senior output rules, session hook), `i-have-adhd` (the owner's reading format: next action first, numbered steps, short), `setup-pre-commit` (invoked once, interrupted; nothing was set up).
**Repo-specific skills:** `.agents/skills/bintanong-phase-handoff` (phase state, checkpoints, handoff artifacts), `.agents/skills/supabase` and `supabase-postgres-best-practices` (for Phase 4).
**Agents:**
- `extractor-implementer` (`.claude/agents/extractor-implementer.md`): one bounded plan task, test first. Run on Sonnet 5.5 (Opus when Sonnet was rate-limited).
- `extractor-reviewer` (`.claude/agents/extractor-reviewer.md`): read-only review of a task or range.
- `general-purpose` (GUI plan writing), `claude-code-guide` (Claude Code docs lookup, run on Haiku), Haiku for a light fact check against git.
- **Codex:** read-only reviews through `codex exec -s read-only`; implementation via the VS Code extension using `CODEX_PICKUP.md`.
- Isolation: git worktrees created by hand (the Agent tool's `isolation: worktree` was refused because of a drive-letter case mismatch).
**Other tools:** Docling, RapidOCR, Tesseract, SWI-Prolog, uv, pypdfium2, Docker, `git filter-repo` (rewrite tested in a mirror clone; the final rewrite used a custom git-plumbing script so that GitHub-signed commits and `main` kept their hashes).

### 9b. Recommended models and effort (what worked in this project)

Model ids available: Opus 5.5 `claude-opus-5-5`, Sonnet 5.5 `claude-sonnet-5-5`, Haiku 4.5 `claude-haiku-4-5-20251001`, Fable 5.1 `claude-fable-5-1`. Fast mode needs paid usage credits and was not available. Set a model per subagent with its `model:` field (or the Agent tool's `model` parameter); subagent usage adds up and is not multiplied, but each agent is a full conversation.

| Role | Claude model | Effort | Notes |
|---|---|---|---|
| Orchestrator (this chat) | Sonnet 5.5 | medium | Keep it light; start a fresh chat from this file instead of letting one conversation grow, because a long idle conversation is re-read at full price after the 1-hour cache. |
| Implementer, routine tasks | Sonnet 5.5 | medium | Plan task with exact steps (docs, wording, CLI, tests, merges). |
| Implementer, hard logic | Sonnet 5.5, or Opus 5.5 | high | Ledger and identity, cache and publish crash-consistency, prerequisite classification, concurrency and locks, security guards. Use Opus when Sonnet is rate-limited or has failed twice. |
| Reviewer (independent) | Sonnet 5.5, or Codex GPT-6.1 Sol read-only | high | Reviews must hunt bypasses and run mutations. Prefer Codex to spare Claude usage. |
| Writing a plan | Sonnet 5.5 | high | |
| Fact checks and docs lookups (git state, usage docs, path checks) | Haiku 4.5 | low | Used for the Claude Code docs lookup and the git-state check. |
| Running gates | none: use scripts | n/a | The suite, the self-test and the 44-input comparer are plain PowerShell commands, so no agent is needed. |
| Architecture or root-cause debugging after repeated failures | Opus 5.5 | high | Rare. |

**Codex:** GPT-6.1 Sol at high effort for implementation and for read-only reviews (works in the VS Code extension; the CLI with a ChatGPT login refused it, fallback `gpt-6-sol`). GPT-6 Luna for mechanical work (renames, doc edits). Use Codex when Claude usage is at 90–95% or the Claude agents are rate-limited; the live queue and exact prompts are in `CODEX_PICKUP.md`.

**Usage habits:** run at most about three independent lanes at a time, one independent review per batch plus one re-check, check `/usage` before starting a lane, and prefer a fresh chat over `/compact` when the history is huge.

## 10. Open owner decisions and known risks

- Owner: the trial review; the Task 13 go/no-go; whether `_review.csv` as LF is fine (decided yes); the stale old hashes in the Phase D decision record header; when to push (the owner runs it).
- Risks: only Windows has been run; the CI matrix does not exist yet; the GUI is not merged and its Task 10 (prerequisite questions) is unbuilt; the OCR has no accuracy scores yet, and the strict "supported" criteria cannot pass until confidence scoring exists; `dev` is 17+ commits ahead of GitHub and not pushed; S-b (any folder holding a `failure.json` is treated as diagnostics) and S-e (a missing input now raises before writing `failed/`) are accepted risks in Phase D.

## 11. Resume prompts

**Claude (fresh chat):**
> Read C:\Users\Hawksprey\source\repos\Bintanong\plans\phase2_prospectus_master_status_2026-10-07.md, then C:\Users\Hawksprey\source\repos\Bintanong-wt\CODEX_PICKUP.md (the UPDATE section) and the memory files it points to. Verify the worktree states with git. Follow section 1 strictly: no AI trailer, no push, never touch the main checkout. Then continue with section 8, starting at item 2 unless I tell you otherwise. Use the i-have-adhd output style.

**Codex (master prompt; use for any phase, then add the batch-specific task):** the batch prompts are in `CODEX_PICKUP.md` (Prompt 1 to 4) and the current one is `C:\Users\Hawksprey\source\repos\Bintanong-wt\CODEX_PROMPT_gui_integration_2026-10-07.md`. Every Codex prompt starts like this:
> Read C:\Users\Hawksprey\source\repos\Bintanong\plans\phase2_prospectus_master_status_2026-10-07.md (sections 1, 3, 6, 8), then C:\Users\Hawksprey\source\repos\Bintanong-wt\CODEX_PICKUP.md ("UPDATE 2026-10-07 LATE" first, then STEP 0). Verify every worktree tip with `git -C <wt> log -1` and `git status --short`. Follow section 1 strictly (no AI trailer, no push, never touch the main checkout, worktrees only, test first, strictness over guessing, `--basetemp` outside the repos). Do not move dev. Output style: i-have-adhd.

**Skills Codex must read as plain Markdown** (it cannot invoke them): the superpowers 5.1.0 skills listed in section 9 (`test-driven-development`, `verification-before-completion`, `systematic-debugging`, `subagent-driven-development`, `executing-plans`, `requesting-code-review`, `receiving-code-review`, `finishing-a-development-branch`), plus `C:\Users\Hawksprey\.claude\skills\grilling\SKILL.md` (`grill-me` only points to it; use it only for decisions that are the owner's: ask one question at a time, recommended answer first), `C:\Users\Hawksprey\.claude\skills\code-review\SKILL.md` (two axes, Standards and Spec; run as two separate read-only runs; spec = the phase plan; the CodeRabbit and Sentry code-review skills are not the ones), `antislop` and `ponytail` for style. The cross-phase rules are in `plans/2026-10-03-prospectus-extractor-package-split.md`.

**Subagent roles for Codex** (each a separate run, never self-review): implementer = `.claude/agents/extractor-implementer.md` plus the implementer prompt (`codex -s workspace-write`, effort medium, high for ledger, locks and Phase C state work); spec reviewer = `.claude/agents/extractor-reviewer.md` plus the spec-reviewer prompt (`codex exec -s read-only`, high); quality reviewer = same file plus the quality-reviewer prompt, after the spec review passes. Loop: findings as file:line, reproducer, severity, NONE when clean; fix test first; one re-check only for a High; same area failing three times means fix the root cause. Gates are plain PowerShell. At most 2 runs at once. Stop and report if the owner's usage is above 85%.

**Every hand-off report must use these three buckets** (verify each row against git and fresh gate runs; say "UNVERIFIED" for what you could not check; "ready" means ready for the owner's sign-off, never approved):
1. **Completed** (section 3 rows with status Done, plus the review GUI Tasks 1-11 at tip `61d251d` once integrated), each with its evidence and test counts.
2. **In progress / in the middle** (OCR about 50% with its remaining tasks; GUI integration and the browser plus Lighthouse pass; Master Phase 2 parts that have no plan), saying what is done and what is left.
3. **Pending, ready and waiting for the owner's sign-off**: B2 Task 12 and the GUI Task 12 trials; the Task 13 go/no-go; B2 Task 14 closeout; the dev fast-forward to `integration/gui-0710`; the open owner decisions in section 10 and in the "UPDATE 2026-10-07 LATE" block of `CODEX_PICKUP.md`; push timing; and the not-started phases E, F and master Phase 1 with Phase 2 prep, in the owner's order.

**Claude (fresh chat) additions to the resume prompt above:** load the superpowers skills, `grill-me`/`grilling`, `code-review` and `ponytail` from section 9, use the agents and models in section 9b (`extractor-implementer` and `extractor-reviewer`, Sonnet 5.5, effort per the table), keep gates as scripts, at most 2 agents at once, check `/usage` between steps, and finish every report with the three buckets above.
