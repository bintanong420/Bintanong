"""Initial-state source registration; never an approval or transition interface."""
from collections.abc import Sequence

from backend.bintanong_contracts.governance import SourceDocumentVersion, STATE_FIELDS, check_register
from .client import SupabaseStorageClient


STORAGE_CATEGORIES = frozenset(('curriculum_prospectus', 'academic_handbook',
    'institutional_statute', 'administrative_order', 'enrollment_guideline'))
_DOCUMENT_FIELDS = {'document_id', 'namespace', 'synthetic', 'document_category', 'title'}
_INITIAL = dict(acquisition_state='pending', verification_state='pending',
    approval_state='not_requested', content_review_state='pending')


class SourceRegistrationLoader:
    """Register explicit parent metadata and complete pending source contracts.

    Administrative RPC insertion is atomic and immutable on identity conflict.
    Chunk loading and draft creation remain separate, inactive operations.
    """
    def __init__(self, client=None):
        self.client = client or SupabaseStorageClient()

    def load_versions(self, versions, documents):
        for rows in (versions, documents):
            if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
                raise ValueError('Nonempty source versions and explicit document metadata required')
        parsed = [SourceDocumentVersion.parse(v.model_dump(mode='json')
            if isinstance(v, SourceDocumentVersion) else v) for v in versions]
        check_register(parsed)
        records = [v.model_dump(mode='json') for v in parsed]
        docs = {}
        for d in documents:
            if (not isinstance(d, dict) or set(d) != _DOCUMENT_FIELDS
                    or not isinstance(d['document_id'], str) or d['document_id'] in docs
                    or d['namespace'] != 'institutional' or type(d['synthetic']) is not bool
                    or not isinstance(d['document_category'], str)
                    or d['document_category'] not in STORAGE_CATEGORIES
                    or not isinstance(d['title'], str) or not d['title'].strip()):
                raise ValueError('Unique explicit institutional storage metadata required')
            docs[d['document_id']] = dict(d)
        if set(docs) != {v['document_id'] for v in records}:
            raise ValueError('Source versions and document metadata must match exactly')
        for v in records:
            if any(v[k]['state'] != _INITIAL[k] for k in STATE_FIELDS) or v['approval_id'] is not None:
                raise ValueError('Registration accepts only initial pending source states')
            d = docs[v['document_id']]
            if any(v[k] != d[k] for k in ('namespace', 'synthetic')):
                raise ValueError('Source namespace/synthetic metadata must match its parent')
        return self.client.rpc('register_pending_sources',
            dict(p_documents=list(docs.values()), p_versions=records), role='admin')
