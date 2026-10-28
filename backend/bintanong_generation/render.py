"""Plain-text candidate previews; canonical decisions never come from generated prose."""
import json

from .course_facts_reply import course_fact_lines

_WORDS={
 'en':dict(preview='Candidate preview only. Not official university guidance.',
  answered='Based on the supplied evidence:',eligible='Supported prerequisite check: conditions satisfied.',
  ineligible='Supported prerequisite check: a documented condition is unmet.',
  unknown='Eligibility cannot be established from the available facts and rule coverage.',
  unsupported='This structured operation is not supported.',error='The structured check could not complete.',
  conditions='Conditions',missing='Missing information',dependency='Potential affected courses within the supplied bundle',
  clarification_needed='Please clarify the missing information before a conclusion can be given.',
  source_conflict='The supplied evidence conflicts; no conclusion is available.',
  insufficient_evidence="This information is not in Bintanong's reviewed sources yet. Please ask the relevant university office.",
  out_of_scope='Bintanong covers undergraduate academic affairs; this request is outside that scope.',
  temporarily_unavailable='The check is temporarily unavailable. Please try again later.',
  greeting='Hello. I can help with supported undergraduate academic-affairs questions.',
  thanks="You're welcome! Ask me anytime about undergraduate academic affairs.",
  abstained='A supported explanation could not be verified from the supplied evidence.'),
 'fil':dict(preview='Preview ng kandidato lamang. Hindi opisyal na gabay ng unibersidad.',
  answered='Batay sa ibinigay na ebidensya:',eligible='Ayon sa prerequisite check: kumpleto ang mga kondisyon.',
  ineligible='Ayon sa prerequisite check: may kondisyon na kulang pa.',
  unknown='Hindi pa masabi kung pwede ka, dahil kulang ang impormasyon o hindi ito sakop ng rules.',
  unsupported='Hindi supported ang check na ito.',error='Hindi natapos ang check.',
  conditions='Mga kondisyon',missing='Kulang na impormasyon',dependency='Posibleng maapektuhang kurso sa ibinigay na bundle',
  clarification_needed='Pakilinaw ang kulang na impormasyon bago makapagbigay ng pasya.',
  source_conflict='Magkasalungat ang ibinigay na ebidensya; walang maibibigay na pasya.',
  insufficient_evidence='Wala pa ito sa mga na-review na source ng Bintanong. Pakitanong sa tamang opisina ng unibersidad.',
  out_of_scope='Saklaw ng Bintanong ang undergraduate academic affairs; nasa labas nito ang tanong.',
  temporarily_unavailable='Hindi muna magawa ang check ngayon. Subukan ulit mamaya.',
  greeting='Kumusta. Makakatulong ako sa mga suportadong tanong tungkol sa undergraduate academic affairs.',
  thanks='Walang anuman! Magtanong ka lang tungkol sa undergraduate academic affairs.',
  abstained='Hindi makumpirma ang sagot mula sa ibinigay na ebidensya.'),
 'taglish':dict(preview='Candidate preview lang. Hindi official university guidance.',
  answered='Based sa supplied evidence:',eligible='Sa supported prerequisite check, satisfied ang conditions.',
  ineligible='Sa supported prerequisite check, may documented condition na hindi met.',
  unknown='Hindi pa ma-establish ang eligibility gamit ang available facts at rule coverage.',
  unsupported='Hindi supported ang structured operation na ito.',error='Hindi nakumpleto ang structured check.',
  conditions='Conditions',missing='Missing information',dependency='Potential affected courses sa supplied bundle',
  clarification_needed='Paki-clarify muna ang missing information bago magbigay ng conclusion.',
  source_conflict='May conflict sa supplied evidence; wala pang supported conclusion.',
  insufficient_evidence='Wala pa ito sa reviewed sources ng Bintanong. Paki-ask sa tamang university office.',
  out_of_scope='Undergraduate academic affairs ang scope ng Bintanong; outside scope ang request.',
  temporarily_unavailable='Temporarily unavailable ang check. Paki-try ulit later.',
  greeting='Hello. Pwede akong tumulong sa supported undergraduate academic-affairs questions.',
  thanks='Walang anuman! Ask ka lang anytime tungkol sa undergraduate academic affairs.',
  abstained='Hindi na-verify ang supported explanation mula sa supplied evidence.')}


# Owner, 24 Oct 2026 (step 2b): with no passed/failed course stated, list the reviewed prerequisites instead of
# "eligibility cannot be established", and ask which ones were passed.
_REQUIREMENT={
 'en':dict(all_of=' and ',any_of='one of: ',co_requisite='or take it at the same time',heading='Prerequisites of',
  ask='Tell me which of these you have passed, and I can check whether you can take {course}.'),
 'fil':dict(all_of=' at ',any_of='isa sa: ',co_requisite='o kunin nang sabay',heading='Mga prerequisite ng',
  ask='Sabihin mo kung alin dito ang naipasa mo na, para ma-check ko kung pwede mo nang kunin ang {course}.'),
 'taglish':dict(all_of=' and ',any_of='one of: ',co_requisite='or i-take nang sabay',heading='Prerequisites ng',
  ask='Sabihin mo kung alin dito ang na-pass mo na, para ma-check ko kung pwede mo nang i-take ang {course}.')}


# Owner27Oct: three input languages,two reply styles;show the distinction for unsupported input.
_LANGUAGE_NOTICE=('Bintanong accepts English, Filipino and Taglish questions and replies in English or Taglish. '
    'Please ask again in one of these input languages. '
    'Pwede ang English, Filipino at Taglish questions; English o Taglish ang replies. Paki-ask ulit.')


# Owner F4 (28 Oct 2026, provisional): ask whether the student is leaving PalSU or transferring in.
_TRANSFER_DIRECTION={
 'en':'Are you leaving PalSU (transfer credentials / honorable dismissal), or transferring into PalSU '
      'from another school? The requirements differ.',
 'fil':'Aalis ka ba sa PalSU (transfer credentials / honorable dismissal), o lilipat ka sa PalSU '
       'galing sa ibang school? Magkaiba ang requirements.',
 'taglish':'Aalis ka ba sa PalSU (transfer credentials / honorable dismissal), o lilipat ka sa PalSU '
       'galing sa ibang school? Magkaiba ang requirements.'}
_COURSE_NOT_FOUND={
 'en':'I could not find that course among the reviewed courses of your curriculum. '
      'Please give the course code as printed in your prospectus.',
 'fil':'Hindi ko nakita ang kursong iyan sa mga na-review na kurso ng curriculum mo. '
       'Pakibigay ang course code na nakasulat sa prospectus mo.',
 'taglish':'Hindi ko nakita yung course na iyan sa reviewed courses ng curriculum mo. '
       'Pakibigay ang course code na naka-print sa prospectus mo.'}


def requirement_text(requirement,language,nested=False):
    words=_REQUIREMENT.get(language,_REQUIREMENT['en'])
    if requirement.kind=='course': return requirement.course_id
    if requirement.kind=='co_requisite': return f"{requirement.course_id} ({words['co_requisite']})"
    if requirement.kind not in ('all_of','any_of'): raise ValueError('requirement_not_listable')
    items=[requirement_text(item,language,nested=True) for item in requirement.items]
    text=words['all_of'].join(items) if requirement.kind=='all_of' else words['any_of']+', '.join(items)
    return f'({text})' if nested else text


def _referenced(requirement,kinds):
    own=(requirement.course_id,) if requirement.kind in kinds else ()
    return {*own,*(c for item in requirement.items for c in _referenced(item,kinds))}


def _lists_requirement(pack,status):
    """No stated fact touched the rule: every course in it is still completion-unknown and every co-requisite
    enrollment-unknown. Outcome flags alone miss a failed any-of alternative (its result drops the violation)."""
    decision=pack.decision
    if (pack.requirement is None or decision is None or status!='clarification_needed'
            or decision.outcome!='unknown' or decision.satisfied_conditions or decision.violated_conditions
            or decision.unresolved_conflicts
            or not set(pack.missing_facts)<=set(decision.missing_facts)):  # e.g. a missing program or curriculum
        return False
    return (set(decision.missing_facts)=={'completion_unknown:'+c
                for c in _referenced(pack.requirement,('course','co_requisite'))}
            and set(decision.unknown_conditions)=={'enrollment_unknown:'+c
                for c in _referenced(pack.requirement,('co_requisite',))})


def fallback_status(status):
    if status in ('unknown','clarify'): return 'clarification_needed'
    if status=='conflict': return 'source_conflict'
    if status in ('uncalibrated','no_evidence'): return 'insufficient_evidence'
    if status=='unsupported_scope': return 'out_of_scope'
    if status=='greeting': return 'greeting'
    if status=='unsupported': return 'abstained'
    return 'temporarily_unavailable'


def selected_cards(pack,claims):
    if pack.status!='ready':
        from .deadline_conflict import unresolved_deadline_context
        expected=unresolved_deadline_context(pack)
        actual=tuple(dict(text=c.text,evidence_ids=list(c.evidence_ids)) for c in claims)
        if not expected or actual!=expected:
            return ()
    ids={ref for claim in claims for ref in claim.evidence_ids}
    return tuple(c for c in pack.cards if c.evidence_id in ids or
                 (c.kind=='rule' and (pack.decision is not None or pack.dependencies is not None)))


_WITHHELD={
 'en':'I cannot verify this answer from retrieved text alone. No structured check has been verified, so I cannot give a structured conclusion.',
 'fil':'Hindi pa masagot nang sigurado gamit lang ang nakuhang text. Wala pang verified na prerequisite check, kaya wala pang desisyon.',
 'taglish':'Hindi pa ma-verify ang answer gamit ang retrieved text lang. Wala pang verified structured check, kaya wala pang structured conclusion.'}


# Evidence that does not answer the question gets the same honest referral as missing evidence (owner E1, 24 Oct;
# simple-question priority, 25 Oct 2026).
_UNCOVERED={lang:words['insufficient_evidence'] for lang,words in _WORDS.items()}


# Source-gap policy: a cited source's unresolved conflict or visible defect is always stated.
# No office is named because the source does not establish which one (22 October 2026).
_LIMIT_NOTICES={
 'en':dict(conflict='Note: the cited source gives conflicting statements on this, so it does not settle '
               'which one applies. Please confirm with the right university office.',
           defect='Note: part of the cited source is cut off or unclear, so this answer may be incomplete. '
               'Please confirm with the right university office.'),
 'fil':dict(conflict='Paalala: magkasalungat ang sinasabi ng source tungkol dito, kaya hindi malinaw kung alin '
               'ang masusunod. Pakitanong sa tamang opisina ng unibersidad.',
            defect='Paalala: may bahagi ng source na putol o hindi malinaw, kaya baka kulang ang sagot na ito. '
               'Pakitanong sa tamang opisina ng unibersidad.'),
 'taglish':dict(conflict='Note: may conflicting statements ang source dito, kaya hindi clear kung alin ang '
               'applicable. Paki-confirm sa tamang university office.',
            defect='Note: may part ng source na cut off o unclear, kaya baka incomplete ang answer na ito. '
               'Paki-confirm sa tamang university office.')}
_NOTICE_ISSUES={'conflicting_deadlines':'conflict','source_cutoff':'defect',
                'malformed_source_condition':'defect','printed_total_discrepancy':'defect'}


# Owner, 24 Oct 2026 ("Answer what's covered"): each part declared unavailable is named in the student's words.
_PART_UNAVAILABLE={
 'en':'The part about "{words}" is not in Bintanong\'s reviewed sources yet. Please ask the relevant university office.',
 'fil':'Ang tanong mo tungkol sa "{words}" ay wala pa sa mga na-review na source ng Bintanong. '
       'Pakitanong sa tamang opisina ng unibersidad.',
 'taglish':'Yung part tungkol sa "{words}" ay wala pa sa reviewed sources ng Bintanong. '
       'Paki-ask sa tamang university office.'}


_PART_SOURCE_GAP={
 'en':'The source for the part about "{words}" is incomplete or unclear, so I cannot verify that answer. '
      'Please ask the relevant university office.',
 'fil':'May kulang o hindi malinaw sa source para sa tanong mo tungkol sa "{words}", kaya hindi '
       'makumpirma ang sagot. Pakitanong sa tamang opisina ng unibersidad.',
 'taglish':'May incomplete o unclear part sa source para sa "{words}", kaya hindi ma-confirm ang answer. '
           'Paki-ask sa tamang university office.'}


def unavailable_part_lines(pack,ledger):
    if ledger is None:
        return []
    texts={p.part_id:p.text for p in pack.understanding.parts}
    lines=[]
    for entry in ledger.entries:
        if entry.status=='unavailable':
            notices=_PART_SOURCE_GAP if entry.reason=='source_gap' else _PART_UNAVAILABLE
            lines.append(notices.get(pack.language,notices['en']).format(words=texts[entry.part_id]))
    return lines


def limit_notices(cards):
    """Notice kinds for unresolved conflicts/defects recorded on the given document cards."""
    kinds=[]
    for card in cards:
        if card.kind!='document': continue
        try: limits=json.loads(card.text).get('source_limits',[])
        except (ValueError,AttributeError): continue
        for limit in limits if isinstance(limits,list) else ():
            kind=(_NOTICE_ISSUES.get(limit.get('issue'))
                  if isinstance(limit,dict) and limit.get('resolution')=='unresolved' else None)
            if kind and kind not in kinds: kinds.append(kind)
    return kinds


def render_text(pack,claims,status,*,decision_withheld=False,question_uncovered=False,ledger=None,thanked=False):
    words=_WORDS.get(pack.language,_WORDS['en'])
    message=(words['thanks'] if thanked else _UNCOVERED.get(pack.language,_UNCOVERED['en']) if question_uncovered else
        _WITHHELD.get(pack.language,_WITHHELD['en']) if decision_withheld else words[status])
    lines=[words['preview'],message]
    def shown(text):  # display printed course codes in place of internal identities
        for course,code in pack.course_labels:
            text=text.replace(course,code)
        return text
    if pack.structured_context is not None:
        context=pack.structured_context
        label={'en':'Check scope','fil':'Sakop ng check','taglish':'Check scope'}.get(pack.language,'Check scope')
        values='; '.join(f'{i.name}={i.value}' for i in context.inputs)
        editions=', '.join(context.scope.edition_ids) if context.scope else ''
        lines.append(shown(f'{label}: {context.operation}; {values}; {context.rule_bundle_version or ""}; {editions}'))
    if _lists_requirement(pack,status):
        listing=_REQUIREMENT.get(pack.language,_REQUIREMENT['en'])
        course=next(i.value for i in pack.structured_context.inputs if i.name=='course_id')
        lines[1]=shown(f"{listing['heading']} {course}: {requirement_text(pack.requirement,pack.language)}.")
        lines.append(shown(listing['ask'].format(course=course)))
        return '\n'.join(lines)
    missing=pack.missing_facts
    if status=='clarification_needed' and 'language' in missing:
        lines[1]=_LANGUAGE_NOTICE
        missing=tuple(field for field in missing if field!='language')
    if status=='clarification_needed' and 'course_id' in missing:  # owner step 2c: no reviewed course matched
        lines[1]=_COURSE_NOT_FOUND.get(pack.language,_COURSE_NOT_FOUND['en'])
        missing=tuple(field for field in missing if field!='course_id')
    if status=='clarification_needed' and 'transfer_direction' in missing:
        lines[1]=_TRANSFER_DIRECTION.get(pack.language,_TRANSFER_DIRECTION['en'])
        missing=tuple(field for field in missing if field!='transfer_direction')
    canonical_allowed=pack.status=='ready' and status=='answered'
    if pack.decision is not None and (canonical_allowed or
            (pack.status=='unknown' and pack.decision.outcome=='unknown')):
        decision=pack.decision
        lines.append(words[decision.outcome])
        conditions=(*decision.satisfied_conditions,*decision.violated_conditions,*decision.unknown_conditions)
        if conditions: lines.append(shown(words['conditions']+': '+', '.join(conditions)))
        missing=tuple(dict.fromkeys((*missing,*decision.missing_facts)))
    if pack.course_facts is not None and canonical_allowed:
        lines.extend(course_fact_lines(pack.course_facts,pack.language))
    if pack.dependencies is not None:
        if canonical_allowed:
            lines.append(shown(words['dependency']+': '+(', '.join(pack.dependencies.course_ids) or '(0)')))
        if (canonical_allowed or pack.status=='unknown') and pack.dependencies.unknown_conditions:
            lines.append(shown(words['missing']+': '+', '.join(pack.dependencies.unknown_conditions)))
    if missing and (canonical_allowed or status=='clarification_needed'):
        labels=({'program_id':'programa','curriculum_id':'bersiyon ng kurikulum'}
            if pack.language=='fil' else {'program_id':'degree program','curriculum_id':'curriculum version'})
        lines.append(shown(words['missing']+': '+', '.join(labels.get(field,field) for field in missing)))
    for claim in claims:
        lines.append(claim.text+' ['+', '.join(claim.evidence_ids)+']')
    if (status=='insufficient_evidence' and ledger is not None
            and any(e.status=='unavailable' and e.reason=='source_gap' for e in ledger.entries)):
        # A reviewed but defective source is different from information not in the corpus.
        notices=unavailable_part_lines(pack,ledger)
        if any(e.status not in ('mapped','unavailable') for e in ledger.entries):
            lines[1]=words['abstained']
            lines.extend(notices)
        else:
            lines[1:2]=notices
    if status=='answered':
        lines.extend(unavailable_part_lines(pack,ledger))
        notices=_LIMIT_NOTICES.get(pack.language,_LIMIT_NOTICES['en'])
        lines.extend(notices[kind] for kind in limit_notices(selected_cards(pack,claims)))
    for card in selected_cards(pack,claims):
        for cite in card.citations:
            locator=cite.locator.ref or '/'.join((*cite.locator.section_path,*cite.locator.cell_ids,*cite.locator.item_ids))
            lines.append(f'[{card.evidence_id}] {cite.filename or cite.version_id}, p.{cite.page}, {locator}')
    return '\n'.join(lines)
