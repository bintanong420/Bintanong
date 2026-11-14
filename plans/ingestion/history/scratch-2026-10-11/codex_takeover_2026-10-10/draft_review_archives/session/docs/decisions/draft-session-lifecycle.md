# Draft: private-session lifecycle (retention and deletion)

Status: DRAFT on its own branch. Not merged, not wired into any API, not an approval of anything. It implements the
lifecycle parts of master plan sections 15.1 to 15.3 and the delete semantics of 16.1 as a small in-memory component,
so the rules can be tested before an API exists. Nothing here approves a source, an edition or a curriculum.

## What is drafted

`backend/bintanong_session/` holds one class, `SessionStore`, standard library plus the Phase 1 contracts only.

- A server-issued opaque capability: `secrets.token_urlsafe(32)`. Only its SHA-256 digest is a lookup key; the token is
  never stored, and the lookup also passes a constant-time comparison. A browser-submitted session id, upload id or
  fact id is never accepted as a credential.
- Every call purges expired sessions first, then resolves the token. Unknown, wrong, deleted and expired tokens raise
  the same `NotAuthorized` with a fixed message, so there is no ownership oracle. Upload ids are random
  (`upload-` plus 128 bits) and are only meaningful inside the session that owns them.
- `add_upload(token, data, extractor)` hands the bytes to a caller-supplied extractor
  `extractor(data, session_id, workdir)` that returns `SessionFact` objects. The store never reads file content. The
  bytes are not kept (a caller-owned `bytearray` is overwritten with zeros) and the temporary workspace is a
  `TemporaryDirectory` removed in all cases, including a failed extraction. An extractor error becomes a fixed
  `ExtractionFailed` with no chained cause, because a parser message may quote file content.
- The extractor output is accepted whole or not at all: every item must be a `SessionFact`, carry this session's id,
  have a unique fact id (also across the session's earlier uploads), and stay within the count limit.
- A result that arrives after the session was deleted or expired is dropped (`NotAuthorized`).
- `facts_for`, `delete_upload`, `delete_session`, `purge_expired`, and a small per-session answer cache
  (`cache_put`, `cache_get`) that is removed with the session.
- Session ids are `sess-` plus 128 random bits and fact ids may use `new_fact_id()`; both satisfy the contracts' own id
  patterns and sit in the `private_session` namespace, so they cannot read as institutional ids.
- Reprs of the store and its internals are fixed redacted strings. Instances refuse pickling and copying. The module
  imports no logging, network, database or institutional code, calls no `print`, `open` or directory scan, and a test
  reads the module source to keep it so.

## Strict defaults (all owner-reviewable)

| Setting | Default | Note |
| --- | --- | --- |
| Idle lifetime | 30 minutes | the plan's proposal; every successful access restarts it; expired at exactly the limit |
| Absolute lifetime | 8 hours | a busy session still ends; the value is a placeholder |
| Sessions in memory | 200 | beyond this, `CapacityExceeded` |
| Uploads per session | 5 | a failed extraction does not use a slot |
| Upload size | 10 MiB | checked before the extractor runs; empty or non-bytes refused |
| Facts per upload | 200 | |
| Cache entries per session | 32 | |
| Clock | monotonic, injectable | tests drive it |

## Owner decisions

1. Idle lifetime, subject to the research privacy protocol (30 minutes is only the plan's proposal).
2. Whether to keep an absolute lifetime cap, and its length.
3. Transport of the capability: an HTTP-only, secure, same-site cookie versus an `Authorization` header. This draft
   issues and checks the token only.
4. The definition of minimal retained context: here, the validated `SessionFact` objects and nothing else. Whether the
   extractor may keep any OCR text or confidence beyond a fact is undecided.
5. Multi-replica deployment. This store is single-process memory. Several replicas need a shared store, which
   conflicts with the no-persistence rule; sticky routing or a shared in-memory service would be a new decision.
6. Telemetry and log policy: this draft emits nothing. Which counts (sessions, expiries) may be exported is undecided.
7. Where `DELETE /uploads/{id}` and `DELETE /session` live and who wires them into `bintanong_api`. Suggested mapping:
   `delete_upload` and `delete_session`, with `NotAuthorized` as a single 404-style answer.
8. Whether fact confirmation (plan 15.1 step 6) is a separate step before facts become visible to routing.
9. The answer cache is a minimal slot so that cached private answers die with the session; whether the API needs one at
   all is open.

## Tested boundary

Cross-session isolation of uploads, facts, cache and in-flight results; expiry (idle, absolute, boundary, sliding);
deletion and failure cleanup of workspace and bytes; a simulated restart (a new store has nothing, nothing was
written); fixed-message errors, redacted reprs, no logging or printing; prompt-like text kept verbatim as data with no
effect; id shape and namespace. This reports a tested in-process boundary, not protection against every threat. A
process memory dump, a swap file, a debugger, a malicious extractor and an attacker who holds a valid token are outside
it.

## NOT RUN

- No API wiring and no HTTP, cookie or header tests.
- No tmpfs or size-bounded workspace on Linux; the workspace here is an ordinary temporary directory without a size cap.
- No real service restart, only a new store instance.
- No load, concurrency or timing tests beyond a lock around state changes.
- No Linux or macOS run.
- No real parser or Docling job, no OCR, no embeddings.
- No memory-forensics check that interpreter-internal copies of bytes are gone; only reachability from the store is tested.
