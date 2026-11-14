# Session cleanup proposal — owner decision required

Design analysis only, 2026-10-10. No product changes, implementation, new tests, probes, review verdict, or approval. The confirmed cleanup High remains open.

## Intended outcome and classification

Contain the existing Windows cleanup failure: public errors must not disclose parser filenames, content, identifiers, or native tracebacks; failed workspaces must remain explicitly owned until deletion succeeds; no failed upload may commit facts. Preserve the standalone callback API and existing defaults. This is a bounded change to the existing store only if the owner approves the exceptional retention and recovery contract below. If immediate erasure on every failure/restart remains unconditional, the existing generic in-process callback cannot satisfy it; that requires an architectural design instead.

The brainstorming gate requires approval of the concrete short in-chat design before bounded implementation: C:\Users\Hawksprey\.codex\plugins\cache\openai-curated-remote\superpowers\6.4.2\skills\brainstorming\SKILL.md:38–55. This proposal is evidence for that presentation, not an approved spec or an implementation plan.

## Source evidence and root cause

Define archive root A = E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\draft_review_archives\session_fixed.

- A\backend\bintanong_session\store.py:161–184 validates/adopts facts only after extraction and wipes caller bytearrays in finally. At :186–197, the try protects callback execution but the enclosing TemporaryDirectory exit is outside it. Cleanup failure therefore replaces the parser failure with an unsanitized native exception and loses explicit lifecycle ownership of the directory.
- E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\session_standards_evidence\runner.py:85–114 records a callback that retains its own output handle, writes synthetic private bytes, then raises. cleanup_probe.json:2–11 records PermissionError, unsanitized traceback, retained disk bytes, wiped bytearray, and zero facts. This was read, not rerun.
- E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\draft_review_archives\SESSION_STANDARDS_REVIEW.md:3–9 records the confirmed High and existing independent evidence. Exception suppression alone does not resolve it.
- C:\Users\Hawksprey\AppData\Local\Programs\Python\Python313\Lib\tempfile.py:949–955 shows exit calls cleanup; explicit cleanup detaches the finalizer before deletion. A retained TemporaryDirectory can be explicitly retried if deletion failed. Its default repr contains its path (:943–944), so it must not become a public diagnostic object.
- A\docs\decisions\phase-01-source-governance.md:87 requires original bytes/parser files deleted after extraction and explicit deletion/expiry/failure cleanup. A\docs\decisions\draft-session-lifecycle.md:18–21 claims removal in all cases; :66–79 documents the limited tested boundary and missing restart/parser/deployment checks.
- C:\Users\Hawksprey\source\repos\Bintanong-wt\integration-fin\plans\master_implementation_plan_original_long.md:613–619 requires memory/bounded tmpfs processing, isolated conversion, deletion after extraction, and failure cleanup; :636–642 requires disappearance and no persistent personal records. Ordinary Windows temp files currently fall short of that final system requirement.
- C:\Users\Hawksprey\source\repos\Bintanong-wt\draft-session\plans\phase-01-handoff.md:23,92,95 states runtime retention/deletion is not delivered and owner decisions remain open. C:\Users\Hawksprey\source\repos\Bintanong-wt\CODEX_HANDOFF_drafts_recovery_2026-10-10.md:94,110,202 keeps the store standalone and session policy/defaults owner-reviewable; :211–216 preserves worktree/scratch/data boundaries and excludes unrelated implementation.

## Approaches

1. **Recommended conditional bounded correction: explicit workspace ownership, sanitized cleanup, retry, and fail-closed upload admission.** Retain a failed workspace cleanup object privately in this SessionStore; retry through existing purge calls. Reject new uploads while any owned cleanup remains unresolved, with the existing fixed ExtractionFailed type/message. Existing facts/deletion continue to work. No new public status API, cleanup count, configuration, timer, persistence, or dependency. This stops silent orphaning during the same store lifetime and allows recovery after the callback closes its handle. It does not erase a locked file or impose a retention deadline. Requires an explicit owner-approved exceptional-retention contract; cannot be described as preserving the present unconditional erasure guarantee.
2. **Wrap the full TemporaryDirectory lifecycle and sanitize the exception only.** Smallest diff, prevents disclosure, but private bytes still become orphaned and purge/delete cannot retry. Insufficient for the confirmed High; not recommended as the complete correction.
3. **Isolated conversion process with owned resources and transient storage.** Move parser handles into a deliberately managed worker so orderly worker exit releases them before parent cleanup. Pair with memory/tmpfs and startup/shutdown recovery to address restart guarantees. This better matches master 15.1, but changes callback execution/serialization/resource ownership and deployment assumptions; arbitrary callbacks may close over unpicklable state. Other processes/filesystem faults can still obstruct deletion. Architectural, not currently authorized, and requires its own spec, implementation plan, and owner approval. No process kill or worker implementation is included here.

Closing handles belonging to callbacks or unrelated code is not an approach: the store does not own them and must not introspect or close them.

## Concrete bounded behavior, conditional on owner approval

- Expand the sanitized lifecycle boundary to workspace allocation, callback materialization, validation, and explicit cleanup. Raise fixed ExtractionFailed outside caught parser/native-error scopes, without retained/chained exceptions or traces. Preserve bytearray wiping on every add_upload exit.
- Give every successfully allocated workspace an explicit owner until cleanup succeeds. Track failed cleanup privately, independently of sessions/uploads; deletion or expiry must not forget it. Retain only the cleanup target/object and safe internal state, never raw bytes, facts, parser objects/handles, or exception objects. Keep reprs redacted and forbid serialization as today.
- Retry exact store-created cleanup targets during the existing _purge path, including purge_expired. Retry only pending workspaces, never still-active callback workspaces. Use the lock for ownership/state transitions and leave callback execution outside it so session deletion/expiry still discards late results.
- Each cleanup target must be its recorded absolute store-created child of the recorded allocation root; verify containment and that the target is not a replaced link/junction before recursive cleanup. Refuse unsafe targets and keep ownership; never scan the temp root, rebuild targets from user/session input, delete a parent root, or follow replacement targets elsewhere.
- Failed cleanup keeps the upload failed even when its returned facts were otherwise valid. Check unresolved cleanup after authorization/normal upload validation and before allocating/invoking another callback, then check again before committing in-flight facts. Another admitted callback may already be running when cleanup fails: it still cleans its own workspace and must not commit while the store remains in cleanup fault. Register ownership atomically so races do not drop targets. Do not pretend this introduces a new in-flight job or byte-size bound.
- _purge must continue expiring facts/cache even when cleanup remains blocked; retry failure cannot prevent delete_session/delete_upload or turn those methods into raw native errors. Reads remain authorized and retain their existing behavior.
- purge_expired retains its existing integer meaning (sessions expired). If cleanup is still unresolved after purge, raise existing fixed ExtractionFailed outside the caught cleanup scope, instead of reporting a misleading successful recovery or exporting pending counts. This is a new documented failure case on an existing API, not a new API. Upload admission uses the same fixed error. Never include workspace paths/filenames or session ownership in public errors.
- Once the external callback closes its own handle, the next explicit purge/access retries deletion. Remove the pending target only after actual cleanup succeeds. A later valid upload may proceed normally; the original failed upload is never automatically committed/replayed.

## Owner decision that must precede implementation

Approve or reject this narrowly stated exception: on an OS-blocked cleanup, private parser bytes can remain in the exact owned temporary workspace after add_upload fails, possibly after session deletion/expiry, until the callback releases its resource and a same-store purge retries successfully. The store refuses new uploads while cleanup is unresolved. There is no guaranteed retention deadline and no automatic worker/timer. The store instance must stay alive to preserve recovery ownership; disposal, process crash, real service restart, and external handles are not solved. Existing 30-minute/8-hour fact TTLs do not become a file-retention permission or guarantee.

Also approve the documented new purge_expired failure case and the distinction between immediate removal of accessible facts/cache and unresolved physical workspace deletion. No silent edit may convert the original privacy guarantee into this weaker contract. If indefinite operation-driven exceptional retention is unacceptable, select the architectural path rather than claiming this bounded fix meets immediate-erasure/restart requirements. This draft remains unsuitable for real private records until the research privacy/storage/restart policy is resolved.

## Exact proposed change scope

Relative to an authorized new candidate copied from A, not edits to A itself:

- backend/bintanong_session/store.py: private cleanup ownership/state, sanitized lifecycle, retry integration, upload admission/commit checks, purge failure behavior, truthful docstrings. Preserve public signatures, token checks, facts/cache semantics, configured defaults, and outside-lock extraction.
- tests/test_session_lifecycle_store.py: cleanup-recovery/fail-closed/state regression cases beside existing :95–147 cleanup tests, :236–303 deletion/expiry tests, :341–367 late-result tests, and :398–421 malformed-output cleanup test.
- tests/test_session_lifecycle_safeguards.py: path/content/token/error/trace/log/repr/pickle checks for the new cleanup state beside :95–141; retain no scan/network/persistence prohibitions at :152–172. Existing source-call scanner need not be weakened for exact-target platform cleanup.
- docs/decisions/draft-session-lifecycle.md: replace the unsupported all-cases erasure claim at :18–21, add owner-approved exception/retry/fail-closed/purge behavior, and separate same-process recovery from restart and full Phase 10 compliance at :63–80. This documentation change is permitted only after the owner explicitly accepts the policy distinction.
- backend/bintanong_session/__init__.py remains unchanged: existing ExtractionFailed is already exported (:3–7). session_lifecycle_fixtures.py remains unchanged unless a test genuinely needs shared synthetic handle ownership; prefer local fixtures whose finally closes only their own handles.
- Repository-wide archived rg finds product references only in store.py and __init__.py; other SessionStore/add_upload/purge_expired references are these two test modules and lifecycle docs. No API worker/parser/deployment consumer exists. No schema/export/config/lock/API/Docker/embedding/Prolog/routing changes are proposed.
- Governance/master requirements remain authoritative and unchanged. Record the approved draft limitation without retroactively declaring the Phase 10 exit gate passed.

## Invariants and acceptance cases for later authorized TDD

1. Windows retained-handle callback raises after writing synthetic bytes: fixed ExtractionFailed; no cause/context/private filename/path/content/token in repr/trace/log/output; bytearray zeroed; zero new facts. Workspace remains privately owned, not silently abandoned.
2. Callback returns valid facts but cleanup fails: same refusal, no facts or upload slot committed. Existing facts/cache from other uploads/sessions are unaffected.
3. While handle stays open, repeated purge fails with the same fixed message; target remains owned; expiry still removes facts/cache; authorized deletion still removes memory state. A new upload invokes no callback and creates no workspace. Invalid tokens retain NotAuthorized behavior.
4. Test closes only its own retained handle; purge removes the exact workspace and clears pending ownership; later upload succeeds. Purge returns expired-session count, not cleanup count. No failed facts resurrect.
5. Workspace creation/native-cleanup failures have fixed errors with no native context/trace leak. Recovery failure keeps ownership. Already absent workspace cleanup is safe and idempotent.
6. Success, ordinary extraction failure, malformed output, exact limits, quota reuse, bytearray wiping, namespace and cross-session isolation retain current behavior. Default values remain unchanged.
7. Concurrent failure/admission/commit and delete/expiry during extraction: no dropped cleanup target, no commit while cleanup fault remains, no purge deletion of an active workspace, no late facts after authorization dies. Do not hold the session lock across callbacks or introduce a deadlocking callback lock.
8. An exact-target containment/replacement failure does not delete any unrelated path; state stays redacted and admission remains closed. No root discovery/scan or leaked public pending count.
9. Internal pending state repr/serialization stays private; no raw bytes/facts/parser errors/handles are reachable through the store after failure. Tests may inspect exact synthetic owned targets privately; diagnostics must not publish them.

Tests should be authored/run only after the root presents the concrete bounded design and receives owner approval. The existing 58-test/reproducer/thread/hash evidence was not repeated. Later verification should cover the smallest affected suite and critical guards, then root-owned applicable gates and the separately authorized independent High recheck; this proposal provides no verdict.

## Not checked / residual risk

No new tests/probes or broad gates; no code, candidate, worktree, archive, Git, dependency, source-data, or memory changes. Only this external proposal was written. Windows locked bytes can survive failure/deletion/expiry and store/process loss; the bounded proposal improves same-process recovery and truthful failure reporting, not immediate erasure or restart compliance.
