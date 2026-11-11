# GUI knowledge intake: upload to local Supabase

Owner request, 11 November 2026: run the policy update pipeline from the researcher GUI
("upload document > docling it > audit what Docling did + with Gemma vision model + HITL
corrections > chunk it > send it to supabase"), for USG first and other policies later.
Owner go-ahead the same day ("okay go"). Continues the
[unified knowledge-update plan](2026-11-08-unified-knowledge-update-plan.md); not a new phase.

## Fit with the master plan and earlier phases

Checked 11 Nov against master plan lines 31, 68, 254, 437, 674 and section 18.3, and against
the Phase 01–12 handoffs (read-only audit). The GUI only starts the existing
researcher-controlled CLI jobs on the researcher's machine (master 674); activation stays a
command; nothing is hosted. Phase rules carried here:

- Phases 0/4: only the Python server writes to Supabase; the service key never reaches a browser.
- Phases 1/10: institutional uploads live in the researcher app and `knowledge_update` only;
  never `bintanong_private_context`, student routes or the student session cookie.
- Phases 2/5: everything stays candidate-only and inactive; Docling or Gemma success approves nothing.
- Phase 3: embeddings use the pinned local SEA-LION-E5 folder; no model picker, no downloads.
- Phases 9/12: no code path can reach hosted Supabase (evaluators use it, owner 8 Nov).
- Phase 11: every new route sits behind the existing loopback host/origin check and review token.

## Rules

1. Call the existing `prepare`, `build` and `verify` unchanged.
2. Server picks the upload id (`secrets.token_hex`); the client filename is never used. Title,
   edition and office go only into JSON, never into a command line. Subprocesses use an
   argument list, no shell.
3. Each upload gets `audit-evidence/ku-uploads/<id>/` with sibling `original/`, `manifest.json`,
   `upload.json` and `packet/`, outside Git. Uploads are capped at 128 MiB, must start with `%PDF`,
   and the server computes the SHA-256.
4. A Gemma audit is chosen at upload; redoing it means a new upload (one packet per manifest).
5. The audience question at upload is a note only; audience stays a per-item review decision.
6. Kinds: `handbook` and `charter`. USG goes in as `handbook`.

## Checklist (test first, synthetic fixtures)

- [ ] 1. Upload route: cap, `%PDF`, hash, server id, manifest; Next proxy allows the larger body
  for this one path only.
- [ ] 2. Build form for subject assignments and claim reviews (not in the review export),
  written as build's `--metadata`; held-back items shown from the export first.
- [ ] 3. Run `prepare` in the configured p12 venv as a background process; status file and
  log tail; say clearly when Gemma was not reachable ("AI assistance unavailable").
- [ ] 4. Open review for a chosen upload (swap the review session; one reviewer per packet).
- [ ] 5. T4 `local_release.py`, local Supabase only (127.0.0.1:54321; owner 8 Nov replaces the
  2 Nov scratch-only target): hosted/local fingerprint first, `load_versions` ->
  `load_artifacts` -> inactive draft `create_release`, then read back counts, draft status
  and the unchanged active release. Build passes the local `--model-dir`.
- [ ] 5b. Targeted question checks against the draft before it may be activated (master 18.3 step 5).
- [ ] 6. Tracked local-only command for activate and rollback with the owner's authorization reference.
- [ ] 7. One synthetic end-to-end test: upload -> prepare -> review -> build -> verify -> draft load.

Not in this round: changed-span re-review (U3; a new edition is a full re-review), new document
kinds/templates, prospectus rules (U1), an activate button, hosted writes, multiple users.
