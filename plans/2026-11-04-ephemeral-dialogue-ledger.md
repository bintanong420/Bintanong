# Ephemeral dialogue ledger and atomic commit — 4 November 2026

Implements the storage/commit slice of the supplied architecture stabilization
plan's Phase 2. This is post-Phase-12 repair work, not a new numbered phase.
Consulted thesis physical 17–18 and 39–44, runtime routing PNG, master routing
architecture, source/scope rules and current handoff on this account resume.

The existing credential-owned SessionStore now keeps at most eight completed
exchanges and 32 KiB of exchange text. Each side is capped at 8 KiB UTF-8 with
an explicit truncation marker. Exchange scope, typed entity IDs, answer status
and validated citation IDs remain separate from accepted ScopedFacts. A generic
unresolved record holds the originating message, operation, slots and candidates.
No new feature-specific pending variant was added.

One locked commit validates the active message, expected revision, facts and
bounded dialogue before changing facts, pending check, legacy conversation and
history together. Failed/cancelled turns release only their own gate. Expired or
deleted sessions stay gone. Wrong owners cannot commit. Duplicate message hashes
survive text eviction; 512 unique completed turns cap the per-session replay set.
Regeneration replaces its exchange and advances the revision.

Only the server-observed current utterance and actual server answer enter history;
client-supplied earlier assistant messages are ignored. Assistant text is dialogue,
never institutional evidence or an accepted student fact. Existing confirmed upload
facts retain their separate storage and provenance. This slice does not yet expose
the ledger to routing: the bounded context compiler and semantic repair/reference
acts are the next capability. No conversational-amnesia completion claim is made.

Retention is memory-only under the existing 30-minute idle session expiry. A new
SessionStore/process forgets it; no disk, database, logs or durable adapter was
added. The same store can be reused by successive ChatTurns instances. Session
identity remains the existing server-issued cookie identity; frontend multi-thread
parity and explicit reset notices remain pending audit slices.

TDD: missing atomic commit reproduced RED; chat regression reproduced the split
conversation write; replay regression exposed acceptance after text eviction.
Focused verification uses system Python 3.13, no pytest cache, ignored external
basetemp `audit-evidence/dialogue-commit-green`: session store, API sessions,
ChatTurns and ledger tests. Final result recorded with the coordinator checkpoint.
No installs, models, source edits, service restart, push or durable storage.
