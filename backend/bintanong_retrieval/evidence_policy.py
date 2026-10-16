"""Trusted candidate policy bindings; metadata consistency is not authorization."""
import copy

from .candidate_subject import _digest, _subject, prepare_candidate_subject_catalogue, select_candidate_subject
from .candidate_claims import _strings, prepare_candidate_claim_reviews, build_candidate_claim_report


_CHUNK_FIELDS = ('chunk_id', 'document_id', 'version_id', 'edition_id', 'byte_sha256',
    'chunk_type', 'chunker_version', 'content_hash', 'text', 'source_text', 'scope',
    'section_path', 'type_fields')
_SPAN_REQUIRED = ('version_id', 'byte_sha256', 'page')
_SPAN_OPTIONAL = ('printed_page_label', 'locator', 'bbox', 'text')


class PolicyBindingError(ValueError):
    """The actual retrieval rows do not match the prepared candidate snapshot."""


def _project(chunk, spans):
    if not isinstance(spans, list):
        raise ValueError('ordered source spans required')
    projected = {k: copy.deepcopy(chunk[k]) for k in _CHUNK_FIELDS}
    projected['spans'] = [{**{k: copy.deepcopy(s[k]) for k in _SPAN_REQUIRED},
        **{k: copy.deepcopy(s.get(k)) for k in _SPAN_OPTIONAL}} for s in spans]
    return projected


class SourceAwareEvidencePolicy:
    """An injected, copied research snapshot, with no storage or approval loader.

    Original full payloads must validate before transport projections are derived.
    All operations are internal to the opt-in engine path. Matching these bindings
    never verifies runtime release membership or permits an institutional answer.
    """
    VERSION = 'source-aware-candidate-policy-v1'

    def __init__(self, *, release_id, embedding_set_id, chunks, catalogue, claim_reviews):
        if any(not isinstance(v, str) or not v.strip() or len(v) > 2048
               for v in (release_id, embedding_set_id)):
            raise ValueError('explicit pinned release and embedding set required')
        chunks, catalogue, claim_reviews = copy.deepcopy((chunks, catalogue, claim_reviews))
        select_candidate_subject(catalogue, chunks)
        if (not isinstance(claim_reviews, dict) or claim_reviews !=
                prepare_candidate_claim_reviews(catalogue, chunks, claim_reviews.get('reviews'))):
            raise ValueError('unchanged original source-review register required')
        self._release_id, self._embedding_set_id = release_id, embedding_set_id
        self._snapshot_sha256 = _digest(dict(release_id=release_id, embedding_set_id=embedding_set_id,
            catalogue=catalogue, claim_reviews=claim_reviews))
        try:
            self._chunks = [_project(c, c['spans']) for c in chunks]
        except (KeyError, TypeError, AttributeError) as exc:
            raise ValueError('complete comparable source snapshot required') from exc
        self._catalogue = prepare_candidate_subject_catalogue(self._chunks, catalogue['assignments'])
        self._reviews = prepare_candidate_claim_reviews(
            self._catalogue, self._chunks, claim_reviews['reviews'])
        self._bindings = {c['chunk_id']: _digest(c) for c in self._chunks}
        # Validate declared limits even on members not returned by a future query.
        for subject in {a['subject_id'] for a in self._catalogue['assignments']}:
            self._assess(subject, (), [])

    def _metadata(self):
        return dict(version=self.VERSION, snapshot_sha256=self._snapshot_sha256,
                    subject_id=None, requested_claims=None, assessment=None,
                    not_run_reason='retrieval_pending')

    @staticmethod
    def _validate_intent(subject_id, requested_claims):
        if subject_id is not None and not _subject(subject_id):
            raise ValueError('explicit canonical subject hint required')
        if requested_claims is not None and (not isinstance(requested_claims, tuple)
                or not _strings(list(requested_claims))):
            raise ValueError('distinct exact claim strings in a tuple required')

    def _has_subject(self, subject_id):
        return any(a['subject_id'] == subject_id for a in self._catalogue['assignments'])

    def _bind(self, request_release_id, raw):
        try:
            if (request_release_id != self._release_id or raw['release_id'] != self._release_id
                    or raw['embedding_set_id'] != self._embedding_set_id
                    or not isinstance(raw['items'], list)):
                raise ValueError('snapshot identity mismatch')
            pending, visited = list(raw['items']), set()
            for row in pending:
                if id(row) in visited:
                    continue
                visited.add(id(row))
                projected = _project(row['chunk'], row['spans'])
                if self._bindings.get(projected['chunk_id']) != _digest(projected):
                    raise ValueError('source payload mismatch')
                neighbors = row.get('neighbors', [])
                if not isinstance(neighbors, list):
                    raise ValueError('neighbor rows required')
                pending.extend(neighbors)
        except (KeyError, ValueError, TypeError, AttributeError) as exc:
            raise PolicyBindingError('source_snapshot_mismatch') from exc

    def _select(self, candidates, subject_id):
        selected = set(select_candidate_subject(
            self._catalogue, self._chunks, subject_id=subject_id)['chunk_ids'])
        return [row for row in candidates if row['chunk']['chunk_id'] in selected]

    def _assess(self, subject_id, requested_claims, emitted_chunk_ids):
        return build_candidate_claim_report(self._catalogue, self._chunks,
            subject_id=subject_id, requested_claims=list(requested_claims),
            emitted_chunk_ids=emitted_chunk_ids, claim_reviews=self._reviews)
