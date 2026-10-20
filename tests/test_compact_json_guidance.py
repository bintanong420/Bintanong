"""All real inference stages request fewer formatting tokens, keeping contracts."""
import json

import pytest

from backend.bintanong_contracts.symbolic import EMPTY_REGISTRY
from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_routing.prompt import build_messages, SYSTEM_PROMPT, output_schema
from backend.bintanong_routing.style import build_style_messages, STYLE_PROMPT, style_output_schema
from backend.bintanong_generation.prompt import (
    draft_messages, support_messages, draft_schema, DRAFT_PROMPT, SUPPORT_PROMPT,
    output_schema as generation_schema,
)
from backend.bintanong_generation.contracts import AnswerDraft, SupportReport
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_contracts.schema_display import compact_for_prompt
from test_generation_evidence import integrated


@pytest.mark.parametrize('stage', ['routing', 'style', 'draft', 'support'])
def test_real_prompt_requests_compact_json_with_complete_payload_and_schema(stage):
    question='Fictional question: "hindi pa passed"; preserve negation.'
    pack=prepare(integrated('Hybrid'))
    before=pack.model_payload()
    if stage=='routing':
        messages=build_messages(question,RequestContext(session_id='sess-a',request_id='req-a'),(),EMPTY_REGISTRY)
        instruction,schema=SYSTEM_PROMPT,output_schema()
    elif stage=='style':
        messages=build_style_messages(question)
        instruction,schema=STYLE_PROMPT,style_output_schema()
    elif stage=='draft':
        messages=draft_messages(question,pack)
        instruction,schema=DRAFT_PROMPT,draft_schema(pack)
    else:
        draft=AnswerDraft.parse(dict(schema_version=AnswerDraft.SCHEMA_VERSION,
            language='en',release_id=pack.release_id,decision_outcome=pack.decision.outcome,claims=[]))
        messages=support_messages(question,pack,draft)
        instruction,schema=SUPPORT_PROMPT,generation_schema(SupportReport)
    system=messages[0]['content']
    assert 'Return compact JSON on one line' in system
    assert 'Keep string values complete; do not omit required fields.' in system
    assert system.startswith(instruction+'\n')
    assert json.loads(system.split('schema:\n',1)[1])==compact_for_prompt(schema)
    data=json.loads(messages[1]['content'])
    assert data.get('original_text',data.get('untrusted_question'))==question
    if stage in ('draft','support'):
        assert data['evidence']==json.loads(json.dumps(before))
        assert pack.model_payload()==before
