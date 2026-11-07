"""Optional student display projection; only validated host witnesses supply content."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from backend.bintanong_api.presentation import student_text, _ALIASES
from backend.bintanong_api.sources import _excerpt


class PresentationRecord(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, frozen=True)


class PresentationBlock(PresentationRecord):
    type: Literal['summary', 'verdict', 'explanation', 'limitation', 'source_notice', 'details']
    text: str = Field(min_length=1, max_length=12000)
    title: str | None = Field(default=None, min_length=1, max_length=160)

    @model_validator(mode='after')
    def disclosure(self):
        if (self.type == 'details') != (self.title is not None):
            raise ValueError('details_require_title')
        return self


class PresentationPart(PresentationRecord):
    partId: Annotated[str, Field(pattern=r'^r[1-8]$')]
    label: str = Field(min_length=1, max_length=240)
    evidenceNeed: Literal['structured', 'document']
    conditional: bool = False
    state: Literal['answered', 'unknown', 'clarification_needed', 'not_checked', 'withheld', 'unavailable']
    blocks: list[PresentationBlock] = Field(min_length=1, max_length=8)
    sourceIds: list[Annotated[str, Field(pattern=r'^ev-[0-9a-f]{64}$')]] = Field(max_length=64)

    @model_validator(mode='after')
    def limits(self):
        if len(set(self.sourceIds)) != len(self.sourceIds):
            raise ValueError('duplicate_presentation_source')
        if self.state != 'answered' and self.sourceIds:
            raise ValueError('unanswered_presentation_has_sources')
        return self


class AnswerPresentationV2(PresentationRecord):
    schemaVersion: Literal['bintanong-answer-presentation-v2']
    coverageState: Literal['complete', 'partial', 'withheld']
    parts: list[PresentationPart] = Field(min_length=1, max_length=8)

    @model_validator(mode='after')
    def coverage(self):
        if len({p.partId for p in self.parts}) != len(self.parts):
            raise ValueError('duplicate_presentation_part')
        answered = sum(p.state == 'answered' for p in self.parts)
        expected = 'complete' if answered == len(self.parts) else 'partial' if answered else 'withheld'
        if self.coverageState != expected:
            raise ValueError('presentation_coverage_mismatch')
        return self


def build_answer_presentation(answer, course_labels=None) -> dict | None:
    """Fall back intact when part attribution cannot be safely represented."""
    ledger = answer.part_ledger
    if answer.status != 'answered' or answer.validation != 'validated' or ledger is None or ledger.errors:
        return None
    if getattr(answer, 'recovery', None) is not None:
        return _recovery_presentation(answer, course_labels or {})
    children = getattr(answer, 'part_answers', ())
    if children:
        parts = []
        released = {card.evidence_id for card in answer.citations}
        for child in children:
            if getattr(child.answer, 'part_answers', ()):
                return None
            view = build_answer_presentation(child.answer, course_labels)
            if view is None:
                # Host control messages keep their explicit state; they provide no supported claims.
                if child.answer.status == 'answered' or child.answer.claims or child.answer.citations:
                    return None
                state = {'clarification_needed': 'clarification_needed', 'temporarily_unavailable': 'not_checked',
                         'insufficient_evidence': 'unavailable'}.get(child.answer.status, 'withheld')
                blocks = [dict(type='limitation', text=student_text(child.answer))]
                sources = []
            else:
                state = 'answered' if view['coverageState'] == 'complete' else view['parts'][0]['state']
                if view['coverageState'] != 'complete' and len(view['parts']) != 1:
                    return None
                blocks = [block for part in view['parts'] for block in part['blocks']]
                sources = list(dict.fromkeys(source for part in view['parts'] for source in part['sourceIds']))
            if not set(sources) <= released:
                return None
            parts.append(dict(partId=child.part_id, label=f'{"Part" if answer.language in ("en", "unknown") else "Bahagi"} {child.part_id[1:]}',
                evidenceNeed=child.evidence_need, conditional=child.answer.decision is not None,
                state=state, blocks=blocks, sourceIds=sources))
        return _checked(parts)
    # One canonical result is attributable. Compound results require their own bound witnesses.
    if len(ledger.canonical_parts) > 1:
        return None
    claims = {c.claim_id: c for c in answer.claims}
    released = {c.evidence_id: c for c in answer.citations}
    english = answer.language in ('en', 'unknown')
    parts = []
    for entry in ledger.entries:
        canonical = entry.part_id in ledger.canonical_parts
        state = 'answered' if entry.status == 'mapped' else (
            'not_checked' if entry.reason in ('structured_check_not_run', 'document_check_not_run') else
            'unavailable' if entry.status == 'unavailable' else 'withheld')
        if canonical and answer.decision is not None and answer.decision.outcome == 'unknown':
            state = 'unknown'
        sources, blocks = [], []
        if canonical and entry.status == 'mapped':
            text = student_text(answer)
            for claim in answer.claims:
                text = text.replace(_ALIASES.sub('', claim.text), '')
            text = '\n'.join(line for line in text.splitlines() if line.strip()).strip()
            if not text or answer.decision is None:
                return None
            blocks = [dict(type='verdict', text=text)]
            sources = [c.evidence_id for c in answer.citations if c.kind == 'rule'] if state == 'answered' else []
        elif state == 'answered':
            for claim_id in entry.claim_ids:
                claim = claims.get(claim_id)
                if claim is None or not set(claim.evidence_ids) <= released.keys():
                    return None
                blocks.append(dict(type='explanation', text=_ALIASES.sub('', claim.text)))
                sources.extend(claim.evidence_ids)
        else:
            notice = ('The reviewed source is incomplete or unclear for this part. Ask the relevant university office to confirm.'
                      if entry.reason == 'source_gap' else
                      'This part could not be checked.' if state == 'not_checked' else
                      'Reviewed evidence does not establish this part.') if english else (
                      'Kulang o hindi malinaw ang reviewed source para sa bahaging ito. Paki-confirm sa relevant university office.'
                      if entry.reason == 'source_gap' else
                      'Hindi na-check ang bahaging ito.' if state == 'not_checked' else
                      'Hindi pa established sa reviewed evidence ang bahaging ito.')
            blocks = [dict(type='limitation', text=notice)]
        if any(_excerpt(released[source].text)[1] for source in sources):
            blocks.append(dict(type='source_notice', text=(
                'This source has recorded limitations. Open its source details before relying on the procedure.' if english else
                'May recorded limitations ang source na ito. Buksan ang source details bago sundin ang procedure.')))
        parts.append(dict(partId=entry.part_id,
            label=f'{"Part" if english else "Bahagi"} {entry.part_id[1:]}',
            evidenceNeed='structured' if canonical or entry.reason == 'structured_check_not_run' else 'document',
            conditional=canonical and answer.decision is not None,
            state=state, blocks=blocks, sourceIds=list(dict.fromkeys(sources))))
    return _checked(parts)


def _checked(parts):
    answered = sum(p['state'] == 'answered' for p in parts)
    coverage = 'complete' if answered == len(parts) else 'partial' if answered else 'withheld'
    try:
        return AnswerPresentationV2.model_validate(dict(schemaVersion='bintanong-answer-presentation-v2',
            coverageState=coverage, parts=parts)).model_dump(exclude_none=True)
    except ValidationError:
        return None


def _recovery_presentation(answer, labels):
    from backend.bintanong_generation.recovery_reply import recovery_sections

    recovery, ledger = answer.recovery, answer.part_ledger
    if (answer.dependencies is None or answer.structured_context is None or len(ledger.entries) != 1
            or len(ledger.canonical_parts) != 1 or ledger.entries[0].status != 'mapped'
            or not any(i.name == 'course_id' and i.value == recovery.failed_course_id
                       for i in answer.structured_context.inputs)):
        return None
    courses = {recovery.failed_course_id, *answer.dependencies.course_ids,
               *(c for draft in recovery.drafts for term in draft.terms
                 for c in (*term.kept, *(p.course_id for p in term.moved))),
               *(r.course_id for draft in recovery.drafts for term in draft.terms
                 for r in term.verdict.reasons if r.course_id)}
    if not courses <= labels.keys():
        return None
    english = answer.language in ('en', 'unknown')
    quotes = []
    sections = recovery_sections(recovery, answer.language, labels.__getitem__, answer.dependencies,
                                 compact=True, cited_clauses=quotes)
    quoted_sources_available = bool(quotes) and all(any(
        card.kind == 'document' and quote in _excerpt(card.text)[0]
        and any(c.page == page for c in card.citations) for card in answer.citations) for page, quote in quotes)
    visible, alternatives, options, sources = [], [], [], []
    primary_shown = False
    for kind, lines in sections:
        if kind == 'options':
            options.extend(lines)
        elif kind == 'sources':
            if not quoted_sources_available:
                sources.extend(lines)
        elif kind == 'order' or kind == 'draft' and primary_shown:
            alternatives.extend(lines)
        else:
            visible.extend(lines)
        primary_shown |= kind == 'draft'
    blocks = [dict(type='summary', text='\n'.join(visible).strip())]
    for title, lines in (
        ('Other drafts' if english else 'Iba pang draft', alternatives),
        ('Recovery options and conditions' if english else 'Recovery options at conditions', options),
        ('Source quotations' if english else 'Mga sipi sa source', sources),
    ):
        if any(line.strip() for line in lines):
            blocks.append(dict(type='details', title=title, text='\n'.join(lines).strip()))
    return _checked([dict(partId=ledger.entries[0].part_id,
        label='Recovery draft', evidenceNeed='structured',
        conditional=True, state='answered', blocks=blocks,
        sourceIds=list(dict.fromkeys(c.evidence_id for c in answer.citations)))])
