"""Source-bound candidate development exam; gold institution text stays external.

Validation binds authored labels to original bytes and locators. It does not read
PDF text, certify authority or prove that an author's answer follows from a clause.
Grading uses a fixed answer key, not an LLM judge or a retrieval performance proxy.
"""
from collections import Counter
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata


SHA = re.compile(r'[0-9a-f]{64}')
VERSION = re.compile(r'ver-[a-z0-9-]+')
STATUSES = {'answerable', 'needs_scope', 'insufficient_evidence'}
CITATION_KEYS = ('version_id', 'byte_sha256', 'page', 'locator_ref')


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _digest(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def _structure(exam):
    _require(isinstance(exam, dict), 'exam must be an object')
    _require(exam.get('schema_version') == 'bintanong-practice-exam-v1', 'unknown exam schema')
    _require(exam.get('split') == 'dev', 'practice exam is development-only; final split refused')
    _require(exam.get('status') == 'candidate' and exam.get('source_approval') == 'not_claimed',
             'candidate exam cannot claim verification or source approval')
    _require(_text(exam.get('exam_id')), 'exam_id is required')
    review = exam.get('review', {})
    _require(isinstance(review, dict) and _text(review.get('author')), 'review author is required')
    reviewer = review.get('independent_reviewer')
    if reviewer is not None:
        _require(_text(reviewer) and reviewer.strip().casefold() != review['author'].strip().casefold(),
                 'independent reviewer cannot equal author')
        _require(_text(review.get('evidence_ref')), 'reviewer requires review evidence')
    sources, cases = exam.get('sources'), exam.get('cases')
    _require(isinstance(sources, list) and sources and isinstance(cases, list) and cases,
             'nonempty source and case lists required')
    by_id, versions = {}, set()
    for source in sources:
        _require(isinstance(source, dict), 'source must be an object')
        sid = source.get('source_id')
        _require(_text(sid) and sid not in by_id, 'unique source_id required')
        version = source.get('version_id')
        _require(isinstance(version, str) and VERSION.fullmatch(version) and version not in versions,
                 'unique ver- source version required')
        _require(_digest(source.get('byte_sha256')), 'source digest must be lowercase SHA-256')
        _require(_text(source.get('relative_path')) and _text(source.get('title')) and
                 _text(source.get('authority_note')), 'source path/title/authority note required')
        _require(type(source.get('page_count')) is int and source['page_count'] >= 1, 'source page_count invalid')
        size = source.get('page_size')
        _require(isinstance(size, list) and len(size) == 2 and all(
            type(v) in (int, float) and math.isfinite(v) and v > 0 for v in size), 'source page size invalid')
        by_id[sid] = source
        versions.add(version)
    seen = set()
    for case in cases:
        _require(isinstance(case, dict), 'case must be an object')
        cid = case.get('case_id')
        _require(_text(cid) and cid not in seen, 'unique case_id required')
        seen.add(cid)
        _require(case.get('split') == 'dev', 'all case families must stay in dev')
        _require(_text(case.get('group_id')) and case['group_id'].startswith('grp-'), 'scenario group required')
        _require(case.get('language') in ('en', 'tl', 'taglish') and _text(case.get('category')),
                 'case language/category invalid')
        _require(_text(case.get('question')) and _text(case.get('expected_answer')), 'question/answer required')
        answers = case.get('acceptable_answers')
        _require(isinstance(answers, list) and answers and all(_text(a) for a in answers)
                 and case['expected_answer'] in answers, 'answer key must be in acceptable_answers')
        _require(case.get('expected_status') in STATUSES, 'case expected control invalid')
        _require(case.get('scope') is None or isinstance(case['scope'], dict), 'case scope invalid')
        gold = case.get('gold_evidence')
        _require(isinstance(gold, list), 'gold evidence must be a list')
        for span in gold:
            _require(isinstance(span, dict) and span.get('source_id') in by_id, 'gold source must resolve')
            source = by_id[span['source_id']]
            _require(span.get('version_id') == source['version_id'] and
                     span.get('byte_sha256') == source['byte_sha256'], 'gold source identity mismatch')
            page = span.get('page')
            _require(type(page) is int and 1 <= page <= source['page_count'], 'gold physical page invalid')
            _require(_text(span.get('printed_page_label')) and _text(span.get('locator_ref')), 'gold locator required')
            bbox = span.get('bbox')
            _require(isinstance(bbox, list) and len(bbox) == 4 and all(
                type(v) in (int, float) and math.isfinite(v) for v in bbox), 'gold bbox invalid')
            _require(0 <= bbox[0] < bbox[2] <= source['page_size'][0] and
                     0 <= bbox[1] < bbox[3] <= source['page_size'][1], 'gold bbox outside page')
            excerpt = span.get('excerpt')
            _require(_text(excerpt) and _digest(span.get('excerpt_sha256')) and
                     hashlib.sha256(excerpt.encode('utf-8')).hexdigest() == span['excerpt_sha256'],
                     'gold excerpt digest mismatch')
            _require(span.get('role') in ('supporting', 'contrast', 'background'), 'gold evidence role invalid')
        if case['expected_status'] == 'answerable':
            _require(any(s['role'] == 'supporting' for s in gold), 'answerable case requires supporting evidence')
        if case['expected_status'] == 'needs_scope':
            _require(len({s['version_id'] for s in gold if s['role'] == 'contrast'}) >= 2,
                     'curriculum clarification requires contrasting source versions')
        if case['expected_status'] == 'insufficient_evidence':
            _require(all(s['role'] == 'background' for s in gold), 'unsupported case cannot claim supporting evidence')
    return by_id


def validate_exam(exam, source_root):
    """Check authored metadata plus actual source bytes; no authority promotion."""
    sources = _structure(exam)
    root = Path(source_root).resolve(strict=True)
    _require(root.is_dir(), 'source_root must be an existing directory')
    for source in sources.values():
        relative = Path(source['relative_path'])
        path = (root / relative).resolve()
        _require(not relative.is_absolute() and path.is_relative_to(root), 'source path must stay inside source_root')
        _require(path.is_file(), f"source file missing: {source['relative_path']}")
        with path.open('rb') as stream:
            _require(stream.read(5) == b'%PDF-', 'source must have a PDF header')
            stream.seek(0)
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        _require(digest == source['byte_sha256'], f"source digest mismatch: {source['source_id']}")
    return dict(schema_version='bintanong-practice-exam-validation-v1', exam_id=exam['exam_id'],
        status='candidate_sources_resolved', case_count=len(exam['cases']), source_count=len(sources),
        group_count=len({c['group_id'] for c in exam['cases']}),
        by_language=dict(Counter(c['language'] for c in exam['cases'])),
        by_category=dict(Counter(c['category'] for c in exam['cases'])),
        institutional_gate_eligible=False, original_pdf_bytes_verified=True,
        printed_content_and_answer_review='manual; independent review remains separate',
        actual_retrieval_run='not_performed_by_validation')


def _normal_answer(answer):
    return ' '.join(unicodedata.normalize('NFC', answer).casefold().split())


def _citation_key(citation):
    return tuple(citation.get(key) for key in CITATION_KEYS)


def _valid_citation(citation):
    version = citation.get('version_id')
    return (isinstance(version, str) and VERSION.fullmatch(version) is not None
            and _digest(citation.get('byte_sha256')) and type(citation.get('page')) is int
            and citation['page'] >= 1 and _text(citation.get('locator_ref')))


def grade_exam(exam, observations):
    """Compare supplied answers/control/citations with the fixed dev key.

    Source bytes must be validated separately with validate_exam. This function
    never manufactures observations or confuses answer-key replay with retrieval.
    """
    _structure(exam)
    _require(isinstance(observations, dict), 'observations must be keyed by case_id')
    known = {c['case_id'] for c in exam['cases']}
    _require(set(observations) <= known, 'observation references unknown case')
    measured = []
    for case in exam['cases']:
        observed = observations.get(case['case_id'])
        failures = []
        answer_ok = source_ok = control_ok = False
        if observed is None:
            failures = ['missing_observation']
        else:
            _require(isinstance(observed, dict) and isinstance(observed.get('answer'), str), 'observation answer invalid')
            citations = observed.get('citations')
            _require(isinstance(citations, list) and all(isinstance(c, dict) for c in citations), 'observation citations invalid')
            answer_ok = _normal_answer(observed['answer']) in {_normal_answer(a) for a in case['acceptable_answers']}
            control_ok = observed.get('status') == case['expected_status']
            required = {_citation_key(g) for g in case['gold_evidence'] if g['role'] != 'background'}
            allowed = {_citation_key(g) for g in case['gold_evidence']}
            if all(_valid_citation(c) for c in citations):
                supplied = {_citation_key(c) for c in citations}
                source_ok = required <= supplied <= allowed
            failures = [label for label, ok in (
                ('answer_key_mismatch', answer_ok), ('control_mismatch', control_ok), ('source_mismatch', source_ok)
            ) if not ok]
        measured.append(dict(case_id=case['case_id'], language=case['language'], category=case['category'],
            answer_correct=answer_ok, source_correct=source_ok, control_correct=control_ok,
            passed=not failures, failure_reasons=failures))
    def summary(rows):
        return dict(case_count=len(rows), passed=sum(r['passed'] for r in rows),
            answer_accuracy=sum(r['answer_correct'] for r in rows)/len(rows),
            source_accuracy=sum(r['source_correct'] for r in rows)/len(rows),
            control_accuracy=sum(r['control_correct'] for r in rows)/len(rows))
    return dict(schema_version='bintanong-practice-exam-grade-v1', exam_id=exam['exam_id'],
        **summary(measured), cases=measured,
        by_language={v:summary([r for r in measured if r['language'] == v]) for v in sorted({r['language'] for r in measured})},
        by_category={v:summary([r for r in measured if r['category'] == v]) for v in sorted({r['category'] for r in measured})},
        institutional_gate_eligible=False, source_byte_validation='run validate_exam separately',
        measurement='fixed-key answer/control/source agreement; not semantic model quality')


def render_exam(exam, source_root=None):
    """Produce a question-only sheet and a separate source-bound answer key."""
    sources = _structure(exam)
    preamble = [f"# Development practice exam: {exam['exam_id']}", '',
        'Candidate source-reading exercise. Independent answer/source review is pending.',
        'This development set is separate from the final benchmark and does not approve institutional policy.', '']
    questions = preamble + ['Write an answer and identify its source edition, physical page and row/column.', '']
    key = preamble + ['## Sources', '']
    for source in sources.values():
        label = source['relative_path']
        if source_root is not None:
            path = (Path(source_root)/label).resolve().as_posix()
            label = f"[{Path(label).name}](</{path}>)"
        key += [f"- **{source['source_id']}**: {source['title']}",
                f"  - Original: {label}", f"  - Version: `{source['version_id']}`",
                f"  - Original SHA-256: `{source['byte_sha256']}`",
                f"  - Authority note: {source['authority_note']}", '']
    key += ['## Answer key', '',
            'Excerpts are manual source transcriptions; table separators are added for readability.',
            'Byte/locator checks do not replace independent content review.', '']
    for number, case in enumerate(exam['cases'], 1):
        title = f"### {number}. {case['question']}"
        questions += [title, '', f"Language: {case['language']}; category: {case['category']}; case: `{case['case_id']}`.",
                      '', 'Answer:', '', 'Source:', '']
        key += [title, '', f"**Expected answer:** {case['expected_answer']}",
                f"**Expected control:** `{case['expected_status']}`; group: `{case['group_id']}`.", '']
        for gold in case['gold_evidence']:
            key += [f"- Source **{gold['source_id']}**, version `{gold['version_id']}`, "
                    f"physical page {gold['page']}, printed page {gold['printed_page_label']}; role: {gold['role']}.",
                    f"- Locator: `{gold['locator_ref']}`; bbox in PDF points (top-left origin): `{gold['bbox']}`.",
                    f"- Original SHA-256: `{gold['byte_sha256']}`.",
                    '', '> ' + gold['excerpt'].replace('\n', '\n> '), '']
        if case['expected_status'] == 'insufficient_evidence':
            key += ['Background passages bound the examined source scope; they do not establish an absent rule.', '']
    return '\n'.join(questions), '\n'.join(key)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Validate/export a source-bound development practice exam')
    parser.add_argument('--exam', required=True, type=Path)
    parser.add_argument('--source-root', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--observations', type=Path, help='Actual externally recorded answers keyed by case_id')
    args = parser.parse_args(argv)
    exam = json.loads(args.exam.read_text(encoding='utf-8'))
    validation = validate_exam(exam, args.source_root)
    output = args.output_dir.resolve()
    _require(not any((parent/'.git').exists() for parent in (output, *output.parents)),
             'gold outputs must stay outside Git repositories/worktrees')
    _require(args.observations is not None or not (output/'grading.json').exists(),
             'grading.json already exists; use a fresh directory for an ungraded export')
    protected = {args.exam.resolve()} | {
        (args.source_root/s['relative_path']).resolve() for s in exam['sources']
    }
    if args.observations:
        protected.add(args.observations.resolve())
    names = ['questions.md', 'answer-key.md', 'validation.json']
    if args.observations:
        names.append('grading.json')
    _require(not any((output/name).resolve() in protected for name in names), 'output would overwrite an input')
    for name in names:
        target = output/name
        _require(not target.is_symlink() and (not target.exists() or target.stat().st_nlink == 1),
                 'output destination is linked; use a fresh unlinked file')
        _require(not target.exists() or target.is_file(), 'output destination must be a regular file')
    grade = None
    if args.observations:
        grade = grade_exam(exam, json.loads(args.observations.read_text(encoding='utf-8')))
    questions, key = render_exam(exam, args.source_root)
    output.mkdir(parents=True, exist_ok=True)
    (output/'questions.md').write_text(questions, encoding='utf-8')
    (output/'answer-key.md').write_text(key, encoding='utf-8')
    (output/'validation.json').write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding='utf-8')
    if grade is not None:
        (output/'grading.json').write_text(json.dumps(grade, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(dict(validation=validation, grading=grade, output_dir=str(output)), ensure_ascii=False))
    return 0 if grade is None or grade['passed'] == grade['case_count'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
