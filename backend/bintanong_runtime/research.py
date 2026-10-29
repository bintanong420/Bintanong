"""Owner-authorized research release inputs derived from reviewed records only.

Research mode (AGENTS.md, 21 October 2026) is development use of reviewed real data,
not school approval or institutional activation.
"""
from collections import Counter
import hashlib
import json
import re

from ..bintanong_contracts.symbolic import Capability, CapabilityRegistry
from ..bintanong_orchestration.adapters import SIGNATURES, MultiCurriculumSymbolicAdapter, RetrievalAdapter, SymbolicAdapter
from ..bintanong_orchestration.contracts import ReleasePin
from ..bintanong_orchestration.ports import ReleaseResources
from ..bintanong_retrieval.engine import RetrievalEngine
from ..bintanong_retrieval.evidence_policy import SourceAwareEvidencePolicy
from ..bintanong_retrieval.types import RetrievalSettings
from ..bintanong_routing.contracts import CatalogEntry, DocumentTopic, NotStatedCue, MAX_TOPIC_FIELDS
from ..bintanong_symbolic.bundle import prepare_runtime_bundle
from ..bintanong_symbolic.runtime import CurriculumRuntime
from .hosted_storage import HostedReleaseStorage
from .package_storage import PackageStorage

OPERATIONS = ('check_prerequisite_eligibility', 'list_missing_prerequisites', 'list_affected_courses',
              'course_facts', 'list_term_courses')
CAPABILITIES = dict(zip(OPERATIONS, ('offline_research_prerequisite_check',
    'offline_research_missing_prerequisites', 'offline_research_dependency_inspection',
    'offline_research_course_facts', 'offline_research_term_courses')))
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
    # A printed code may repeat only on titled rows (owner, 23 Oct 2026); both stay cataloged, so a
    # code-only mention matches two entries and the router asks which course is meant.
    repeated = _repeated_codes(courses)
    unique = [v for c in courses if c['facts']['course_code']['value'] not in repeated for v in [printed[c['course_id']]]]
    if sum(len(v) for v in unique) != len(set().union(*unique) if unique else ()):
        raise ValueError('duplicate_printed_course_code')
    short = {cid: _short_forms(c['facts']['course_code']['value']) for c in courses for cid in [c['course_id']]}
    counts = Counter(a for forms in [*printed.values(), *short.values()] for a in forms)
    # A printed title names its course only when no other course carries it or a code spelled like it.
    fold = lambda text: ' '.join(text.split()).casefold()
    titles = {c['course_id']: c['facts']['course_title']['value'] for c in courses if 'course_title' in c['facts']}
    title_counts = Counter(fold(t) for t in titles.values())
    codes = {fold(a) for forms in [*printed.values(), *short.values()] for a in forms}
    entries = []
    for c in courses:
        cid = c['course_id']
        aliases = printed[cid] | {a for a in short[cid] if counts[a] == 1}
        title = titles.get(cid)
        if title is not None and title_counts[fold(title)] == 1 and fold(title) not in codes:
            aliases.add(title)
        entries.append(CatalogEntry(kind='course', entity_id=cid, program_id=c['program_id'],
            curriculum_id=c['curriculum_id'], aliases=tuple(sorted(aliases)),
            source_ref=c['source_version_id'], review_ref=c['review_refs'][0], reviewed=True))
    return tuple(entries)


def _repeated_codes(courses):
    """Printed codes on more than one row; each such row must carry its printed title."""
    counts = Counter(c['facts']['course_code']['value'] for c in courses)
    repeated = {code for code, n in counts.items() if n > 1}
    if any(c['facts']['course_code']['value'] in repeated and 'course_title' not in c['facts'] for c in courses):
        raise ValueError('duplicate_printed_course_code')
    return repeated


def course_labels(ledger):
    """Display-only printed codes, drafts included (they can appear inside conditions); a repeated
    printed code is shown with its printed title."""
    courses = [c for c in ledger['courses'] if 'course_code' in c.get('facts', {})]
    repeated = _repeated_codes(courses)
    titles = Counter((c['facts']['course_code']['value'], c['facts']['course_title']['value'])
                     for c in courses if c['facts']['course_code']['value'] in repeated)

    def label(c):
        code = c['facts']['course_code']['value']
        if code not in repeated:
            return code
        title = c['facts']['course_title']['value']
        if titles[(code, title)] > 1:  # same printed code and title: told apart by printed units
            return f"{code} ({title}, {c['facts']['units.total']['value']} units)"
        return f'{code} ({title})'
    return tuple((c['course_id'], label(c)) for c in courses)


# Owner, 23 Oct 2026 (run 11): a part that asks one person's amount needs the individual assessment,
# which the source does not state; the printed class example is not each student's share.
PER_PERSON = ('each student', 'per student', 'every student', 'each of us', 'per person', 'per head',
              'each one', 'bawat isa', 'bawat estudyante', 'bawat mag-aaral', 'bawat student',
              'kada isa', 'kada estudyante', 'kada student')
NOT_STATED_CUES = {'official individual student assessment': PER_PERSON}


def _reviewed_topic_context(register, catalogue, chunks):
    """Copy assigned reviewed labels/numbered clauses; retain any deadline conflict."""
    def context_field(name):
        return isinstance(name,str) and (name in ('service_title','description')
            or re.fullmatch(r'\d+(?:\.\d+)+',name) is not None)
    readings = {a['reading_id']: a['subject_id'] for a in (catalogue or {}).get('assignments', [])}
    approved = {}
    for review in register['reviews']:
        if review.get('finding') != 'visible_fields':
            continue
        for ref in review.get('field_refs', []):
            if (context_field(ref.get('field_name',''))
                    and readings.get(ref.get('reading_id')) == review['subject_id']):
                key = (review['subject_id'], ref['reading_id'], ref['field_name'])
                approved.setdefault(key, set()).update(review.get('reviewed_chunk_ids', []))
    context = {}
    for chunk in chunks:
        reading = chunk.get('type_fields', {}).get('reading_id')
        subject = readings.get(reading)
        try:
            record = json.loads(chunk['text'])
            unresolved = [limit for limit in record.get('source_limits', [])
                          if limit.get('resolution') == 'unresolved']
            fields = record.get('fields', [])
            by_name = {f['name']: f for f in fields}
            if len(by_name) != len(fields):
                continue
            values = [by_name[name]['value'] for name in by_name if context_field(name)
                and (not unresolved or name not in ('service_title','description')
                     and all(limit.get('issue') == 'conflicting_deadlines' for limit in unresolved))
                and by_name[name].get('source_blank') is False
                and isinstance(by_name[name].get('value'), str) and by_name[name]['value'].strip()
                and chunk.get('chunk_id') in approved.get((subject, reading, name), ())]
        except (ValueError, TypeError, KeyError, AttributeError):
            continue
        text = '; '.join(values)
        if text and unresolved:
            text += '\nUnresolved source limitations: '+json.dumps([
                dict(issue=limit['issue'],affected_claims=limit.get('affected_claims',[]))
                for limit in unresolved],ensure_ascii=False,separators=(',',':'))
        if text and len(text) <= 1024:
            context.setdefault(subject, []).append(text)
    return {s: tuple(dict.fromkeys(values)) for s, values in context.items()
            if len(set(values)) <= 4}


PRINTED_DEFECTS = ('malformed_source_condition', 'printed_total_discrepancy')


def topic_menu(register, *, catalogue=None, chunks=(), routing_context=False):
    """One topic per reviewed subject with its reviewed claims, plus the claims its chunks'
    source_limits record as not stated (selecting one makes the policy withhold)."""
    if type(routing_context) is not bool:
        raise ValueError('invalid_routing_context')
    labels, columns = {}, {}
    if routing_context:
        from .routing_context import reviewed_context
        labels, columns = reviewed_context(register, catalogue, chunks)
    subjects, missing = {}, {}
    for review in register['reviews']:
        subjects.setdefault(review['subject_id'], [])
        # A claim the review found not stated is offered only as not stated, never as answerable.
        if review.get('finding') == 'not_stated_in_selected_fields':
            missing.setdefault(review['subject_id'], []).append(review['claim'])
        else:
            subjects[review['subject_id']].append(review['claim'])
    readings = {a['reading_id']: a['subject_id'] for a in (catalogue or {}).get('assignments', [])}
    for chunk in chunks:
        subject = readings.get(chunk.get('type_fields', {}).get('reading_id'))
        if subject not in subjects:
            continue
        try:
            limits = json.loads(chunk['text']).get('source_limits', [])
        except (ValueError, TypeError, AttributeError):
            limits = []
        for limit in limits:
            # Owner29Oct: printed defects are shown as printed with a note, not offered as not stated.
            if limit.get('resolution') == 'unresolved' and limit.get('issue') not in PRINTED_DEFECTS:
                missing.setdefault(subject, []).extend(
                    c for c in limit.get('affected_claims', []) if c not in subjects[subject])
    contexts = _reviewed_topic_context(register, catalogue, chunks)
    fields = _reviewed_claim_fields(register, readings, chunks,
        max_fields=MAX_TOPIC_FIELDS if routing_context else 32)
    topics = []
    for s, c in subjects.items():
        not_stated = tuple(dict.fromkeys(missing.get(s, ())))
        topics.append(DocumentTopic(subject_id=s, claims=tuple(dict.fromkeys(c)), source_context=contexts.get(s, ()),
            claim_fields=fields.get(s, {}),
            not_stated=not_stated,
            cues=tuple(NotStatedCue(claim=n, phrases=NOT_STATED_CUES[n]) for n in not_stated if n in NOT_STATED_CUES),
            source_labels=labels.get(s, ()), claim_context=columns.get(s, {})))
    return tuple(topics)


def _reviewed_claim_fields(register, readings, chunks, *, max_fields=32):
    """Only source-present, assigned, reviewed nonblank field names; no new claims."""
    available = {}
    for chunk in chunks:
        reading = chunk.get('type_fields', {}).get('reading_id')
        try:
            fields = json.loads(chunk['text'])['fields']
            names = [f['name'] for f in fields]
            if len(set(names)) != len(names):
                continue
            available[reading] = (chunk['chunk_id'], {f['name'] for f in fields
                if isinstance(f['name'], str) and 0 < len(f['name']) <= 256
                and f.get('source_blank') is False and isinstance(f.get('value'), str) and f['value'].strip()})
        except (ValueError, TypeError, KeyError, AttributeError):
            continue
    result = {}
    for review in register['reviews']:
        if review.get('finding') != 'visible_fields':
            continue
        names = []
        for ref in review.get('field_refs', []):
            reading, name = ref.get('reading_id'), ref.get('field_name')
            identity, fields = available.get(reading, (None, ()))
            if (isinstance(name, str) and readings.get(reading) == review['subject_id']
                    and identity in review.get('reviewed_chunk_ids', ())
                    and name in fields and name not in names):
                names.append(name)
        if names and len(names) <= max_fields:
            result.setdefault(review['subject_id'], {})[review['claim']] = tuple(names)
    return result


def retrieval_storage(release_id, package, *, hosted, authorization_ref):
    """Hosted research release when given (dict(client=..., release_id=...)), else the package."""
    if hosted is not None:
        return HostedReleaseStorage(hosted['client'], pin_release_id=release_id,
            hosted_release_id=hosted['release_id'], authorization_ref=authorization_ref,
            chunks=package['chunks'])
    return PackageStorage(release_id=release_id, manifest=package['manifest'], chunks=package['chunks'],
                          versions=package['versions'], vectors=package['vectors'])


def research_registry():
    return CapabilityRegistry({op: Capability(name, SIGNATURES[op]) for op, name in CAPABILITIES.items()})


def build_research_resources(ledger, package, *, encoder, authorization_ref, hosted=None):
    """Compose one research release: reviewed rules, reviewed package, research labels."""
    return build_multi_research_resources({ledger['scope']['curriculum_id']:ledger}, package,
        encoder=encoder, authorization_ref=authorization_ref, hosted=hosted)


def build_multi_research_resources(ledgers, package, *, encoder, authorization_ref, hosted=None,
                                   program_names=None, curriculum_names=None, routing_context=False):
    """One research release serving several reviewed curricula ({curriculum_id: ledger}).

    Each curriculum keeps its own runtime, release identity and rule-bundle version (listed in the
    pin); the release identity of the set is a digest of those members.
    """
    adapters, members, sources, catalog, labels = {}, [], {}, [], []
    for curriculum, ledger in sorted(ledgers.items()):
        if ledger['scope']['curriculum_id'] != curriculum:
            raise ValueError('curriculum_key_mismatch')
        bundle = prepare_runtime_bundle(ledger)
        runtime = CurriculumRuntime.for_offline_research(bundle, authorization=dict(
            purpose='offline_curriculum_acceptance', authorization_ref=authorization_ref,
            bundle_sha256=bundle['content_sha256'], operations=list(OPERATIONS)))
        adapters[curriculum] = SymbolicAdapter(runtime, research=True)
        members.append(dict(curriculum_id=curriculum, release_id=runtime.release_id,
                            rule_bundle_version=runtime.rule_bundle_version))
        sources.update({s['version_id']: s['byte_sha256'] for s in bundle['ledger']['sources']})
        catalog.extend(research_catalog(ledger)); labels.extend(course_labels(ledger))
    catalog.extend(name_catalog(ledgers, program_names or {}, curriculum_names or {}))
    manifest, chunks = package['manifest'], package['chunks']
    rules_digest = hashlib.sha256(json.dumps(members, sort_keys=True).encode()).hexdigest()
    binding = dict(curricula=members, embedding_set_id=manifest['embedding_set_id'],
        documents=sorted((c['chunk_id'],c['version_id'],c['byte_sha256']) for c in chunks),
        catalogue=package['catalogue'], claim_reviews=package['register'])
    if 'subject_context_budgets' in package:
        if not isinstance(package['subject_context_budgets'], dict):
            raise ValueError('trusted subject context budgets required')
        binding['subject_context_budgets'] = package['subject_context_budgets']
    digest = hashlib.sha256(json.dumps(binding, sort_keys=True, allow_nan=False).encode()).hexdigest()
    release_id, version = 'release-offline-research-set-' + digest[:16], 'offline-research-set-v1-' + rules_digest
    storage = retrieval_storage(release_id, package, hosted=hosted, authorization_ref=authorization_ref)
    policy = SourceAwareEvidencePolicy(release_id=release_id, embedding_set_id=manifest['embedding_set_id'],
        chunks=chunks, catalogue=package['catalogue'], claim_reviews=package['register'])
    sources.update({c['version_id']: c['byte_sha256'] for c in chunks})
    pin = ReleasePin.parse(dict(release_id=release_id, synthetic=False, research_ref=authorization_ref,
        rule_bundle_version=version, curricula=members,
        sources=[dict(version_id=v, byte_sha256=h) for v, h in sorted(sources.items())],
        documents=[dict(chunk_id=c['chunk_id'], version_id=c['version_id'], byte_sha256=c['byte_sha256'])
                   for c in chunks]))
    registry = research_registry()
    budgets = {'pre_enrollment':4096} if any(
        r['subject_id'] == 'pre_enrollment' for r in package['register']['reviews']) else {}
    engine = RetrievalEngine(storage, encoder, SETTINGS, evidence_policy=policy,
        subject_context_budgets=package.get('subject_context_budgets', budgets))
    return ReleaseResources(pin, tuple(catalog), registry, RetrievalAdapter(engine, research=True),
        MultiCurriculumSymbolicAdapter(adapters, release_id=release_id, rule_bundle_version=version),
        topics=topic_menu(package['register'], catalogue=package['catalogue'], chunks=chunks,
                          routing_context=routing_context),  # opt-in reviewed source labels
        document_scope=('audience:undergraduate',), course_labels=tuple(labels))


def name_catalog(ledgers, program_names, curriculum_names):
    """Owner-approved program and curriculum names (24 Oct 2026) for the curricula in this release.
    A name shared by several programs stays on each, so a question using it asks which is meant."""
    entries, programs = [], {}
    for curriculum, ledger in sorted(ledgers.items()):
        programs.setdefault(ledger['scope']['program_id'], ledger)
        if curriculum_names.get(curriculum):
            entries.append(CatalogEntry(kind='curriculum', entity_id=curriculum, program_id=ledger['scope']['program_id'],
                curriculum_id=curriculum, aliases=tuple(dict.fromkeys(curriculum_names[curriculum])),
                source_ref=ledger['sources'][0]['version_id'], review_ref=ledger['reviews'][0]['review_id'], reviewed=True))
    for program, ledger in sorted(programs.items()):
        if program_names.get(program):
            entries.append(CatalogEntry(kind='program', entity_id=program, program_id=program, curriculum_id=None,
                aliases=tuple(dict.fromkeys(program_names[program])),
                source_ref=ledger['sources'][0]['version_id'], review_ref=ledger['reviews'][0]['review_id'], reviewed=True))
    return entries
