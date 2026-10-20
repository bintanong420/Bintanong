"""One model call, separately grounded interpretation and response-style evidence."""
from dataclasses import replace
import hashlib

from pydantic import ValidationError

from ..bintanong_contracts.base import Contract
from ..bintanong_contracts.runtime import NormalizedQuery
from ..bintanong_contracts.schema_display import compact_for_prompt
from .contracts import Interpretation, RequestContext, prepare_query
from .prompt import SYSTEM_PROMPT, build_messages as routing_messages, canonical, digest
from .prompt import output_schema as routing_schema
from .router import Router, _json_proposal, _repair_messages
from .style import STYLE_PROMPT, STYLE_PROMPT_SHA256, STYLE_PROMPT_VERSION, StyleEvidence, style_output_schema
from .transport import RuntimeFailure
from .validation import RoutingResult, _decision, anchor_unique_quotes, validate_interpretation


class CombinedProposal(Contract):
    SCHEMA_VERSION = 'bintanong-routing-style-v1'
    interpretation: Interpretation
    style: StyleEvidence


PROMPT_VERSION = 'bintanong-routing-style-p09-v1'
SYSTEM = '''Perform two separately validated tasks in ONE JSON packet.
The outer schema_version is bintanong-routing-style-v1. Fill interpretation and
style as separate objects. Never answer the student or execute a tool here.
The following routing instructions apply ONLY inside interpretation. Their
schema_version refers to interpretation.schema_version, not the outer packet.
BEGIN INTERPRETATION INSTRUCTIONS
'''+SYSTEM_PROMPT+'''
END INTERPRETATION INSTRUCTIONS
The following response-style instructions apply ONLY to the outer style object.
Use original_text from the same data payload, not English catalog/context labels.
Their instruction not to decide a route applies to style only; interpretation
still selects the requested route/control independently. Do not copy a route's
language label as a substitute for quoting actual conversational evidence.
BEGIN STYLE INSTRUCTIONS
'''+STYLE_PROMPT+'''
END STYLE INSTRUCTIONS
Return only the combined packet matching the final schema below.'''
PROMPT_SHA256 = hashlib.sha256(SYSTEM.encode()).hexdigest()


def output_schema():
    schema=CombinedProposal.model_json_schema()
    schema['properties']['schema_version']['const']=CombinedProposal.SCHEMA_VERSION
    interpretation=routing_schema()
    # Existing local refs resolve at this packet's root, not a nested $defs root.
    schema['$defs'].update(interpretation.pop('$defs',{}))
    schema['$defs']['Interpretation']=interpretation
    schema['$defs']['StyleEvidence']=style_output_schema()['$defs']['StyleEvidence']
    return schema


def build_messages(text,context,catalog,registry):
    data=routing_messages(text,context,catalog,registry)[1]
    return [dict(role='system',content=SYSTEM+'\nJSON schema:\n'+canonical(
        compact_for_prompt(output_schema()))),data]


class CombinedRouter(Router):
    """Same dispatch guards; one shared format repair, no separate-style call."""
    @staticmethod
    def evaluation_identity():
        return dict(routing_profile='combined',prompt_version=PROMPT_VERSION,
            prompt_sha256=PROMPT_SHA256,schema_sha256=digest(output_schema()),
            style_prompt_version=STYLE_PROMPT_VERSION,style_prompt_sha256=STYLE_PROMPT_SHA256,
            style_schema_sha256=digest(style_output_schema()))

    async def route(self,text,context):
        normalized=prepare_query(text)
        context=RequestContext.parse(context.model_dump(mode='json'))
        messages=build_messages(text,context,self.catalog,self.registry)
        proposed=None

        def failure(code,attempts):
            query=NormalizedQuery(schema_version=NormalizedQuery.SCHEMA_VERSION,
                original_text=text,normalized_text=normalized,language_hints=(),intent=None,
                entities=(),ambiguities=(),negations=(),time_qualifiers=(),
                session_fact_refs=tuple(f.fact_id for f in context.facts))
            return RoutingResult(query,_decision(control='evidence_unavailable',reason=code),
                proposed,(),'unknown',code,attempts)

        for attempt in (1,2):
            try:
                raw=await self.transport.infer(messages,output_schema())
            except RuntimeFailure as error:
                return failure(str(error),attempt)
            try:
                data=_json_proposal(raw)
                corrections=0
                if isinstance(data,dict) and 'interpretation' in data:
                    data['interpretation'],corrections=anchor_unique_quotes(data['interpretation'],text)
                packet=CombinedProposal.parse(data)
                proposed=packet.interpretation
            except (ValueError,ValidationError):
                if attempt==2:
                    return failure('invalid_model_output',attempt)
                messages=_repair_messages(messages,raw)
                continue
            try:
                packet.style.ground(text)
                effective=Interpretation.parse(dict(proposed.model_dump(mode='json'),
                    language=packet.style.language))
                result=validate_interpretation(text,context,effective,catalog=self.catalog,
                    registry=self.registry,documents_available=self.documents_available,
                    synthetic=self.synthetic)
                return replace(result,proposed=proposed,attempts=attempt,style_attempts=0,
                    style_evidence=packet.style,offset_corrections=corrections)
            except ValueError:
                return failure('invalid_grounding',attempt)
        raise AssertionError('unreachable')
