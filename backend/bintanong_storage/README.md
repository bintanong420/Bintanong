# Source registration and candidate loading

`SourceRegistrationLoader.load_versions(versions, documents)` registers parent
sources before `BatchKnowledgeLoader.load_artifacts`. Both accept an injected
storage client; administrative credentials stay on the server. Runtime requests
never invoke this importer or fall back to its credentials.

Versions must validate as `SourceDocumentVersion` and retain initial acquisition,
verification and content-review state `pending`, approval `not_requested`, and
null approval ID. This interface does not approve sources or update their review
states. A valid acquired/approved register needs a separate governed transition
workflow. It cannot be downgraded through registration.

Pass explicit document dictionaries with exactly `document_id`, `namespace`
(`institutional`), `synthetic` (boolean), `document_category` and `title`. The
storage categories are curriculum_prospectus, academic_handbook,
institutional_statute, administrative_order and enrollment_guideline. A generic
source-register category is preserved in the full payload; it does not infer the
storage category. Document namespace/synthetic flags must match every version,
and document/version membership must match exactly.

The administrative `register_pending_sources` RPC atomically inserts documents
and versions under the publication lock. `document_versions.source_register`
retains the complete contract including evidence references and approval ID.
Existing version fields preserve the source metadata/states. Exact reimports
are no-ops; changed document/version identities reject the whole registration
batch. Legacy rows remain null in the new column and are not backfilled here.

Incoming versions also pass the existing cross-record register validator.
The RPC rejects duplicate source bytes under separate IDs and conflicting
edition/byte identities against stored rows, including later calls, while
holding the publication lock. It does not silently merge locators or identities.
The trusted administrative ingester must use the Python contract boundary;
the RPC is not a second implementation of every governance validator.

Registration, chunk/vector loading and draft creation are separate resumable
operations. A later load failure can leave pending parents, which remain hidden
by existing RLS. Creating a draft does not activate it. Existing activation
checks and source/content holds still apply. New migration files are candidates
until applied through the applicable deployment workflow; no shared application
is implied by local test delivery.

`SourceAcquisitionLoader.observe(current, check)` records only the A1 acquisition
transition from initial pending to observed. Supply the unchanged full source
contract and an exact check envelope: version_id, source_sha256,
acquisition_locators and Evidence. It binds the check to the source and preserves
all scope, review and approval fields. This records a trusted byte-check claim;
it does not verify local files, authenticate a recorder or establish authority.

The administrative `observe_source_acquisition` invoker RPC derives the change
under the publication lock, compares the complete register and relational
projection, and rejects stale/conflicting, legacy/null or published sources.
Only acquisition_state and the appended source-register Evidence change. An
explicit exact replay returns the persisted record without an UPDATE; uncertain
transport errors never trigger retries. Replay observation directly: initial
registration of the old pending record remains a conflict after observation.
Runtime roles cannot invoke this operation, and observed pending sources remain
hidden. No verification, approval, content review or release activation follows.
