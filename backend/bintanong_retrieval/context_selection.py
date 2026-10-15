"""Optional offline selection trace; assembly success is not claim coverage."""
from .context import build_context


def _dependencies(candidate):
    """Inspect only the same local neighbor map the context builder can use."""
    identity = candidate['chunk']['chunk_id']
    available = {r['chunk']['chunk_id']: r
                 for r in [candidate] + candidate.get('neighbors', [])}
    group = [candidate]
    required, absent, malformed = set(), set(), set()
    for row in group:
        dependencies = row['chunk'].get('type_fields', {}).get('required_neighbor_chunk_ids', [])
        if not isinstance(dependencies, list) or any(not isinstance(i, str) for i in dependencies):
            malformed.add(row['chunk']['chunk_id'])
            continue
        for dependency in dependencies:
            required.add(dependency)
            if dependency not in available:
                absent.add(dependency)
            elif available[dependency] not in group:
                group.append(available[dependency])
    required.discard(identity)
    return dict(required_chunk_ids=sorted(required),
                absent_required_chunk_ids=sorted(absent),
                malformed_dependency_chunk_ids=sorted(malformed),
                dependency_trace_complete=not malformed)


def build_context_selection_report(candidates, budget, count_tokens, *, primary_limit=None,
                                   compact_citations=False, shared_citations=False,
                                   shared_group_metadata=False):
    """Build a caller-selected prefix and report literal source-chunk identities.

    ``None`` requests every offered primary; zero explicitly requests none.
    Dependencies remain atomic and local to each candidate's supplied neighbors.
    Deferred rows are inspected, not assembled or certified as valid evidence.
    ``primary_emitted``/``unemitted_required_chunk_ids`` describe output IDs only:
    overlap deduplication can omit an ID whose spans are already represented.
    Neither these fields nor empty assembly gaps establish answer sufficiency,
    relevance, applicability, authority or complete dependency/claim coverage.
    """
    limit = len(candidates) if primary_limit is None else primary_limit
    if type(limit) is not int or not 0 <= limit <= len(candidates):
        raise ValueError('primary_limit must be None or an integer from zero to candidate count')
    assembly = build_context(candidates[:limit], budget, count_tokens,
        compact_citations=compact_citations, shared_citations=shared_citations,
        shared_group_metadata=shared_group_metadata)
    emitted = {r['chunk_id'] for r in assembly['evidence']}
    offered = []
    for index, candidate in enumerate(candidates):
        chunk = candidate['chunk']
        identity = chunk['chunk_id']
        dependencies = _dependencies(candidate)
        offered.append(dict(rank=index+1, chunk_id=identity,
            version_id=chunk['version_id'], byte_sha256=chunk['byte_sha256'],
            similarity=candidate['similarity'], requested=index < limit,
            primary_emitted=identity in emitted, **dependencies,
            unemitted_required_chunk_ids=sorted(set(dependencies['required_chunk_ids']) - emitted),
            assembly_gaps=[gap for gap in assembly['gaps'] if gap.partition(':')[2] == identity]))
    return dict(schema_version='context-selection-report-v1', candidate_only=True,
        activation_eligible=False, claim_coverage='unknown', assembly=assembly,
        requested_primary_ids=[r['chunk_id'] for r in offered if r['requested']],
        deferred_primary_ids=[r['chunk_id'] for r in offered if not r['requested']],
        emitted_chunk_ids=[r['chunk_id'] for r in assembly['evidence']], offered=offered)
