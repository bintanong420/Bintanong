# Phase D F4 LF artifact task
Base: 4a0cdb794a337b9cc91846d16585478c3bb5fde0.
Worktree: C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d.
Owner: /root/d_lf; no subagents or other writer.
Scope: batch.write_manifest reuses publish.write_text_lf; review CSV uses stdlib DictWriter lineterminator LF and retains utf-8-sig BOM. Preserve names, contracts, manifest schema/fields/timestamps, CSV columns/values and quoted embedded CRLF field data. Do not touch S1/default root.
Tests first: raw bytes expose Windows CRLF JSON and CSV record separators; Unicode, parsed contents, BOM and embedded field preservation checked. Exact red/green/focused/full logs saved externally; checkpoint after each boundary. Fresh main full excluded baseline required before explicit commit; do not repeat initial baseline. GUI review venv comprehensive suite and standalone selftest NOT RUN for this task, deferred final D gates.
Constraints: PowerShell only; pathlib LF evidence; explicit staging; preserve preexisting progress checkpoint changes. No main edits, venv changes/install/sync, repo generated outputs, push/dev merge/worktree removal or cleanup of preserved files. Required final trailer: Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>.
Parent dispatches independent spec then quality reviews; Phase D not complete.
