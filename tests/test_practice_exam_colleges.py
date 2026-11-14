"""Invented college fixtures; no institutional answers or originals committed."""
import copy
import hashlib
from pathlib import Path
import shutil
import tempfile
import unittest

from evaluation.practice_exam import validate_exam, grade_exam, render_exam
from tests.test_practice_exam import packet, citation


def college_packet(root):
    exam = packet(root)
    exam['sources'], exam['cases'] = [], []
    template = packet(root)
    for college in ('CAD', 'CAH'):
        relative = f'Tiniguiban - Main/{college}/fiction.pdf'
        path = root/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        content = f'%PDF-1.4\nInvented {college} fixture.\n%%EOF\n'.encode()
        path.write_bytes(content)
        source = copy.deepcopy(template['sources'][0])
        source.update(source_id='src-'+college.lower(), version_id='ver-'+college.lower(),
                      relative_path=relative, college=college, byte_sha256=hashlib.sha256(content).hexdigest())
        exam['sources'].append(source)
        for number, language in enumerate(('en', 'tl', 'taglish'), 1):
            case = copy.deepcopy(template['cases'][0])
            case.update(case_id=f'dev-{college.lower()}-{number}', group_id='grp-'+college.lower(),
                        language=language, college=college)
            case['gold_evidence'][0].update(source_id=source['source_id'], version_id=source['version_id'],
                                            byte_sha256=source['byte_sha256'])
            exam['cases'].append(case)
    (root/'fixture.pdf').unlink()  # Only this fixture's owned helper file.
    exam['college_coverage'] = dict(required_colleges=['CAD', 'CAH'], cases_per_college=3,
                                   required_languages=['en', 'tl', 'taglish'])
    return exam


class PracticeExamCollegeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.exam = college_packet(self.root)

    def test_coverage_reports_every_college_with_balanced_languages(self):
        report = validate_exam(self.exam, self.root)
        self.assertEqual(set(report['by_college']), {'CAD', 'CAH'})
        self.assertEqual(report['by_college']['CAD']['case_count'], 3)
        self.assertEqual(report['by_college']['CAH']['by_language'], {'en':1, 'tl':1, 'taglish':1})
        self.assertTrue(report['college_coverage_complete'])

    def test_unrepresented_dataset_college_cannot_be_hidden_by_declaration(self):
        added = self.root/'Tiniguiban - Main'/'CTE'/'new.pdf'
        added.parent.mkdir(parents=True)
        added.write_bytes(b'%PDF-1.4\nInvented extra college.\n%%EOF\n')
        with self.assertRaisesRegex(ValueError, 'college'):
            validate_exam(self.exam, self.root)

    def test_missing_or_unbalanced_college_cases_are_rejected(self):
        for mode in ('missing', 'extra'):
            with self.subTest(mode=mode):
                bad = copy.deepcopy(self.exam)
                if mode == 'missing':
                    bad['cases'] = [c for c in bad['cases'] if c['college'] != 'CAH']
                else:
                    extra = copy.deepcopy(bad['cases'][0])
                    extra['case_id'] = 'dev-cad-extra'
                    bad['cases'].append(extra)
                with self.assertRaisesRegex(ValueError, 'college'):
                    validate_exam(bad, self.root)

    def test_case_cannot_claim_a_college_using_another_colleges_evidence(self):
        self.exam['cases'][0]['college'] = 'CAH'
        with self.assertRaisesRegex(ValueError, 'college'):
            validate_exam(self.exam, self.root)

    def test_source_college_must_match_its_dataset_directory(self):
        self.exam['sources'][0]['college'] = 'CAH'
        with self.assertRaisesRegex(ValueError, 'college'):
            validate_exam(self.exam, self.root)

    def test_each_college_must_include_the_declared_languages(self):
        self.exam['cases'][2]['language'] = 'en'
        with self.assertRaisesRegex(ValueError, 'language'):
            validate_exam(self.exam, self.root)

    def test_relative_source_paths_survive_a_dataset_root_relocation(self):
        relocated = self.root/'relocated'
        relocated.mkdir()
        for source in self.exam['sources']:
            target = relocated/source['relative_path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.root/source['relative_path'], target)
        report = validate_exam(self.exam, relocated)
        self.assertTrue(report['college_coverage_complete'])
        self.assertEqual(report['case_count'], 6)

    def test_grading_separates_college_results(self):
        observations = {c['case_id']:dict(answer=c['expected_answer'], status='answerable',
            citations=[citation(g) for g in c['gold_evidence']]) for c in self.exam['cases']}
        observations['dev-cad-1']['answer'] = 'wrong'
        report = grade_exam(self.exam, observations)
        self.assertEqual(report['by_college']['CAD']['passed'], 2)
        self.assertEqual(report['by_college']['CAH']['passed'], 3)

    def test_rendered_question_sheet_identifies_college(self):
        questions, key = render_exam(self.exam)
        self.assertIn('college: CAD', questions)
        self.assertIn('College: CAH', key)

    def test_legacy_exam_without_college_declaration_still_validates(self):
        legacy = packet(self.root)
        self.assertEqual(validate_exam(legacy, self.root)['by_college'], {})


if __name__ == '__main__':
    unittest.main()
