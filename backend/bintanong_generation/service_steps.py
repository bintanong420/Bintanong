"""Strict printed Charter service tables from reviewed record fields; never inferred associations.

Every field of the service's records must match an explicit grammar, or there is no table and the
answer path is unchanged. Values stay verbatim; a blank source cell stays '' (never zero or none).
Printed data and column labels stay English; only conversational lead-ins follow the reply language.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import re

IGNORED = re.compile(r'^(?:[a-z_]+_label|(?:requirements|process)_column_labels|general_(?:requirements|where)_heading|'
                     r'classification|transaction|audience|service_description)$')
STEP = re.compile(r'^step(?P<step>\d+)_(?:(?P<client>client_step)|(?P<shared>shared_)?(?P<attr>fee|time|person|office)'
                  r'|subaction(?P<sub>\d+)_(?P<sattr>action|time|person|office|fee)|(?P<single>action))$')
REQUIREMENT = re.compile(r'^(?P<key>(?:[a-z]+_)?)requirement(?P<n>\d*)$')
WHERE = re.compile(r'^(?P<key>(?:[a-z]+_)?)where_to_secure(?P<n>\d*)$')
TOTAL = re.compile(r'^(?:whole_service_)?total_(?P<attr>fee|time)$')
ACTION_ATTRS = ('time', 'person', 'office', 'fee')


@dataclass(frozen=True)
class Action:
    action: str
    time: str | None
    person: str | None
    office: str | None
    fee: str | None


@dataclass(frozen=True)
class Step:
    number: int
    client_step: str
    fee: str | None
    actions: tuple[Action, ...]
    shared: tuple[str, ...]  # step-level time/person/office printed once for all actions
    evidence_ids: tuple[str, ...]


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


def _put(target, key, value):
    if key in target:
        raise ValueError('duplicate_service_field')
    target[key] = value


def _table(records):
    meta, requirements, wheres, totals, steps, limits = {}, {}, {}, {}, {}, []
    overview, total_records = [], []
    for evidence_id, text in records:
        record = json.loads(text)
        for limit in record.get('source_limits', []):
            # Owner29Oct: defective printed tables are shown as printed with a note (no interpretation).
            if limit['resolution'] == 'unresolved' and limit['message'] not in limits:
                limits.append(limit['message'])
        for field in record['fields']:
            name, value = field['name'], field['value']
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
            elif (m := REQUIREMENT.match(name)):
                _put(requirements, (m['key'], m['n']), value)
            elif (m := WHERE.match(name)):
                _put(wheres, (m['key'], m['n']), value)
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
    if set(wheres) - set(requirements) or not steps or sorted(steps) != list(range(1, len(steps) + 1)):
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
            actions.append(Action(action['action'], *(action.get(k, shared.get(k) if k != 'fee' else None)
                                                      for k in ACTION_ATTRS)))
        built.append(Step(number, step['client_step'], shared.get('fee'), tuple(actions),
                          tuple(k for k in ('time', 'person', 'office') if k in shared), tuple(step['evidence'])))
    checklist = tuple((requirements[key], wheres.get(key)) for key in requirements)
    return ServiceTable(meta.get('service_title'), meta.get('office'), checklist, tuple(built),
                        totals.get('fee'), totals.get('time'), tuple(e for e, _ in records), tuple(limits),
                        tuple(overview), tuple(dict.fromkeys(total_records)))


def parse_service(records):
    """[(evidence_id, record_text)] in source order -> ServiceTable, or None outside the strict grammar."""
    try:
        return _table(records)
    except (ValueError, KeyError, TypeError):
        return None


ORIGINAL_NOTE = dict(
    en="Note: these steps are shown exactly as printed in the Citizen's Charter; any inconsistency comes "
       'from the original document.',
    taglish="Note: Ipinapakita ito nang eksakto gaya ng nakaprint sa Citizen's Charter; anumang inconsistency "
            'ay galing mismo sa original na dokumento.')
LEADS = dict(en=dict(requirements='Requirements:', steps='Steps to follow:'),
             taglish=dict(requirements='Eto ang mga requirements na kailangan mo:',
                          steps='Eto ang mga kailangan mong gawin:'))
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
    header = [f'Step {step.number}: {_end(step.client_step)}']
    if step.fee is not None:
        header.append(f'Fee: {_value(step.fee)}')
    units = [header + ['Office actions:']]
    own = [k for k, _ in LABELS if k not in step.shared]
    for action in step.actions:
        unit = [f'  {_end(action.action)}', *_columns(action, own, '    ')]
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


def render_service(table, language, max_claims=8):
    """Host claims [(text, evidence_ids)]: overview/checklist, one claim per step (merging consecutive
    steps only when the claim budget requires), then the printed total, source limits and the original-
    document note. None when the steps cannot fit the claim budget within ProseClaim limits."""
    key = 'taglish' if language in ('taglish', 'fil') else 'en'
    overview = [x for x in (_end(table.title or ''), f'Office: {table.office}' if table.office else '') if x]
    if table.checklist:
        overview.append(LEADS[key]['requirements'])
        overview += [f'- {_end(r)}' + (f' — where to secure: {_end(w)}' if w else '') for r, w in table.checklist]
    claims = [('\n'.join(overview), table.overview_evidence_ids or table.steps[0].evidence_ids)] if overview else []
    tail = []
    if table.total_fee is not None or table.total_time is not None:
        tail.append('Printed total: ' + '; '.join(_value(v) for v in (table.total_fee, table.total_time) if v is not None))
    if table.limits:
        tail += [f'Source limitation: {m}' for m in table.limits] + [ORIGINAL_NOTE[key]]
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
