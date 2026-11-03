"""Memory/eligibility gates. Usage (from the repository root):

    python -m evaluation.memory_eligibility.gates offline   --out <ignored dir>   # Prolog only, no model, < 1 min
    python -m evaluation.memory_eligibility.gates scenarios --out <ignored dir>   # plan demos, ~12 live turns
    python -m evaluation.memory_eligibility.gates curricula --out <ignored dir> [curriculum ...]  # 3 turns each
    python -m evaluation.memory_eligibility.gates recorded  --out <ignored dir>   # 113 recorded questions

See README.md for the environment and what each gate expects. Expectations come from the reviewed ledgers and the
owner plan; they are not an independent reading of each prospectus.
"""
from __future__ import annotations

import argparse
import asyncio
import re
from pathlib import Path

from .harness import Harness, first_line, write

# ---- offline: the plan's source-backed cases through Prolog (no model) -----------------------------------------

OFFLINE = [  # (name, curriculum, target, [(code, state)], check(result, shown) -> bool)
    ('BSCS 2018 CS 13/L asks about CC 5/L', 'bscs-2018-2019', 'CS 13/L', [],
     lambda r, s: r.decision.outcome == 'unknown' and s(r.decision.missing_facts) == ['completion_unknown:CC 5/L']),
    ('BSCS 2018 CS 13/L after a CC 5/L pass', 'bscs-2018-2019', 'CS 13/L', [('CC 5/L', 'passed')],
     lambda r, s: r.decision.outcome == 'eligible'),
    ('BSCS 2018 CS 13/L, "took it" still asks', 'bscs-2018-2019', 'CS 13/L', [('CC 5/L', 'taken_unknown')],
     lambda r, s: r.decision.outcome == 'unknown'),
    ('Lawrence: CC 5/L without CC 3/L and CC 4/L', 'bscs-2018-2019', 'CC 5/L',
     [('CC 3/L', 'not_passed'), ('CC 4/L', 'not_passed')],
     lambda r, s: s(r.decision.violated_conditions) == ['not_completed:CC 3/L', 'not_completed:CC 4/L']),
    ('Proposed BSCS CS 13/L needs CS 6/L and CS 10/L', 'bscs-proposed-2025-2026', 'CS 13/L', [],
     lambda r, s: s(r.decision.missing_facts) == ['completion_unknown:CS 10/L', 'completion_unknown:CS 6/L']),
    ('BSCE Phy 11/L unmet', 'bsce-2018-2019', 'Phy 11/L',
     [('Math 11/L', 'passed'), ('Math 12/L', 'not_passed'), ('Math 12/L', 'enrolled')],
     lambda r, s: r.decision.outcome == 'ineligible'),
    ('BSME Phy 11/L met', 'bsme-2018-2019', 'Phy 11/L',
     [('Math 11/L', 'passed'), ('Math 12/L', 'not_passed'), ('Math 12/L', 'enrolled')],
     lambda r, s: r.decision.outcome == 'eligible'),
    ('Architecture ACAD-2/L', 'bsa-2018-2019', 'ACAD-2/L', [('ACAD-1/L', 'passed')],
     lambda r, s: r.decision.outcome == 'eligible'),
    ('Nursing NCM 15-103 asks only NCM15-102B', 'bsn-2018-2019', 'NCM 15-103',
     [('NCM15-101A', 'passed'), ('NCM15-101B', 'passed'), ('NCM15-102A', 'passed')],
     lambda r, s: s(r.decision.missing_facts) == ['completion_unknown:NCM15-102B']),
    ('BusEco BE 2001, GE-PC not taken', 'bsba-buseco-2018-2019', 'BE 2001', [('GE-PC', 'not_taken')],
     lambda r, s: r.decision.outcome == 'ineligible'),
    ('BusEco BAC 5 reviewed "None"', 'bsba-buseco-2018-2019', 'BAC 5', [],
     lambda r, s: r.decision.outcome == 'eligible'),
    ('BSEd Math FS 2 no positive verdict', 'bsed-math-2018-2019', 'FS 2', [],
     lambda r, s: r.decision.outcome != 'eligible'),
]


def offline(h, out):
    from backend.bintanong_contracts.runtime import PredicateRequest
    from backend.bintanong_orchestration.adapters import SymbolicAdapter
    from backend.bintanong_routing.contracts import RequestContext
    from backend.bintanong_runtime.research import OPERATIONS
    from backend.bintanong_symbolic.bundle import prepare_runtime_bundle
    from backend.bintanong_symbolic.runtime import CurriculumRuntime
    adapters, codes = {}, {}

    def adapter(c):
        if c not in adapters:
            bundle = prepare_runtime_bundle(h.ledgers[c])
            pin, _ = h.pin_and_package
            adapters[c] = SymbolicAdapter(CurriculumRuntime.for_offline_research(bundle, authorization=dict(
                purpose='offline_curriculum_acceptance', authorization_ref=pin['research_authorization_ref'],
                bundle_sha256=bundle['content_sha256'], operations=list(OPERATIONS))), research=True)
            codes[c] = {x['course_id']: x['facts']['course_code']['value'] for x in h.ledgers[c]['courses']
                        if 'course_code' in x.get('facts', {})}
        return adapters[c]

    def cid(c, code):
        adapter(c)
        found = [i for i, v in codes[c].items() if v.replace(' ', '').casefold() == code.replace(' ', '').casefold()]
        if len(found) != 1:
            raise SystemExit(f'{c}: {code!r} matched {found}')
        return found[0]

    def run(c, predicate, facts, **inputs):
        program = h.ledgers[c]['scope']['program_id']
        context = RequestContext.parse(dict(session_id='sess-gate', request_id='req-gate', program_id=program,
            curriculum_id=c, facts=[dict(fact_id=f'fact-{n}', session_id='sess-gate', program_id=program,
                curriculum_id=c, course_id=cid(c, code), state=state,
                **({'period': 'current'} if state == 'enrolled' else {})) for n, (code, state) in enumerate(facts)]))
        request = PredicateRequest.parse({'predicate': predicate, 'inputs': [
            {'name': 'curriculum_id', 'value': c, 'fact_ref': None},
            *({'name': k, 'value': v, 'fact_ref': None} for k, v in inputs.items())]})
        return asyncio.run(adapter(c).execute(request, context))

    rows = []
    for name, c, target, facts, check in OFFLINE:
        result = run(c, 'check_prerequisite_eligibility', facts, course_id=cid(c, target))
        shown = lambda conds, c=c: sorted(x.split(':', 1)[0] + ':' + codes[c].get(x.split(':', 1)[1], '?')
                                          for x in conds if ':' in x)
        rows.append(dict(case=name, ok=bool(check(result, shown)), outcome=result.decision.outcome))
    term = run('bscs-2018-2019', 'assess_term_prerequisites', [('CC 3/L', 'failed'), ('CC 4/L', 'failed')],
               year_level='2', semester='second_semester')
    groups = {x.code: x.group for x in term.courses if not x.retake}
    rows.append(dict(case='Old BSCS 2nd year 2nd sem after failing CC 3/L and CC 4/L', outcome=str(groups),
                     ok=groups.get('CC 5/L') == 'blocked' and groups.get('CS 4/L') == 'blocked'
                     and groups.get('GE-PS') == 'needs_info'))
    mid = run('bsmid-2019-2020', 'assess_term_prerequisites', [], year_level='2', semester='first_semester')
    rows.append(dict(case='Midwifery 2nd year not covered', ok=mid.status == 'not_covered', outcome=mid.status))
    return rows


# ---- live: the plan's demo scenarios ------------------------------------------------------------------------------

PHY = ("I passed Math 11/L. Hindi ko pa napapasa ang Math 12/L, pero naka-enroll ako sa Math 12/L this term. "
       'Can I take Phy 11/L this term?')
SCENARIOS = {  # name: (curriculum, [(message, status or None, outcome or None, phrase in the first line)])
    'bscs-demo': ('bscs-2018-2019', [
        ('Natake ko na yung CC5/L. Can I take Information Assurance and Security na ba?', 'clarification_needed', 'unknown', 'CC 5/L'),
        ('Oo, pasado.', 'answered', 'eligible', 'CS 13/L'),
        ('What are the prerequisites of CS 4/L?', None, None, 'CS 4/L'),
        ('Pasok ba ako sa prerequisites ng CS 13/L?', 'answered', 'eligible', 'CS 13/L')]),
    'fresh-chat': ('bscs-2018-2019', [('Oo, pasado.', None, None, '')]),
    'proposed-bscs': ('bscs-proposed-2025-2026', [('I passed CC 5/L. Can I take CS 13/L?', 'clarification_needed', 'unknown', 'CS 6/L')]),
    'lawrence': ('bscs-2018-2019', [("Can I take CC 5/L if I haven't passed CC 3/L and CC 4/L?", 'answered', 'ineligible', 'CC 3/L')]),
    'civil': ('bsce-2018-2019', [(PHY, 'answered', 'ineligible', 'Math 12/L')]),
    'mechanical': ('bsme-2018-2019', [(PHY, 'answered', 'eligible', 'Phy 11/L')]),
    'term': ('bscs-2018-2019', [('I failed CC 3/L and CC 4/L. What can I take next sem?', 'clarification_needed', None, 'year level'),
                                ('second year, second sem', 'answered', None, 'Second year, second semester')]),
    'buseco': ('bsba-buseco-2018-2019', [("Can I take BE 2001? I haven't taken GE-PC yet.", 'answered', 'ineligible', 'GE-PC')]),
}


def scenarios(h, out, names=()):
    rows = []
    for name in names or SCENARIOS:
        curriculum, messages = SCENARIOS[name]
        ask = h.chat()
        for n, (text, status, outcome, phrase) in enumerate(messages, 1):
            r = ask(text, curriculum)
            r.update(scenario=name, turn=n, question=text, ok=(status in (None, r['status'])
                     and outcome in (None, r['outcome']) and phrase in first_line(r['reply'])))
            rows.append(r)
            print('PASS' if r['ok'] else 'FAIL', name, n, r['status'], r['outcome'], f"{r['seconds']}s",
                  r['explanation_check'], '|', first_line(r['reply'])[:120], flush=True)
    return rows


# ---- live: every release member -----------------------------------------------------------------------------------

ASK = {'en': 'Can I take {t}?', 'fil': 'Pwede ko na bang kunin ang {t}?', 'taglish': 'Pwede ko na bang i-take ang {t}?'}
YES = {'en': 'Yes, I passed it.', 'fil': 'Oo, pasado.', 'taglish': 'Oo, pasado na.'}
NOT = {'en': "I haven't passed {p} yet. Can I take {t}?", 'fil': 'Hindi ko pa naipapasa ang {p}. Pwede ko na bang kunin ang {t}?',
       'taglish': 'Hindi ko pa na-pass ang {p}. Pwede ko na bang i-take ang {t}?'}


def single_prerequisite(ledger):
    """The first reviewed course whose whole rule is one reviewed, uniquely coded course."""
    courses = {c['course_id']: c for c in ledger['courses']}
    codes = [c['facts']['course_code']['value'] for c in ledger['courses'] if 'course_code' in c.get('facts', {})]
    for c in ledger['courses']:
        rule = c.get('prerequisites') or {}
        pre = courses.get(rule.get('course_id')) if rule.get('kind') == 'course' else None
        if c['review_state'] == 'reviewed' and pre is not None and pre['review_state'] == 'reviewed':
            t, p = c['facts']['course_code']['value'], pre['facts']['course_code']['value']
            if codes.count(t) == 1 and codes.count(p) == 1:
                return t, p
    return None


def curricula(h, out, names=()):
    rows = []
    for n, curriculum in enumerate(names or sorted(h.ledgers)):
        language = ('en', 'fil', 'taglish')[n % 3]
        pair = single_prerequisite(h.ledgers[curriculum])
        if pair is None:
            rows.append(dict(curriculum=curriculum, case='coverage', ok=None, detail='no single-course reviewed rule'))
            print('LIMITED', curriculum, flush=True)
            continue
        t, p = pair
        ask = h.chat()
        first = ask(ASK[language].format(t=t), curriculum)
        second = ask(YES[language], curriculum)
        negative = h.chat()(NOT[language].format(t=t, p=p), curriculum)
        for case, r, ok in (('ask', first, first['outcome'] == 'unknown' and p in first_line(first['reply'])),
                            ('yes', second, second['status'] == 'answered' and second['outcome'] == 'eligible'),
                            ('not_passed', negative, negative['outcome'] == 'ineligible')):
            r.update(curriculum=curriculum, case=case, language=language, target=t, prerequisite=p, ok=ok)
            rows.append(r)
            print('PASS' if ok else 'FAIL', curriculum, case, language, f'{t} <- {p}', r['status'], r['outcome'],
                  f"{r['seconds']}s", r['explanation_check'], flush=True)
        write(out, 'curricula-partial', rows)
    return rows


# ---- live: the recorded single-turn questions ---------------------------------------------------------------------

def recorded(h, out, names=()):
    text = (Path(__file__).resolve().parents[2] / 'Context' / 'sample-query-results-20261103.md').read_text(encoding='utf-8')
    names_to_program = {aliases[0]: program for program, aliases in h.config.program_names.items()}
    editions = {(l['scope']['program_id'], re.search(r'(\d{4}-\d{4})$', c).group(1)): c for c, l in h.ledgers.items()}
    cases, scope = [], None
    for line in text.splitlines():
        heading = re.match(r'### (.+) · (\d{4}-\d{4})$', line)
        if heading:
            scope = editions.get((names_to_program.get(heading.group(1)), heading.group(2)))
        question = re.match(r'\d+\. \*\*(.+)\*\*$', line)
        if question and scope and (not names or scope in names):
            cases.append((scope, question.group(1)))
    rows = []
    for curriculum, question in cases:
        want = (('answered', 'eligible') if re.search('already passed', question, re.I) else
                ('answered', 'ineligible') if re.search(r"haven't taken|have not taken", question, re.I) else
                ('clarification_needed', 'unknown'))
        r = h.chat()(question, curriculum)
        r.update(curriculum=curriculum, question=question, expected=want, ok=(r['status'], r['outcome']) == want)
        rows.append(r)
        print('PASS' if r['ok'] else 'FAIL', curriculum, '|', question[:70], '|', r['status'], r['outcome'],
              f"{r['seconds']}s", flush=True)
        write(out, 'recorded-partial', rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('gate', choices=('offline', 'scenarios', 'curricula', 'recorded'))
    parser.add_argument('names', nargs='*', help='scenario or curriculum ids (default: all)')
    parser.add_argument('--out', type=Path, required=True, help='an ignored directory for the result JSON')
    args = parser.parse_args()
    h = Harness()
    rows = {'offline': lambda: offline(h, args.out), 'scenarios': lambda: scenarios(h, args.out, args.names),
            'curricula': lambda: curricula(h, args.out, args.names), 'recorded': lambda: recorded(h, args.out, args.names)}[args.gate]()
    checked = [r for r in rows if r.get('ok') is not None]
    path = write(args.out, args.gate, rows)
    print(f"{sum(r['ok'] for r in checked)}/{len(checked)} pass; "
          f"explanations accepted {sum(r.get('explanation_check') == 'accepted' for r in checked)}; written {path}")


if __name__ == '__main__':
    main()
