"""Owner-authorized research release inputs derived from reviewed records only.

Research mode (AGENTS.md, 21 October 2026) is development use of reviewed real data,
not school approval or institutional activation.
"""
from collections import Counter
import json

from ..bintanong_contracts.symbolic import Capability, CapabilityRegistry
from ..bintanong_orchestration.adapters import RetrievalAdapter, SymbolicAdapter
from ..bintanong_orchestration.contracts import ReleasePin
from ..bintanong_orchestration.ports import ReleaseResources
from ..bintanong_retrieval.engine import RetrievalEngine
from ..bintanong_retrieval.evidence_policy import SourceAwareEvidencePolicy
from ..bintanong_retrieval.types import RetrievalSettings
from ..bintanong_routing.contracts import CatalogEntry, DocumentTopic
from ..bintanong_symbolic.bundle import prepare_runtime_bundle
from ..bintanong_symbolic.runtime import CurriculumRuntime
from .package_storage import PackageStorage

OPERATIONS = ('check_prerequisite_eligibility', 'list_missing_prerequisites', 'list_affected_courses')
CAPABILITIES = dict(zip(OPERATIONS, ('offline_research_prerequisite_check',
    'offline_research_missing_prerequisites', 'offline_research_dependency_inspection')))
# Phase 05 selected document-development profile (uncalibrated; research status rule applies).
SETTINGS = RetrievalSettings(top_k=3, min_similarity=.25, context_budget=2048,
                             policy_id='uncalibrated-document-development-v1')


def _printed_forms(code):
    return {code, code.replace(' ', '')}


def _short_forms(code):
    # Owner alias rule: students may omit spacing and the printed "/L" suffix.
    return _printed_forms(code[:-2]) if code.endswith('/L') else set()


def research_catalog(ledger):
    """Course entries for reviewed identities; draft identities are left out."""
    courses = [c for c in ledger['courses'] if c['review_state'] == 'reviewed' and c['review_refs']
               and 'course_code' in c.get('facts', {})]
    printed = {c['course_id']: _printed_forms(c['facts']['course_code']['value']) for c in courses}
    if sum(len(v) for v in printed.values()) != len(set().union(*printed.values()) if printed else ()):
        raise ValueError('duplicate_printed_course_code')
    short = {cid: _short_forms(c['facts']['course_code']['value']) for c in courses for cid in [c['course_id']]}
    counts = Counter(a for forms in [*printed.values(), *short.values()] for a in forms)
    entries = []
    for c in courses:
        cid = c['course_id']
        aliases = printed[cid] | {a for a in short[cid] if counts[a] == 1}
        entries.append(CatalogEntry(kind='course', entity_id=cid, program_id=c['program_id'],
            curriculum_id=c['curriculum_id'], aliases=tuple(sorted(aliases)),
            source_ref=c['source_version_id'], review_ref=c['review_refs'][0], reviewed=True))
    return tuple(entries)


def course_labels(ledger):
    """Display-only printed codes, drafts included (they can appear inside conditions)."""
    return tuple((c['course_id'], c['facts']['course_code']['value']) for c in ledger['courses']
                 if 'course_code' in c.get('facts', {}))


def topic_menu(register, *, catalogue=None, chunks=()):
    """One topic per reviewed subject with its reviewed claims, plus the claims its chunks'
    source_limits record as not stated (selecting one makes the policy withhold)."""
    subjects = {}
    for review in register['reviews']:
        subjects.setdefault(review['subject_id'], []).append(review['claim'])
    readings = {a['reading_id']: a['subject_id'] for a in (catalogue or {}).get('assignments', [])}
    missing = {}
    for chunk in chunks:
        subject = readings.get(chunk.get('type_fields', {}).get('reading_id'))
        if subject not in subjects:
            continue
        try:
            limits = json.loads(chunk['text']).get('source_limits', [])
        except (ValueError, TypeError, AttributeError):
            limits = []
        for limit in limits:
            if limit.get('issue') == 'claim_not_stated' and limit.get('resolution') == 'unresolved':
                missing.setdefault(subject, []).extend(
                    c for c in limit.get('affected_claims', []) if c not in subjects[subject])
    return tuple(DocumentTopic(subject_id=s, claims=tuple(dict.fromkeys(c)),
                               not_stated=tuple(dict.fromkeys(missing.get(s, ()))))
                 for s, c in subjects.items())


def build_research_resources(ledger, package, *, encoder, authorization_ref):
    """Compose one research release: reviewed rules, reviewed package, research labels."""
    bundle = prepare_runtime_bundle(ledger)
    runtime = CurriculumRuntime.for_offline_research(bundle, authorization=dict(
        purpose='offline_curriculum_acceptance', authorization_ref=authorization_ref,
        bundle_sha256=bundle['content_sha256'], operations=list(OPERATIONS)))
    release_id, manifest, chunks = runtime.release_id, package['manifest'], package['chunks']
    storage = PackageStorage(release_id=release_id, manifest=manifest, chunks=chunks,
                             versions=package['versions'], vectors=package['vectors'])
    policy = SourceAwareEvidencePolicy(release_id=release_id, embedding_set_id=manifest['embedding_set_id'],
        chunks=chunks, catalogue=package['catalogue'], claim_reviews=package['register'])
    sources = {s['version_id']: s['byte_sha256'] for s in bundle['ledger']['sources']}
    sources.update({c['version_id']: c['byte_sha256'] for c in chunks})
    pin = ReleasePin.parse(dict(release_id=release_id, synthetic=False, research_ref=authorization_ref,
        rule_bundle_version=runtime.rule_bundle_version,
        sources=[dict(version_id=v, byte_sha256=h) for v, h in sorted(sources.items())],
        documents=[dict(chunk_id=c['chunk_id'], version_id=c['version_id'], byte_sha256=c['byte_sha256'])
                   for c in chunks]))
    registry = CapabilityRegistry({op: Capability(name, ('curriculum_id', 'course_id'))
                                   for op, name in CAPABILITIES.items()})
    engine = RetrievalEngine(storage, encoder, SETTINGS, evidence_policy=policy)
    return ReleaseResources(pin, research_catalog(ledger), registry,
        RetrievalAdapter(engine, research=True), SymbolicAdapter(runtime, research=True),
        topics=topic_menu(package['register'], catalogue=package['catalogue'], chunks=chunks),
        document_scope=('audience:undergraduate',),
        course_labels=course_labels(ledger))
