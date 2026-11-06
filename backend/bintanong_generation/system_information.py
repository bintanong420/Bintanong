"""Project-owned descriptions; never institutional evidence or a student's record."""

INDEX_VERSION = '2026-11-06'

# Keep implemented features separate from the study's wider intended source coverage.
SYSTEM_INFORMATION = {
    'en': {
        'capabilities': (
            'I’m Bintanong, a web-based academic guide for Palawan State University (PalSU) undergraduates. '
            'I can look up reviewed curriculum courses, units and term placement; list prerequisites and '
            'affected courses; check prerequisite conditions using the curriculum and results you provide; '
            'and explain reviewed academic policies and procedures with sources. '
            'Term checks and study-plan or what-if guidance depend on the available reviewed rules. '
            'Curriculum checks use structured facts and Prolog; document explanations use RAG; '
            'questions needing both use Hybrid.'),
        'research_scope': (
            'Research scope: PalSU undergraduate academic affairs for the 2026–2027 study. '
            'The intended sources include curricula, the Student Handbook, Citizens’ Charter and applicable '
            'USG/CSG policies; only available reviewed material can support an answer. '
            'Graduate programs, professional Medicine and Law programs, laboratory school and '
            'faculty/staff-only procedures are outside scope. Undergraduate Nursing and Health Sciences '
            'remain in scope. Ask in English, Filipino or Taglish; replies are in English or Taglish.'),
        'limitations': (
            'Research preview; university validation is pending. I give read-only advice: I cannot officially '
            'enroll you, change grades or issue a COR. A prerequisite check is not enrollment approval. '
            'Missing facts, source gaps and conflicting policies can limit an answer. Plan guidance does '
            'not guarantee offerings, future grades or approvals. Private uploaded PDFs stay separate from '
            'institutional knowledge, and extracted details need your confirmation before use. I do not '
            'automatically learn policies from chats or acquire missing sources. Confirm important academic '
            'decisions with your adviser or the relevant university office.'),
    },
    'taglish': {
        'capabilities': (
            'Ako si Bintanong, isang web-based academic guide para sa Palawan State University (PalSU) '
            'undergraduates. Pwede akong maghanap ng reviewed curriculum courses, units at term placement; '
            'maglista ng prerequisites at affected courses; mag-check ng prerequisite conditions gamit ang '
            'curriculum at results na ibinigay mo; at magpaliwanag ng reviewed academic policies at procedures '
            'kasama ang sources. Depende sa available reviewed rules ang term checks, study-plan at what-if '
            'guidance. Structured facts at Prolog ang gamit sa curriculum checks, RAG sa document explanations, '
            'at Hybrid kapag kailangan pareho.'),
        'research_scope': (
            'Research scope: PalSU undergraduate academic affairs para sa 2026–2027 study. Kasama sa intended '
            'sources ang curricula, Student Handbook, Citizens’ Charter at applicable USG/CSG policies; '
            'available reviewed material lang ang pwedeng basehan ng sagot. Outside scope ang graduate '
            'programs, professional Medicine at Law programs, laboratory school at faculty/staff-only '
            'procedures. In scope pa rin ang undergraduate Nursing at Health Sciences. Pwede ang English, '
            'Filipino at Taglish questions; English o Taglish ang replies.'),
        'limitations': (
            'Research preview ito; pending pa ang university validation. Read-only advice lang: hindi ako '
            'pwedeng official na mag-enroll, magbago ng grades o mag-issue ng COR. Ang prerequisite check '
            'ay hindi enrollment approval. Pwedeng malimitahan ang sagot dahil sa missing facts, source gaps '
            'o conflicting policies. Walang guarantee ng course offerings, future grades o approvals ang '
            'plan guidance. Hiwalay sa institutional knowledge ang private uploaded PDFs; kailangan mong '
            'i-confirm ang extracted details bago gamitin. Hindi ako automatically natututo ng policies '
            'mula sa chats o kumukuha ng missing sources. I-confirm ang important academic decisions '
            'sa adviser mo o sa relevant university office.'),
    },
}


def system_information(language: str) -> str:
    if language not in ('en', 'fil', 'taglish'):
        raise ValueError('unsupported_system_information_language')
    entries = SYSTEM_INFORMATION['en' if language == 'en' else 'taglish']
    return '\n\n'.join((*entries.values(), f'Source: Bintanong system-information index ({INDEX_VERSION}).'))
