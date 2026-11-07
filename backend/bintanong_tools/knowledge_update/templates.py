from __future__ import annotations

import copy

from ...bintanong_contracts.source import SourceSpan
from ..document_ingest.reviewed_policy import build_reviewed_policy_bundle
from .files import digest, encoded


def template_items(template: dict, doc: dict, source: bytes) -> list[dict]:
    """Import source-bound associations, never approval from an earlier review."""
    if (not isinstance(template, dict) or set(template) - {'readings', 'field_spans', 'required_readings'}
            or not isinstance(template.get('readings'), list) or not template['readings']
            or not isinstance(template.get('field_spans', {}), dict)
            or not isinstance(template.get('required_readings', {}), dict)):
        raise ValueError('invalid review template')
    rows, items = copy.deepcopy(template['readings']), []
    for row in rows:
        if (row.get('source_sha256') != doc['sha256']
                or row.get('version_id') != 'ver-' + doc['sha256']):
            raise ValueError('review template source identity mismatch')
        identity = row.get('reading_id')
        fields = row.get('fields')
        if not isinstance(fields, list) or any(not isinstance(f, dict) for f in fields):
            raise ValueError('review template needs fields')
        item = {'id': identity, 'document_id': doc['id'], 'title': row.get('title', identity),
                'audience': 'unresolved', 'companions': template.get('required_readings', {}).get(identity, []),
                'findings': ['source_bound_template_requires_review'], 'fields': [],
                'source_gaps': copy.deepcopy(row.get('gaps', []))}
        for field in fields:
            name = field.get('name')
            original = field.get('original_value')
            proposed = copy.deepcopy(field.get('reviewed_value', original))
            field.update(reviewed_value=copy.deepcopy(original), decision='pending', review_event_sha256=None)
            spans = template.get('field_spans', {}).get(identity, {}).get(name, [])
            if not isinstance(spans, list):
                raise ValueError('template field spans must be a list')
            for raw in spans:
                span = SourceSpan.parse(raw)
                if (span.byte_sha256 != doc['sha256'] or span.version_id != row['version_id']
                        or span.page not in field.get('locator', {}).get('physical_pages', [])):
                    raise ValueError('template span source identity/page mismatch')
            item['fields'].append({**copy.deepcopy(field), 'proposed_value': proposed, 'spans': spans})
        row.update(intended_audience='unknown', applicability='unknown', applicability_evidence_ref=None,
                   preserved_evidence=[{'artifact': 'review_template', 'sha256': digest(encoded(template))}])
        items.append(item)
    build_reviewed_policy_bundle(rows, sources={doc['sha256']: source}, review_events={})
    for item in items:
        companions = item['companions']
        if (not isinstance(companions, list) or any(not isinstance(i, str) or not i for i in companions)
                or len(companions) != len(set(companions)) or item['id'] in companions):
            raise ValueError('invalid template companion mapping')
    return items
