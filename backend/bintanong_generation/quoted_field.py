"""Exact source quotation scope; never infer a field or step from question words."""


def quoted_field_parts(pack):
    result = {}
    for part in (pack.understanding.parts if pack.understanding else ()):
        matches = [(claim,ref,text) for subject,claim,ref,text in pack.field_quotes
                   if subject == part.subject_id and claim in part.requested_claims]
        if not matches:
            continue
        if part.evidence_need != 'document' or len(matches) != 1 or part.requested_claims != (matches[0][0],):
            raise ValueError('unsupported_answer_scope')
        _,ref,text = matches[0]
        prefix = 'Ayon sa source: ' if pack.language == 'taglish' else 'The source states: '
        result[part.part_id] = (prefix+'"'+text+'"',ref)
    return result
