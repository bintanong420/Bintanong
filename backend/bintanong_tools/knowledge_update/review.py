from __future__ import annotations

import copy
import json
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from ..prospectus_extractor.ledger import LedgerLock
from .files import digest, encoded, write_json
from .prepare import load_packet

AUDIENCES = {'undergraduate', 'excluded', 'unresolved'}
DECISIONS = {'accepted', 'corrected', 'unresolved', 'pending'}


class ReviewSession:
    def __init__(self, root: Path, reviewer: str):
        if (not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 120
                or any(ord(c) < 32 for c in reviewer)):
            raise ValueError('explicit researcher identity required')
        self.root = Path(root).resolve()
        self.packet = load_packet(root)
        self.reviewer = reviewer.strip()
        self.path = self.root / 'review/decisions.jsonl'
        if self.path.is_symlink() or self.path.parent.is_symlink():
            raise ValueError('symlink review journal refused')
        self.guard = threading.RLock()
        self.lock = LedgerLock(self.path, 'knowledge review: ' + self.reviewer)
        self.lock.__enter__()
        try:
            self.events = self._read_events()
        except BaseException:
            self.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        self.lock.release()

    def _read_events(self) -> list[dict]:
        if not self.path.exists():
            return []
        if self.path.stat().st_size > 32 * 1024 * 1024:
            raise ValueError('review journal exceeds 32 MiB')
        events = []
        previous = None
        operations = set()
        try:
            for line in self.path.read_bytes().splitlines():
                value = json.loads(line)
                core = dict(value)
                sha = core.pop('event_sha256')
                if (sha != digest(encoded(core)) or core['previous_sha256'] != previous
                        or core['packet_id'] != self.packet['packet_id']
                        or core['revision'] != len(events) + 1 or core['operation_id'] in operations):
                    raise ValueError('review journal identity or order mismatch')
                self._validate(core)
                row = next(r for r in self.packet['items'] if r['id'] == core['item_id'])
                doc = next(d for d in self.packet['documents'] if d['id'] == row['document_id'])
                if core['source_sha256'] != doc['sha256']:
                    raise ValueError('review journal source mismatch')
                previous = sha
                operations.add(core['operation_id'])
                events.append(value)
        except (KeyError, TypeError, StopIteration, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError('review journal is malformed or interrupted; preserve it for recovery') from exc
        return events

    def _validate(self, command: dict) -> dict:
        if not isinstance(command, dict):
            raise ValueError('review decision must be an object')
        row = next((r for r in self.packet['items'] if r['id'] == command.get('item_id')), None)
        if row is None or not row['fields']:
            raise ValueError('unknown or unsupported review item')
        if row.get('reference_only'):
            raise ValueError('prior reviewed references are read-only; prepare a new candidate for a new source review')
        if type(command.get('revision')) is not int or command['revision'] < 0:
            raise ValueError('invalid revision')
        if (not isinstance(command.get('operation_id'), str)
                or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', command['operation_id'])):
            raise ValueError('invalid operation identity')
        if not isinstance(command.get('audience'), str) or command['audience'] not in AUDIENCES:
            raise ValueError('invalid audience decision')
        if (not isinstance(command.get('reason'), str) or not command['reason'].strip()
                or len(command['reason']) > 8000):
            raise ValueError('a review reason is required')
        companions = command.get('companions')
        ids = {r['id'] for r in self.packet['items']}
        if (not isinstance(companions, list) or any(not isinstance(i, str) or i not in ids for i in companions)
                or len(set(companions)) != len(companions) or row['id'] in companions):
            raise ValueError('invalid companion mapping')
        fields = command.get('fields')
        if not isinstance(fields, dict) or set(fields) != {f['name'] for f in row['fields']}:
            raise ValueError('review must name the exact source fields')
        for field in row['fields']:
            result = fields[field['name']]
            if (not isinstance(result, dict) or set(result) != {'decision', 'value'}
                    or not isinstance(result.get('decision'), str) or result['decision'] not in DECISIONS
                    or type(result.get('value')) is not type(field['original_value'])):
                raise ValueError('invalid typed field decision')
            if field['source_blank'] and result['value'] != '':
                raise ValueError('literal blank cannot acquire invented content')
            if result['decision'] == 'accepted' and result['value'] != field['original_value']:
                raise ValueError('changed text needs an explicit correction decision')
            if len(encoded(result)) > 256 * 1024:
                raise ValueError('review field exceeds size limit')
        gaps = command.get('gaps')
        if not isinstance(gaps, list) or len(gaps) > 100:
            raise ValueError('invalid source-gap records')
        for gap in gaps:
            if (not isinstance(gap, dict) or set(gap) != {'issue', 'field_names', 'visible_text', 'affected_claims'}
                    or not isinstance(gap['issue'], str) or not gap['issue'].strip()
                    or not isinstance(gap['field_names'], list) or not gap['field_names']
                    or any(name not in fields for name in gap['field_names'])
                    or not isinstance(gap['visible_text'], str)
                    or not isinstance(gap['affected_claims'], list) or not gap['affected_claims']
                    or any(not isinstance(s, str) or not s.strip() for s in gap['affected_claims'])):
                raise ValueError('source gap needs fields, visible text and affected claims')
        return row

    def save(self, command: dict) -> dict:
        with self.guard:
            if self.lock._fd is None:
                raise ValueError('review session is closed')
            load_packet(self.root)
            self.events = self._read_events()
            required = {'item_id', 'revision', 'operation_id', 'audience', 'reason', 'companions', 'gaps', 'fields'}
            if not isinstance(command, dict) or set(command) != required:
                raise ValueError('invalid review command fields')
            row = self._validate(command)
            request_sha = digest(encoded(command))
            for event in self.events:
                if event['operation_id'] == command['operation_id']:
                    if event['request_sha256'] != request_sha:
                        raise ValueError('operation identity already used for another decision')
                    return {'revision': event['revision'], 'event_sha256': event['event_sha256']}
            if command['revision'] != len(self.events):
                raise ValueError('stale review revision; reload before editing')
            doc = next(d for d in self.packet['documents'] if d['id'] == row['document_id'])
            event = copy.deepcopy(command)
            event.update(revision=len(self.events) + 1, packet_id=self.packet['packet_id'],
                source_sha256=doc['sha256'], reviewer=self.reviewer,
                owner_statement=command['reason'], request_sha256=request_sha,
                previous_sha256=self.events[-1]['event_sha256'] if self.events else None,
                recorded_at=datetime.now(timezone.utc).isoformat())
            event['event_sha256'] = digest(encoded(event))
            with self.path.open('ab') as stream:
                stream.write(encoded(event))
                stream.flush()
                os.fsync(stream.fileno())
            self.events = self._read_events()
            return {'revision': event['revision'], 'event_sha256': event['event_sha256']}

    def state(self) -> dict:
        with self.guard:
            load_packet(self.root)
            self.events = self._read_events()
            rows = copy.deepcopy(self.packet['items'])
            latest = {e['item_id']: e for e in self.events}
            for row in rows:
                event = latest.get(row['id'])
                if event:
                    row.update(audience=event['audience'], companions=event['companions'],
                               reason=event['reason'], gaps=event['gaps'])
                    for field in row['fields']:
                        choice = event['fields'][field['name']]
                        field.update(decision=choice['decision'], reviewed_value=copy.deepcopy(choice['value']))
            return {'packet_id': self.packet['packet_id'], 'revision': len(self.events),
                    'source_basis': copy.deepcopy(self.packet.get('source_basis')),
                    'documents': copy.deepcopy(self.packet['documents']), 'items': rows,
                    'researcher': self.reviewer, 'candidate_only': True}

    def history(self) -> list[dict]:
        with self.guard:
            self.events = self._read_events()
            return copy.deepcopy(self.events)

    def export(self) -> dict:
        with self.guard:
            state = self.state()
            events = {digest(encoded(e)): encoded(e).decode('utf-8') for e in self.events}
            latest = {e['item_id']: digest(encoded(e)) for e in self.events}
            readings, anchors, withheld = [], {}, []
            docs = {d['id']: d for d in self.packet['documents']}
            for row in state['items']:
                if row.get('reference_only'):
                    withheld.append({'item_id': row['id'], 'reason': 'prior_review_reference'})
                    continue
                if not row['fields'] or any(not f['locator']['physical_pages'] for f in row['fields']):
                    withheld.append({'item_id': row['id'], 'reason': 'missing_policy_fields_or_pages'})
                    continue
                doc = docs[row['document_id']]
                version = next(v for v in doc['source_versions'] if v['byte_sha256'] == doc['sha256'])
                ref = latest.get(row['id'])
                audience = row['audience']
                reading = {'reading_id': row['id'], 'source_sha256': doc['sha256'],
                    'version_id': version['version_id'],
                    'intended_audience': 'undergraduate' if audience == 'undergraduate' else 'unknown',
                    'applicability': audience if audience != 'unresolved' else 'unknown',
                    'applicability_evidence_ref': ref, 'fields': [], 'gaps': copy.deepcopy(row.get('source_gaps', [])),
                    'preserved_evidence': [{'artifact': 'packet.json#' + row['id'],
                                            'sha256': digest((self.root / 'packet.json').read_bytes())}]}
                if 'reference_chunk' in row:
                    reading['reference_chunk'] = copy.deepcopy(row['reference_chunk'])
                anchors[row['id']] = {}
                for field in row['fields']:
                    reading['fields'].append({k: copy.deepcopy(field[k]) for k in
                        ('name', 'original_value', 'reviewed_value', 'decision', 'source_blank', 'locator')})
                    reading['fields'][-1]['review_event_sha256'] = ref
                    anchors[row['id']][field['name']] = copy.deepcopy(field['spans'])
                    if (field['decision'] == 'corrected' and isinstance(field['reviewed_value'], str)
                            and len(anchors[row['id']][field['name']]) == 1):
                        span = anchors[row['id']][field['name']][0]
                        span['text'] = field['reviewed_value']
                        span['extraction'] = {**span['extraction'], 'resolution_method': 'human_review', 'repair_id': ref}
                for index, gap in enumerate(row.get('gaps', [])):
                    pages = sorted({p for f in row['fields'] if f['name'] in gap['field_names']
                                    for p in f['locator']['physical_pages']})
                    reading['gaps'].append({**gap, 'gap_id': row['id'] + ':gap-' + str(index),
                        'locator': {'physical_pages': pages, 'field': ', '.join(gap['field_names'])}})
                readings.append(reading)
            value = {'schema_version': 'bintanong-review-export-v1', 'packet_id': self.packet['packet_id'],
                'revision': state['revision'], 'candidate_only': True, 'readings': readings,
                'review_events': events, 'field_spans': anchors, 'withheld_items': withheld,
                'required_readings': {r['id']: r['companions'] for r in state['items'] if r['companions']}}
            write_json(self.root / 'review/export.json', value)
            return value
