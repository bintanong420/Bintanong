"""A model-capitalized Filipino style quote binds back to the original text only."""
import pytest
import json

from backend.bintanong_routing.style import StyleEvidence, literal_style
from backend.bintanong_routing.contracts import DocumentTopic
from test_routing_contracts import proposal
from test_routing_router import FakeTransport, run, style_proposal


def style(fragment):
    return StyleEvidence(english_fragments=(), filipino_fragments=(fragment,),
                         preferred_response_style='taglish')


def test_initial_capitalization_of_a_filipino_conversational_quote_uses_the_exact_original_span():
    original = 'Naiwan yung card, paano ko kukunin ulit?'
    raw = style('Paano ko kukunin ulit?')
    grounded = literal_style(raw, original)
    assert grounded.filipino_fragments == ('paano ko kukunin ulit?',)
    assert grounded.preferred_response_style == raw.preferred_response_style
    grounded.ground(original)
    assert raw.filipino_fragments == ('Paano ko kukunin ulit?',)


def test_capitalized_style_quote_does_not_discard_a_valid_document_route():
    text = 'Naiwan yung fictional card, paano ko kukunin ulit?'
    topic = DocumentTopic(subject_id='fictional_card', claims=('reviewed card procedure',))
    value = proposal(text=text, mentions=[], claims=[], operations=[], route='RAG', language='taglish')
    value['parts'][0].update(subject_id=topic.subject_id, requested_claims=list(topic.claims))
    model = FakeTransport(json.dumps(value), style_outputs=[json.dumps(style_proposal(
        'taglish', english=[], filipino=['Paano ko kukunin ulit?']))])
    result = run(model, text=text, topics=(topic,))
    assert result.diagnostic == 'validated' and result.decision.route == 'RAG'
    assert result.response_style == 'taglish'
    assert result.style_evidence.filipino_fragments == ('paano ko kukunin ulit?',)


@pytest.mark.parametrize('original, fragment', [
    ('paano ko kukunin?', 'Paano ko kuhanin?'),
    ('paano ang mark na 4?', 'Paano ang mark na 5?'),
    ('paano ang CC4?', 'Paano ang CC5?'),
    ('paano? paano?', 'Paano?'),
])
def test_altered_or_ambiguous_fragments_are_not_repaired(original, fragment):
    grounded = literal_style(style(fragment), original)
    assert grounded.filipino_fragments == (fragment,)
    with pytest.raises(ValueError, match='ungrounded_response_style'):
        grounded.ground(original)
