"""Cited institutional sources (master 16.1 `GET /sources/{source_id}`).

Only evidence cards cited by answers in this process are served. Cards hold release content only
(`generation.evidence._card` refuses private references). Internal locators stay out; reviewed fields are shown
as readable pairs and a blank source field stays visibly blank (source-gap policy).
"""
from __future__ import annotations

import json
import threading
from collections import OrderedDict

_SOURCE = 'Institutional source'


class SourceRegistry:
    def __init__(self, *, max_cards: int = 4096):
        self._max = max_cards
        self._cards: OrderedDict = OrderedDict()
        self._lock = threading.Lock()

    def remember(self, cards) -> None:
        with self._lock:
            for card in cards:
                self._cards[card.evidence_id] = card
                self._cards.move_to_end(card.evidence_id)
            while len(self._cards) > self._max:
                self._cards.popitem(last=False)

    def get(self, source_id: str):
        with self._lock:
            return self._cards.get(source_id)


def _excerpt(text: str) -> tuple[str, bool]:
    try:
        data = json.loads(text)
    except ValueError:
        return text, False
    if not isinstance(data, dict) or not isinstance(data.get('fields'), list):
        return text, False
    lines = []
    for field in data['fields']:
        label = str(field.get('name', '')).replace('_', ' ').capitalize()
        value = '(blank in the source)' if field.get('source_blank') else str(field.get('value', ''))
        lines.append(f'{label}: {value}')
    return '\n'.join(lines), bool(data.get('source_limits'))


def source_view(card) -> dict:
    cite = card.citations[0]
    excerpt, limited = _excerpt(card.text)
    return {'sourceId': card.evidence_id, 'kind': card.kind, 'title': cite.filename or _SOURCE, 'page': cite.page,
            'printedPageLabel': cite.printed_page_label, 'section': ' / '.join(cite.locator.section_path) or None,
            'excerpt': excerpt, 'hasSourceLimits': limited}
