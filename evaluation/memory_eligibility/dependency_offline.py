"""Release-wide dependency direction replay and Prolog checks; no LLM or network calls.

Uses the harness's existing read-only ledger cache. Expectations are derived from the reviewed
ledger, not an independent source review. Run with --out pointing to ignored audit-evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path

from backend.bintanong_contracts.runtime import PredicateRequest
from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
from backend.bintanong_generation.dependency_reply import dependency_lines
from backend.bintanong_routing.compile import compile_reply
from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_routing.validation import validate_interpretation
from backend.bintanong_runtime.research import course_labels, research_catalog, OPERATIONS
from backend.bintanong_symbolic.bundle import prepare_runtime_bundle
from backend.bintanong_symbolic.runtime import CurriculumRuntime
from .harness import Harness

PHRASES = (
    'Which courses need {course} as a prerequisite?',
    'Ano yung courses na need {course} as pre-requisite?',
    'Kung may subject ba na {course} yung pre requisite',
    'Do succeeding courses need {course} as their pre-req?',
)


def references(tree):
    if tree.get('kind') in ('course', 'co_requisite'):
        return {tree['course_id']}
    return set().union(*(references(item) for item in tree.get('items', ())))


def run(harness, out):
    if not (harness.cache / 'roster.json').is_file():
        raise ValueError('existing_read_only_ledger_cache_required')
    rows = []
    pin, _ = harness.pin_and_package
    registry = CapabilityRegistry({'list_affected_courses': Capability(
        'synthetic_dependency_inspection', ('curriculum_id', 'course_id'))})
    for curriculum, ledger in sorted(harness.ledgers.items()):
        catalog = research_catalog(ledger)
        labels = dict(course_labels(ledger))
        courses = {c['course_id']: c for c in ledger['courses'] if c['review_state'] == 'reviewed'}
        graph = {cid: references(c.get('prerequisites', {})) for cid, c in courses.items()}
        named = {entry.entity_id: entry for entry in catalog}
        alias_owners = {}
        for entry in catalog:
            for alias in entry.aliases:
                alias_owners.setdefault(alias.casefold(), set()).add(entry.entity_id)
        candidates = [cid for cid, entry in named.items()
                      if alias_owners[entry.course_code.casefold()] == {cid}]
        referenced = set().union(*graph.values()) if graph else set()
        linked = next((cid for cid in candidates if cid in referenced), None)
        terminal = next((cid for cid in candidates if cid not in referenced), None)
        selected = list(dict.fromkeys(cid for cid in (linked, terminal) if cid))
        row = dict(curriculum=curriculum, ledger_sha256=hashlib.sha256(
            json.dumps(ledger, sort_keys=True).encode()).hexdigest(), routing_checks=0,
            prolog_checks=0, failures=[], targets=[])
        bundle = prepare_runtime_bundle(ledger)
        runtime = CurriculumRuntime.for_offline_research(bundle, authorization=dict(
            purpose='offline_curriculum_acceptance', authorization_ref=pin['research_authorization_ref'],
            bundle_sha256=bundle['content_sha256'], operations=list(OPERATIONS)))
        for cid in selected:
            entry = named[cid]
            aliases = [entry.course_code, entry.course_code.replace(' ', '')]
            title = courses[cid]['facts'].get('course_title', {}).get('value')
            if title in entry.aliases:
                aliases.append(title)
            ctx = RequestContext(session_id='sess-offline', request_id='req-offline',
                program_id=entry.program_id, curriculum_id=curriculum)
            for alias in dict.fromkeys(aliases):
                for phrase in PHRASES:
                    text = phrase.format(course=alias)
                    quote = dict(text=alias, occurrence=0)
                    for operation in ('list_course_prerequisites', 'check_prerequisite_eligibility'):
                        row['routing_checks'] += 1
                        packet = dict(schema_version='bintanong-interpretation-wire-v4', language='taglish',
                            audience='undergraduate', control=None, route='Symbolic', intent='request',
                            ambiguities=[], claims=[], part_count=1, mentions=[dict(kind='course', quote=quote)],
                            operations=[dict(name=operation, target=quote)], parts=[dict(part_id='r1',
                                quote=dict(text=text, occurrence=0), evidence_need='structured', operation_indices=[0])])
                        result = validate_interpretation(text, ctx, compile_reply(packet, text, ctx, catalog),
                            catalog=catalog, registry=registry, synthetic=True)
                        request = result.decision.predicate_request
                        if request is None or request.predicate != 'list_affected_courses' or not any(
                                i.name == 'course_id' and i.value == cid for i in request.inputs):
                            row['failures'].append(dict(text=text, operation=operation, diagnostic=result.diagnostic))
            expected, frontier = set(), {cid}
            while frontier:
                reached = {course for course, refs in graph.items() if refs & frontier} - expected - {cid}
                expected.update(reached)
                frontier = reached
            request = PredicateRequest.parse(dict(predicate='list_affected_courses', inputs=[
                dict(name='curriculum_id', value=curriculum, fact_ref=None),
                dict(name='course_id', value=cid, fact_ref=None)]))
            result = runtime.list_affected_courses(request)
            row['prolog_checks'] += 1
            if result.status not in ('complete', 'partial') or set(result.course_ids) != expected:
                row['failures'].append(dict(target=labels[cid], status=result.status,
                    expected=sorted(expected), actual=list(result.course_ids)))
            for language in ('en', 'taglish'):
                lines = dependency_lines(result, cid, language, lambda key: labels.get(key, key))
                if any(word in lines[0].casefold() for word in ('fail', 'bagsak', 'block')):
                    row['failures'].append(dict(target=labels[cid], language=language, prose=lines[0]))
            row['targets'].append(dict(code=labels[cid], expected=[labels.get(c, c) for c in sorted(expected)],
                                       unknown_conditions=list(result.unknown_conditions)))
        row['ok'] = bool(selected) and not row['failures']
        rows.append(row)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
        print(curriculum, 'PASS' if row['ok'] else 'FAIL', row['routing_checks'], row['prolog_checks'], flush=True)
    return all(row['ok'] for row in rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if run(Harness(), args.out) else 1)
