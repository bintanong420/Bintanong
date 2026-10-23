"""Request-local wire labels; canonical provenance never leaves host validation."""
from dataclasses import dataclass
from typing import Annotated

from pydantic import Field

from .contracts import AnswerDraft, ProseClaim
from .evidence import PreparedEvidence

ShortEvidenceID=Annotated[str,Field(pattern=r'^e(?:[1-9]|[12][0-9]|3[0-2])$')]


class ShortProseClaim(ProseClaim):
    evidence_ids: tuple[ShortEvidenceID,...]=Field(min_length=1,max_length=8)


class ShortAnswerDraft(AnswerDraft):
    SCHEMA_VERSION='bintanong-answer-draft-short-v1'
    claims: tuple[ShortProseClaim,...]=Field(max_length=8)


@dataclass(frozen=True)
class EvidenceReferences:
    pack: PreparedEvidence

    @property
    def labels(self):
        return tuple(f'e{i+1}' for i in range(len(self.pack.cards)))

    def payload(self):
        value=self.pack.model_payload()
        for label,card in zip(self.labels,value['sources'],strict=True):
            card['evidence_id']=label
        return value

    def encode(self,draft: AnswerDraft):
        lookup={card.evidence_id:label for label,card in zip(self.labels,self.pack.cards,strict=True)}
        value=draft.model_dump(mode='json')
        value['schema_version']=ShortAnswerDraft.SCHEMA_VERSION
        try:
            for claim in value['claims']:
                claim['evidence_ids']=[lookup[ref] for ref in claim['evidence_ids']]
        except KeyError as exc:
            raise ValueError('unknown_evidence_reference') from exc
        return ShortAnswerDraft.parse(value).model_dump(mode='json')

    def decode(self,draft: ShortAnswerDraft):
        lookup=dict(zip(self.labels,(card.evidence_id for card in self.pack.cards),strict=True))
        value=draft.model_dump(mode='json')
        value['schema_version']=AnswerDraft.SCHEMA_VERSION
        try:
            for claim in value['claims']:
                claim['evidence_ids']=[lookup[ref] for ref in claim['evidence_ids']]
        except KeyError as exc:
            raise ValueError('unknown_evidence_reference') from exc
        return AnswerDraft.parse(value)
