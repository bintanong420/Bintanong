"""Produce new model-wire fixtures from authored normalized test records.

This never calls the production normalizer. Literal wire boundary tests separately
prove the actual accepted protocol, including rejection of legacy model packets.
"""
from copy import deepcopy


def wire_fixture(value, original_text=None):
    value = deepcopy(value)
    if value.get('schema_version') != 'bintanong-interpretation-v2':
        return value

    def quote(item):
        text = item.get('text')
        occurrence = 0
        if original_text is not None and isinstance(text, str) and text:
            positions = []
            found = original_text.find(text)
            while found >= 0:
                positions.append(found)
                found = original_text.find(text, found + 1)
            if len(positions) > 1:
                start = item.get('start')
                occurrence = positions.index(start) if start in positions else 8191
        return dict(text=text, occurrence=occurrence)

    references = [quote(m) for m in value['mentions']]

    def reference(index):
        if type(index) is int and 0 <= index < len(references):
            return deepcopy(references[index])
        return index  # malformed authored references must remain malformed

    def replace_span(item):
        return {k:v for k,v in item.items() if k not in ('text', 'start', 'end')} | {'quote':quote(item)}

    value['schema_version'] = 'bintanong-interpretation-wire-v3'
    value.pop('intent', None)  # the host, not the model, supplies these (wire v3)
    value.pop('reason', None)
    value['part_count'] = len(value['parts'])
    value['mentions'] = [replace_span(m) for m in value['mentions']]
    value['claims'] = [replace_span(c) | {'entity':reference(c['entity'])} for c in value['claims']]
    value['operations'] = [dict(o, target=reference(o['target'])) for o in value['operations']]
    value['parts'] = [replace_span(p) for p in value['parts']]
    return value
