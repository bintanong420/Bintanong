"""Strict printed Charter service tables from reviewed record fields; never inferred associations.

Every field of the service's records must match an explicit grammar, or there is no table and the
answer path is unchanged. Values stay verbatim; a blank source cell stays '' (never zero or none).
Printed data and column labels stay English; only conversational lead-ins follow the reply language.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import json
import re

IGNORED = re.compile(r'^(?:[a-z_]+_label|(?:requirements|process)_column_labels|general_(?:requirements|where)_heading|'
                     r'classification|transaction|audience|service_description)$')
STEP = re.compile(r'^step(?P<step>\d+)_(?:(?P<client>client_step)|(?P<shared>shared_)?(?P<attr>fee|time|person|office)'
                  r'|subaction(?P<sub>\d+)_(?P<sattr>action|time|person|office|fee)|(?P<single>action))$')
REQUIREMENT = re.compile(r'^(?P<key>(?:[a-z]+_)*)requirement(?P<n>\d*)$')
WHERE = re.compile(r'^(?P<key>(?:[a-z]+_)*)where_to_secure(?P<n>\d*)$')
TOTAL = re.compile(r'^(?:whole_service_)?total_(?P<attr>fee|time)$')
ACTION_ATTRS = ('time', 'person', 'office', 'fee')


@dataclass(frozen=True)
class Action:
    action: str
    time: str | None
    person: str | None
    office: str | None
    fee: str | None
    window: str | None = None
    staff: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Step:
    number: int
    client_step: str
    fee: str | None
    actions: tuple[Action, ...]
    shared: tuple[str, ...]  # step-level time/person/office printed once for all actions
    evidence_ids: tuple[str, ...]
    notes: tuple[str, ...] = ()
    heading: str | None = None


@dataclass(frozen=True)
class ServiceTable:
    title: str | None
    office: str | None
    checklist: tuple[tuple[str, str | None], ...]
    steps: tuple[Step, ...]
    total_fee: str | None
    total_time: str | None
    evidence_ids: tuple[str, ...]
    limits: tuple[str, ...] = ()  # unresolved source-limit messages, shown verbatim
    overview_evidence_ids: tuple[str, ...] = ()  # records holding title/office/checklist
    total_evidence_ids: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    checklist_headings: tuple[tuple[int, str], ...] = ()
    printed_total: str | None = None
    field_evidence: tuple[tuple[str, str], ...] = ()


def _put(target, key, value):
    if key in target:
        raise ValueError('duplicate_service_field')
    target[key] = value


def _table(records):
    meta, requirements, wheres, totals, steps, limits = {}, {}, {}, {}, {}, []
    notes, headings = [], {}
    row_numbers = []
    overview, total_records = [], []
    record_row = 0
    grammar, ranges, fragments = set(), [], {}
    local_ranges, continuations, staff, shared_wheres = [], [], {}, {}
    staff_evidence = {}
    field_evidence = []
    for evidence_id, text in records:
        record = json.loads(text)
        fields = record['fields']
        names = [f['name'] for f in fields]
        if any(STEP.match(n) for n in names):
            grammar.add('step')
        if any(re.fullmatch(r'row\d+_\w+', n) for n in names):
            grammar.add('row')
        if 'client_step' in names or 'agency_action' in names:
            grammar.add('record')
        if len(grammar) > 1:
            raise ValueError('mixed_service_grammars')
        if 'client_step' in names or 'agency_action' in names:
            if 'client_step' not in names or 'agency_action' not in names or steps and not record_row:
                raise ValueError('incomplete_record_row')
            record_row += 1
            aliases = dict(client_step='client_step', agency_action='action', fees='fee', fees_shared='fee',
                           processing_time='time', person='person', person_shared='person',
                           office='office', office_shared='office')
            fields = [dict(f, name=f'step{record_row}_{aliases[f["name"]]}' if f['name'] in aliases else f['name'])
                      for f in fields]
        if 'conditional_authorization' in names:
            if names.count('conditional_representation_heading') != 1:
                raise ValueError('unscoped_authorization')
            heading = next(f['value'] for f in fields if f['name'] == 'conditional_representation_heading')
            fields = [dict(f, name='representation_requirement', value=heading + ' ' + f['value'])
                      if f['name'] == 'conditional_authorization' else
                      dict(f, name='representation_where_to_secure')
                      if f['name'] == 'authorization_where_to_secure_shared' else f
                      for f in fields if f['name'] != 'conditional_representation_heading']
        for limit in record.get('source_limits', []):
            # Owner29Oct: defective printed tables are shown as printed with a note (no interpretation).
            if limit['resolution'] == 'unresolved' and limit['message'] not in limits:
                limits.append(limit['message'])
        for field in fields:
            name, value = field['name'], field['value']
            name = {'service_title_and_description': 'service_title', 'service_title_and_note': 'service_title',
                    'office_division': 'office', 'transaction_type': 'transaction', 'who_may_avail': 'audience',
                    'total_fees': 'total_fee', 'total_processing_time': 'total_time'}.get(name, name)
            if (m := re.fullmatch(r'requirement(\d+)_checklist', name)):
                name = f'requirement{m[1]}'
            elif (m := re.fullmatch(r'requirement(\d+)_where_to_secure', name)):
                name = f'where_to_secure{m[1]}'
            elif (m := re.fullmatch(r'row(\d+)_(client_step|agency_actions|fees|processing_time|person|office)', name)):
                row = int(m[1])
                if row not in row_numbers:
                    row_numbers.append(row)
                attr = {'agency_actions': 'action', 'fees': 'fee', 'processing_time': 'time'}.get(m[2], m[2])
                name = f'step{row}_{attr}'
            elif STEP.match(name) and row_numbers:
                raise ValueError('mixed_row_step_grammar')
            if name in ('registration_description', 'second_copy_note', 'service_note', 'printed_description'):
                field_evidence.append((f'note{len(notes)}', evidence_id))
                notes.append(value)
                if evidence_id not in overview:
                    overview.append(evidence_id)
                continue
            if name == 'result_requirements_scope':
                name = 'result_requirements_heading'
            if (m := re.fullmatch(r'(in_campus_|out_of_campus_|result_)requirements_heading', name)):
                field_evidence.append((f'heading:{m[1]}', evidence_id))
                _put(headings, m[1], value)
                if evidence_id not in overview:
                    overview.append(evidence_id)
                continue
            if name == 'result_where_to_secure_shared':
                _put(shared_wheres, 'result_', (value, evidence_id))
                continue
            if name in ('in_campus_where_heading', 'out_of_campus_where_heading', 'end_transaction_label'):
                continue
            if name == 'description':
                continue  # same metadata role as service_description
            if name == 'printed_total':
                _put(totals, 'printed', value)
                total_records.append(evidence_id)
                continue
            if (m := re.fullmatch(r'steps(\d+)_(\d+)_shared_(person|office|time)', name)):
                ranges.append(('steps', int(m[1]), int(m[2]), m[3], value, evidence_id))
                continue
            if (m := re.fullmatch(r'step(\d+)_subactions(\d+)_(\d+)_(person|office|time)', name)):
                ranges.append((int(m[1]), int(m[2]), int(m[3]), m[4], value, evidence_id))
                continue
            if (m := re.fullmatch(r'step(\d+)_local_(person|office|window)', name)):
                number = int(m[1])
                actions = sorted({int(a['sub']) for f in fields if (a := STEP.match(f['name']))
                                  and int(a['step']) == number and a['sub'] and a['sattr'] == 'action'})
                if not actions:
                    raise ValueError('missing_local_actions')
                local_ranges.append((number, actions, m[2], value, evidence_id))
                continue
            if (m := re.fullmatch(r'step(\d+)_continuation_through_step(\d+)_shared_(person|office)', name)):
                number = int(m[1])
                actions = sorted({int(a['sub']) for f in fields if (a := STEP.match(f['name']))
                                  and int(a['step']) == number and a['sub'] and a['sattr'] == 'action'})
                if len(actions) != 1:
                    raise ValueError('ambiguous_continuation_start')
                continuations.append((number, actions[0], int(m[2]), m[3], value, evidence_id))
                continue
            if (m := re.fullmatch(r'step(\d+)_subaction(\d+)_(person|office)(\d+)', name)):
                key = (int(m[1]), int(m[2]))
                _put(staff.setdefault(key, {}).setdefault(int(m[4]), {}), m[3], value)
                staff_evidence.setdefault(key, []).append(evidence_id)
                continue
            if (m := re.fullmatch(r'step(\d+)_phase_heading', name)):
                step = steps.setdefault(int(m[1]), dict(actions={}, shared={}, evidence=[]))
                _put(step, 'heading', value)
                if evidence_id not in step['evidence']:
                    step['evidence'].append(evidence_id)
                continue
            if (m := re.fullmatch(r'step(\d+)_(fee_start|fee_continuation|assisting_person|agency_heading|conditional_time)', name)):
                number, attr = int(m[1]), m[2]
                if attr in ('fee_start', 'fee_continuation'):
                    _put(fragments.setdefault(number, {}), attr, (value, evidence_id))
                    continue
                if attr == 'conditional_time':
                    name = f'step{number}_shared_time'
                else:
                    step = steps.setdefault(number, dict(actions={}, shared={}, evidence=[]))
                    step.setdefault('notes', []).append(value)
                    if evidence_id not in step['evidence']:
                        step['evidence'].append(evidence_id)
                    continue
            if IGNORED.match(name):
                continue
            if (m := TOTAL.match(name)):
                _put(totals, m['attr'], value)
                total_records.append(evidence_id)
                continue
            if not STEP.match(name) and evidence_id not in overview:
                overview.append(evidence_id)
            if name in ('service_title', 'office'):
                _put(meta, name, value)
                field_evidence.append((name, evidence_id))
            elif (m := REQUIREMENT.match(name)):
                _put(requirements, (m['key'], m['n']), value)
                field_evidence.append((f'requirement:{m["key"]}:{m["n"]}', evidence_id))
            elif (m := WHERE.match(name)):
                _put(wheres, (m['key'], m['n']), value)
                field_evidence.append((f'where:{m["key"]}:{m["n"]}', evidence_id))
            elif (m := STEP.match(name)):
                step = steps.setdefault(int(m['step']), dict(actions={}, shared={}, evidence=[]))
                if evidence_id not in step['evidence']:
                    step['evidence'].append(evidence_id)
                if m['client']:
                    _put(step, 'client_step', value)
                elif m['attr']:
                    _put(step['shared'], m['attr'], (value, bool(m['shared'])))
                else:
                    action = steps[int(m['step'])]['actions'].setdefault(int(m['sub'] or 1), {})
                    _put(action, m['sattr'] or 'action', value)
            else:
                raise ValueError('unknown_service_field')
    for prefix, (value, evidence) in shared_wheres.items():
        targets = [key for key in requirements if key[0] == prefix]
        if not targets:
            raise ValueError('missing_shared_checklist')
        for key in targets:
            _put(wheres, key, value)
            field_evidence.append((f'where:{key[0]}:{key[1]}', evidence))
    for first, action, last, attr, value, evidence in continuations:
        if first not in steps or last < first:
            raise ValueError('invalid_continuation')
        local_ranges.append((first, [n for n in steps[first]['actions'] if n >= action], attr, value, evidence))
        if last > first:
            ranges.append(('steps', first + 1, last, attr, value, evidence))
    for number, actions, attr, value, evidence in local_ranges:
        if number not in steps:
            raise ValueError('missing_local_step')
        for action in actions:
            if action not in steps[number]['actions']:
                raise ValueError('missing_local_action')
            _put(steps[number]['actions'][action], attr, value)
        if evidence not in steps[number]['evidence']:
            steps[number]['evidence'].append(evidence)
    for (number, action), people in staff.items():
        if (number not in steps or action not in steps[number]['actions'] or
                sorted(people) != list(range(1, len(people) + 1)) or
                any(set(pair) != {'person', 'office'} for pair in people.values())):
            raise ValueError('incomplete_staff_pairs')
        _put(steps[number]['actions'][action], 'staff', tuple((p['person'], p['office']) for _, p in sorted(people.items())))
        for evidence in staff_evidence[number, action]:
            if evidence not in steps[number]['evidence']:
                steps[number]['evidence'].append(evidence)
    for number, parts in fragments.items():
        if set(parts) != {'fee_start', 'fee_continuation'} or number not in steps:
            raise ValueError('incomplete_fee_fragments')
        _put(steps[number]['shared'], 'fee', (parts['fee_start'][0] + ' ' + parts['fee_continuation'][0], True))
        steps[number]['evidence'] += [e for _, e in parts.values() if e not in steps[number]['evidence']]
    for scope, first, last, attr, value, evidence in ranges:
        if first > last:
            raise ValueError('invalid_shared_range')
        targets = range(first, last + 1)
        for number in targets:
            step = steps.get(number if scope == 'steps' else scope)
            if step is None:
                raise ValueError('missing_range_step')
            if scope == 'steps':
                _put(step['shared'], attr, (value, True))
            else:
                if number not in step['actions']:
                    raise ValueError('missing_range_action')
                _put(step['actions'][number], attr, value)
            if evidence not in step['evidence']:
                step['evidence'].append(evidence)
    start = min(row_numbers) if row_numbers else 1
    if set(wheres) - set(requirements) or not steps or sorted(steps) != list(range(start, start + len(steps))):
        raise ValueError('incomplete_service_table')
    built = []
    for number in sorted(steps):
        step = steps[number]
        if 'client_step' not in step or not step['actions'] or sorted(step['actions']) != list(
                range(1, len(step['actions']) + 1)):
            raise ValueError('incomplete_service_step')
        shared = {k: v for k, (v, _) in step['shared'].items()}
        actions = []
        for _, action in sorted(step['actions'].items()):
            if 'action' not in action or set(action) & set(shared) - {'fee'}:
                raise ValueError('ambiguous_service_action')
            if action.get('staff') and ({'person', 'office'} & (set(action) | set(shared))):
                raise ValueError('ambiguous_staff_pairs')
            actions.append(Action(action['action'], *(action.get(k, shared.get(k) if k != 'fee' else None)
                                                      for k in ACTION_ATTRS), action.get('window'), action.get('staff', ())))
        built.append(Step(number, step['client_step'], shared.get('fee'), tuple(actions),
                          tuple(k for k in ('time', 'person', 'office') if k in shared), tuple(step['evidence']),
                          tuple(step.get('notes', ())), step.get('heading')))
    checklist = tuple((requirements[key], wheres.get(key)) for key in requirements)
    positions, seen, previous_prefix = [], set(), None
    for index, (prefix, _) in enumerate(requirements):
        if prefix in {'in_campus_', 'out_of_campus_', 'result_'} and prefix not in headings:
            raise ValueError('missing_checklist_scope')
        if prefix in headings and prefix != previous_prefix:
            positions.append((index, headings[prefix]))
            seen.add(prefix)
        previous_prefix = prefix
    if set(headings) - seen:
        raise ValueError('empty_checklist_section')
    sources = dict(field_evidence)
    for index, (prefix, number) in enumerate(requirements):
        field_evidence.append((f'item{index}', sources[f'requirement:{prefix}:{number}']))
        if (source := sources.get(f'where:{prefix}:{number}')) is not None:
            field_evidence.append((f'item{index}', source))
    for index, heading in positions:
        prefix = list(requirements)[index][0]
        field_evidence.append((f'heading{index}', sources[f'heading:{prefix}']))
    return ServiceTable(meta.get('service_title'), meta.get('office'), checklist, tuple(built),
                        totals.get('fee'), totals.get('time'), tuple(e for e, _ in records), tuple(limits),
                        tuple(overview), tuple(dict.fromkeys(total_records)), tuple(notes), tuple(positions),
                        totals.get('printed'), tuple(field_evidence))


def parse_service(records):
    """[(evidence_id, record_text)] in source order -> ServiceTable, or None outside the strict grammar."""
    try:
        phase_steps = {'application': set(), 'result': set()}
        result_headings = []
        plain_steps = False
        for _, text in records:
            for field in json.loads(text)['fields']:
                name = field['name']
                plain_steps |= bool(STEP.match(name))
                if (m := re.fullmatch(r'(application|result)_step(\d+)_.+', name)):
                    phase_steps[m[1]].add(int(m[2]))
                if name == 'result_phase_heading':
                    result_headings.append(field['value'])
        numbers = {}
        if any(phase_steps.values()):
            if plain_steps or len(result_headings) != 1 or any(
                    not steps or sorted(steps) != list(range(1, len(steps) + 1)) for steps in phase_steps.values()):
                return None
            normalized = []
            for evidence, text in records:
                body = json.loads(text)
                fields = []
                for field in body['fields']:
                    name = field['name']
                    if (m := re.fullmatch(r'(application|result)_step(\d+)_(.+)', name)):
                        original = int(m[2])
                        number = original + (len(phase_steps['application']) if m[1] == 'result' else 0)
                        numbers[number] = original
                        name = f'step{number}_{m[3]}'
                    elif name == 'result_phase_heading':
                        name = f'step{len(phase_steps["application"]) + 1}_phase_heading'
                    fields.append(dict(field, name=name))
                normalized.append((evidence, json.dumps(dict(body, fields=fields))))
            records = normalized
        if any(f['name'] == 'client_step' for _, text in records for f in json.loads(text)['fields']):
            grouped = [(json.loads(text)['service_group'], evidence, text) for evidence, text in records]
            identities = {(g['logical_step_id'], g['part_count']) for g, _, _ in grouped}
            if len(identities) != 1:
                return None
            count = grouped[0][0]['part_count']
            if sorted(g['part_order'] for g, _, _ in grouped) != list(range(count)):
                return None
            records = [(e, t) for g, e, t in sorted(grouped, key=lambda item: item[0]['part_order'])]
        table = _table(records)
        return replace(table, steps=tuple(replace(s, number=numbers[s.number]) for s in table.steps)) if numbers else table
    except (ValueError, KeyError, TypeError):
        return None


ORIGINAL_NOTE = dict(
    en="Note: these steps are shown exactly as printed in the Citizen's Charter; any inconsistency comes "
       'from the original document.',
    taglish="Note: Ipinapakita ito nang eksakto gaya ng nakaprint sa Citizen's Charter; anumang inconsistency "
            'ay galing mismo sa original na dokumento.')
LEADS = dict(en=dict(requirements='Requirements:', steps='Steps to follow:', fees='Fees as printed:',
                     processing_time='Processing time as printed:'),
             taglish=dict(requirements='Eto ang mga requirements na kailangan mo:',
                          steps='Eto ang mga kailangan mong gawin:',
                          fees='Eto ang mga bayarin ayon sa nakaprint:',
                          processing_time='Eto ang processing time ayon sa nakaprint:'))
LABELS = (('person', 'Person responsible'), ('office', 'Office'), ('time', 'Processing time'))
BLANK = '(blank in the printed table)'
MAX_CLAIM_CHARS, MAX_CLAIM_RECORDS = 1200, 8  # ProseClaim limits
PIECE_CHARS = MAX_CLAIM_CHARS - 250  # room for the lead line, printed total, limits and note


def _value(value):
    return BLANK if value == '' else _end(value)


def _end(text):
    return text.rstrip().rstrip('.')  # printed values may already end with a period


def _columns(source, keys, indent):
    return [f'{indent}{label}: {_value(getattr(source, key))}' for key, label in LABELS
            if key in keys and getattr(source, key) is not None]


def _step_units(step):
    """Indivisible line blocks: header, each office action with its own columns, shared columns."""
    header = ([step.heading] if step.heading else []) + [f'Step {step.number}: {_end(step.client_step)}']
    if step.fee is not None:
        header.append(f'Fee: {_value(step.fee)}')
    header += list(step.notes)
    units = [header + ['Office actions:']]
    own = [k for k, _ in LABELS if k not in step.shared]
    for action in step.actions:
        unit = [f'  {_end(action.action)}', *_columns(action, own, '    ')]
        if action.window is not None:
            unit.append(f'    {_value(action.window)}')
        for person, office in action.staff:
            unit += [f'    Person responsible: {_value(person)}', f'    Office: {_value(office)}']
        if action.fee is not None:
            unit.append(f'    Fee: {_value(action.fee)}')
        units.append(unit)
    shared = _columns(step.actions[0], step.shared, '')
    if shared:
        units.append(shared)
    return units


def _step_pieces(step):
    """One text per claim; a step too long for one claim continues as 'Step N (continued):'."""
    pieces, current = [], []
    for unit in _step_units(step):
        if current and len('\n'.join(current + unit)) > PIECE_CHARS:
            pieces.append('\n'.join(current))
            current = [f'Step {step.number} (continued):']
        current += unit
    pieces.append('\n'.join(current))
    return pieces


def _fits(text, ids):
    return len(text) <= MAX_CLAIM_CHARS and len(ids) <= MAX_CLAIM_RECORDS


def _detail_lines(table, detail):
    """Printed fees or processing times only (owner 28 Oct 2026: answer the detail asked), one line per
    printed value with its step; the printed total for that column ends the list."""
    lines = []
    if detail == 'fees':
        for step in table.steps:
            if step.fee is not None:
                lines.append(f'Step {step.number}: {_end(step.client_step)} — Fee: {_value(step.fee)}')
            lines += [f'Step {step.number}: {_end(step.client_step)} — {_end(a.action)} — Fee: {_value(a.fee)}'
                      for a in step.actions if a.fee is not None]
        total = table.total_fee
    else:
        for step in table.steps:
            if 'time' in step.shared:
                lines.append(f'Step {step.number}: {_end(step.client_step)} — Processing time: '
                             f'{_value(step.actions[0].time)}')
                continue
            timed = [a for a in step.actions if a.time is not None]
            if timed:
                lines.append(f'Step {step.number}: {_end(step.client_step)}')
                lines += [f'  {_end(a.action)} — Processing time: {_value(a.time)}' for a in timed]
        total = table.total_time
    if total is not None:
        lines.append(f'Printed total: {_value(total)}')
    return lines


def render_service(table, language, max_claims=8, detail='whole'):
    """Host claims [(text, evidence_ids)]: overview/checklist, one claim per step (merging consecutive
    steps only when the claim budget requires), then the printed total, source limits and the original-
    document note. None when the steps cannot fit the claim budget within ProseClaim limits. A detail
    other than 'whole' keeps only the checklist, the printed fees or the printed processing times."""
    key = 'taglish' if language in ('taglish', 'fil') else 'en'
    limits = ([f'Source limitation: {m}' for m in table.limits] + [ORIGINAL_NOTE[key]]) if table.limits else []
    if detail in ('fees', 'processing_time'):
        lines = _detail_lines(table, detail)
        if not lines:
            return None
        text = '\n'.join([_end(table.title or ''), LEADS[key][detail], *lines, *limits]).lstrip('\n')
        ids = tuple(dict.fromkeys((*(e for s in table.steps for e in s.evidence_ids), *table.total_evidence_ids)))
        return ((text, ids),) if _fits(text, ids) and max_claims >= 1 else None
    def sources(name):
        return tuple(dict.fromkeys(e for n, e in table.field_evidence if n == name)) or table.overview_evidence_ids

    overview = []
    if table.title:
        overview.append((_end(table.title), sources('service_title')))
    if table.office:
        overview.append((f'Office: {table.office}', sources('office')))
    overview += [(_end(note), sources(f'note{i}')) for i, note in enumerate(table.notes)]
    if table.checklist:
        headings = dict(table.checklist_headings)
        for index, (r, w) in enumerate(table.checklist):
            lines, ids = [], sources(f'item{index}')
            if index == 0:
                lines.append(LEADS[key]['requirements'])
            if index in headings:
                lines.append(headings[index])
                ids = tuple(dict.fromkeys((*ids, *sources(f'heading{index}'))))
            lines.append(f'- {_end(r)}' + (f' — where to secure: {_end(w)}' if w else ''))
            overview.append(('\n'.join(lines), ids))
    claims = []
    for text, ids in overview:
        if claims and _fits(claims[-1][0] + '\n' + text, tuple(dict.fromkeys((*claims[-1][1], *ids)))):
            previous, prior_ids = claims.pop()
            claims.append((previous + '\n' + text, tuple(dict.fromkeys((*prior_ids, *ids)))))
        else:
            claims.append((text, ids))
    if detail == 'requirements':
        if not table.checklist:
            return None
        if limits:
            claims.append(('\n'.join(limits), table.overview_evidence_ids or claims[-1][1]))
        return tuple(claims) if len(claims) <= max_claims and all(_fits(t, ids) for t, ids in claims) else None
    tail = []
    if table.printed_total is not None:
        tail.append(table.printed_total)
    if table.total_fee is not None or table.total_time is not None:
        tail.append('Printed total: ' + '; '.join(_value(v) for v in (table.total_fee, table.total_time) if v is not None))
    tail += limits
    budget = max_claims - len(claims)
    groups = [[(piece, step.evidence_ids)] for step in table.steps for piece in _step_pieces(step)]
    while len(groups) > budget:  # merge the consecutive pair that stays smallest
        options = [(len('\n'.join(t for t, _ in groups[i] + groups[i+1])), i) for i in range(len(groups) - 1)]
        if not options:
            return None
        _, i = min(options)
        groups[i:i+2] = [groups[i] + groups[i+1]]
    for index, group in enumerate(groups):
        lines = [LEADS[key]['steps']] if index == 0 else []
        lines += [t for t, _ in group]
        ids = tuple(dict.fromkeys(e for _, evidence in group for e in evidence))
        if index == len(groups) - 1:
            lines += tail
            ids = tuple(dict.fromkeys((*ids, *table.total_evidence_ids)))
        claims.append(('\n'.join(lines), ids))
    if budget < 1 or not all(_fits(t, ids) for t, ids in claims):
        return None
    return tuple(claims)
