"""Ephemeral dialogue is interpretive context, never an institutional source or academic record."""
from typing import Annotated, Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Record
from ..bintanong_routing.contracts import ConversationContext, DialogueDocument

MAX_EXCHANGES = 8
MAX_TEXT_BYTES = 32768
Text = Annotated[str, Field(max_length=8192)]
Reference = Annotated[str, Field(min_length=1, max_length=128)]


class DialogueEntity(Record):
    kind: Literal['course', 'program', 'curriculum', 'topic']
    entity_id: Reference


class UnresolvedDialogue(Record):
    originating_message_id: Reference
    requested_operation: Reference | None = None
    missing_slots: tuple[Reference, ...] = Field(default=(), max_length=32)
    candidates: tuple[DialogueEntity, ...] = Field(default=(), max_length=32)


class DialogueExchange(Record):
    message_id: Reference
    program_id: Reference | None = None
    curriculum_id: Reference | None = None
    user_text: Text
    assistant_text: Text
    answer_status: Reference
    context: ConversationContext | None = None
    documents: tuple[DialogueDocument, ...] = Field(default=(), max_length=8)
    entities: tuple[DialogueEntity, ...] = Field(default=(), max_length=32)
    source_refs: tuple[Reference, ...] = Field(default=(), max_length=32)
    text_truncated: bool = False

    @model_validator(mode='after')
    def _text_bounds(self):
        if any(len(text.encode('utf-8')) > 8192 for text in (self.user_text, self.assistant_text)):
            raise ValueError('dialogue_exchange_text_budget')
        return self


class DialogueState(Record):
    revision: int = Field(default=0, ge=0)
    exchanges: tuple[DialogueExchange, ...] = Field(default=(), max_length=MAX_EXCHANGES)
    unresolved: UnresolvedDialogue | None = None

    @model_validator(mode='after')
    def _budget(self):
        if len({e.message_id for e in self.exchanges}) != len(self.exchanges):
            raise ValueError('duplicate_dialogue_message')
        if sum(text_bytes(e) for e in self.exchanges) > MAX_TEXT_BYTES:
            raise ValueError('dialogue_text_budget')
        return self


def text_bytes(exchange):
    return len(exchange.user_text.encode('utf-8')) + len(exchange.assistant_text.encode('utf-8'))


def append_exchange(state, exchange, unresolved=None):
    # Regeneration replaces its prior exchange rather than introducing two answers as evidence.
    exchanges = tuple(e for e in state.exchanges if e.message_id != exchange.message_id) + (exchange,)
    while len(exchanges) > MAX_EXCHANGES or sum(map(text_bytes, exchanges)) > MAX_TEXT_BYTES:
        discard = next(i for i, e in enumerate(exchanges) if unresolved is None or
                       e.message_id != unresolved.originating_message_id)
        exchanges = exchanges[:discard] + exchanges[discard+1:]
    return DialogueState(revision=state.revision + 1, exchanges=exchanges, unresolved=unresolved)


def bounded_text(text):
    encoded = text.encode('utf-8')
    return encoded[:8192].decode('utf-8', errors='ignore'), len(encoded) > 8192
