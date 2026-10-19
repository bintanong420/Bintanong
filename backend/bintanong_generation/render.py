"""Plain-text candidate previews; canonical decisions never come from generated prose."""

_WORDS={
 'en':dict(preview='Candidate preview only. Not official university guidance.',
  answered='Based on the supplied evidence:',eligible='Supported prerequisite check: conditions satisfied.',
  ineligible='Supported prerequisite check: a documented condition is unmet.',
  unknown='Eligibility cannot be established from the available facts and rule coverage.',
  unsupported='This structured operation is not supported.',error='The structured check could not complete.',
  conditions='Conditions',missing='Missing information',dependency='Potential affected courses within the supplied bundle',
  clarification_needed='Please clarify the missing information before a conclusion can be given.',
  source_conflict='The supplied evidence conflicts; no conclusion is available.',
  insufficient_evidence='The available evidence is insufficient for this answer.',
  out_of_scope='Bintanong covers undergraduate academic affairs; this request is outside that scope.',
  temporarily_unavailable='The check is temporarily unavailable. Please try again later.',
  greeting='Hello. I can help with supported undergraduate academic-affairs questions.',
  abstained='A supported explanation could not be verified from the supplied evidence.'),
 'fil':dict(preview='Preview ng kandidato lamang. Hindi opisyal na gabay ng unibersidad.',
  answered='Batay sa ibinigay na ebidensya:',eligible='Sa sinuring prerequisite: natugunan ang mga kondisyon.',
  ineligible='Sa sinuring prerequisite: may hindi natugunang nakasaad na kondisyon.',
  unknown='Hindi matiyak ang pagiging kwalipikado mula sa kasalukuyang impormasyon at saklaw ng tuntunin.',
  unsupported='Hindi suportado ang pagsusuring ito.',error='Hindi natapos ang pagsusuri.',
  conditions='Mga kondisyon',missing='Kulang na impormasyon',dependency='Posibleng maapektuhang kurso sa ibinigay na bundle',
  clarification_needed='Pakilinaw ang kulang na impormasyon bago makapagbigay ng pasya.',
  source_conflict='Magkasalungat ang ibinigay na ebidensya; walang maibibigay na pasya.',
  insufficient_evidence='Hindi sapat ang kasalukuyang ebidensya para sa sagot.',
  out_of_scope='Saklaw ng Bintanong ang undergraduate academic affairs; nasa labas nito ang tanong.',
  temporarily_unavailable='Pansamantalang hindi magawa ang pagsusuri. Subukan muli mamaya.',
  greeting='Kumusta. Makakatulong ako sa mga suportadong tanong tungkol sa undergraduate academic affairs.',
  abstained='Hindi mapatunayan ang paliwanag mula sa ibinigay na ebidensya.'),
 'taglish':dict(preview='Candidate preview lang. Hindi official university guidance.',
  answered='Based sa supplied evidence:',eligible='Sa supported prerequisite check, satisfied ang conditions.',
  ineligible='Sa supported prerequisite check, may documented condition na hindi met.',
  unknown='Hindi pa ma-establish ang eligibility gamit ang available facts at rule coverage.',
  unsupported='Hindi supported ang structured operation na ito.',error='Hindi nakumpleto ang structured check.',
  conditions='Conditions',missing='Missing information',dependency='Potential affected courses sa supplied bundle',
  clarification_needed='Paki-clarify muna ang missing information bago magbigay ng conclusion.',
  source_conflict='May conflict sa supplied evidence; wala pang supported conclusion.',
  insufficient_evidence='Hindi sapat ang available evidence para sa answer.',
  out_of_scope='Undergraduate academic affairs ang scope ng Bintanong; outside scope ang request.',
  temporarily_unavailable='Temporarily unavailable ang check. Paki-try ulit later.',
  greeting='Hello. Pwede akong tumulong sa supported undergraduate academic-affairs questions.',
  abstained='Hindi na-verify ang supported explanation mula sa supplied evidence.')}


def fallback_status(status):
    if status in ('unknown','clarify'): return 'clarification_needed'
    if status=='conflict': return 'source_conflict'
    if status in ('uncalibrated','no_evidence'): return 'insufficient_evidence'
    if status=='unsupported_scope': return 'out_of_scope'
    if status=='greeting': return 'greeting'
    if status=='unsupported': return 'abstained'
    return 'temporarily_unavailable'


def selected_cards(pack,claims):
    if pack.status!='ready': return ()
    ids={ref for claim in claims for ref in claim.evidence_ids}
    return tuple(c for c in pack.cards if c.evidence_id in ids or
                 (c.kind=='rule' and (pack.decision is not None or pack.dependencies is not None)))


def render_text(pack,claims,status):
    words=_WORDS.get(pack.language,_WORDS['en'])
    lines=[words['preview'],words[status]]
    if pack.structured_context is not None:
        context=pack.structured_context
        label={'en':'Check scope','fil':'Saklaw ng pagsusuri','taglish':'Check scope'}.get(pack.language,'Check scope')
        values='; '.join(f'{i.name}={i.value}' for i in context.inputs)
        editions=', '.join(context.scope.edition_ids) if context.scope else ''
        lines.append(f'{label}: {context.operation}; {values}; {context.rule_bundle_version or ""}; {editions}')
    missing=pack.missing_facts
    canonical_allowed=pack.status=='ready' and status=='answered'
    if pack.decision is not None and (canonical_allowed or
            (pack.status=='unknown' and pack.decision.outcome=='unknown')):
        decision=pack.decision
        lines.append(words[decision.outcome])
        conditions=(*decision.satisfied_conditions,*decision.violated_conditions,*decision.unknown_conditions)
        if conditions: lines.append(words['conditions']+': '+', '.join(conditions))
        missing=tuple(dict.fromkeys((*missing,*decision.missing_facts)))
    if pack.dependencies is not None:
        if canonical_allowed:
            lines.append(words['dependency']+': '+(', '.join(pack.dependencies.course_ids) or '(0)'))
        if (canonical_allowed or pack.status=='unknown') and pack.dependencies.unknown_conditions:
            lines.append(words['missing']+': '+', '.join(pack.dependencies.unknown_conditions))
    if missing and (canonical_allowed or status=='clarification_needed'):
        labels=({'program_id':'programa','curriculum_id':'bersiyon ng kurikulum'}
            if pack.language=='fil' else {'program_id':'degree program','curriculum_id':'curriculum version'})
        lines.append(words['missing']+': '+', '.join(labels.get(field,field) for field in missing))
    for claim in claims:
        lines.append(claim.text+' ['+', '.join(claim.evidence_ids)+']')
    for card in selected_cards(pack,claims):
        for cite in card.citations:
            locator=cite.locator.ref or '/'.join((*cite.locator.section_path,*cite.locator.cell_ids,*cite.locator.item_ids))
            lines.append(f'[{card.evidence_id}] {cite.filename or cite.version_id}, p.{cite.page}, {locator}')
    return '\n'.join(lines)
