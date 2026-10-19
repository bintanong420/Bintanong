"""Model-selected conversational style and literal evidence, never a word-list classifier."""
from copy import deepcopy
from typing import Annotated, Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Record
from .contracts import Interpretation

WIRE_SCHEMA_VERSION = 'bintanong-router-proposal-v2'
Fragment = Annotated[str, Field(min_length=1, max_length=160)]
_REQUIREMENTS = {'english_only':(True,False), 'filipino':(False,True),
                 'taglish':(True,True), 'unknown':(False,False)}
_LANGUAGE = {'english_only':'en', 'filipino':'fil', 'taglish':'taglish', 'unknown':'unknown'}


class StyleEvidence(Record):
    english_fragments: tuple[Fragment, ...] = Field(max_length=4)
    filipino_fragments: tuple[Fragment, ...] = Field(max_length=4)
    preferred_response_style: Literal['english_only', 'filipino', 'taglish', 'unknown']

    @model_validator(mode='after')
    def _consistent(self):
        if any(not f.strip() for f in (*self.english_fragments, *self.filipino_fragments)):
            raise ValueError('blank_style_fragment')
        if (bool(self.english_fragments), bool(self.filipino_fragments)) != _REQUIREMENTS[self.preferred_response_style]:
            raise ValueError('inconsistent_style_evidence')
        return self

    @property
    def language(self):
        return _LANGUAGE[self.preferred_response_style]

    def ground(self, original_text):
        if any(f not in original_text for f in (*self.english_fragments, *self.filipino_fragments)):
            raise ValueError('ungrounded_response_style')


def _style_schema():
    schema = StyleEvidence.model_json_schema()
    # Omit display annotations from the model token budget; validation is unchanged.
    schema.pop('title', None)
    for prop in schema['properties'].values():
        prop.pop('title', None)
    schema['properties']['preferred_response_style'].pop('type', None)  # enum already fixes types
    branches = []
    for name, (english, filipino) in _REQUIREMENTS.items():
        branch = deepcopy(schema)
        branch['properties']['preferred_response_style'] = {'const':name}
        for field, needed in [('english_fragments', english), ('filipino_fragments', filipino)]:
            branch['properties'][field]['minItems' if needed else 'maxItems'] = 1 if needed else 0
        branches.append(branch)
    schema['oneOf'] = branches
    return schema


def model_schema(canonical_schema):
    """Project the canonical routing schema to wire-v2 without copying its rule fields."""
    schema = deepcopy(canonical_schema)
    schema.setdefault('$defs', {})['ResponseStyleEvidence'] = _style_schema()
    for obj in [schema, *schema.get('oneOf', [])]:
        props = obj['properties']
        props.pop('language')
        props['style'] = {'$ref':'#/$defs/ResponseStyleEvidence'}
        first = ('schema_version', 'style', 'audience', 'route', 'control')
        obj['properties'] = {k:props[k] for k in (*first, *(k for k in props if k not in first))}
        obj['properties']['schema_version']['const'] = WIRE_SCHEMA_VERSION
        obj['required'] = ['style' if k == 'language' else k for k in obj['required']]
    return schema


def decode_model_proposal(data):
    if not isinstance(data, dict) or data.get('schema_version') != WIRE_SCHEMA_VERSION or 'language' in data:
        raise ValueError('invalid_model_proposal_version_or_fields')
    style = StyleEvidence.parse(data.get('style'))
    canonical = {k:v for k,v in data.items() if k != 'style'}
    canonical.update(schema_version=Interpretation.SCHEMA_VERSION, language=style.language)
    return Interpretation.parse(canonical), style
