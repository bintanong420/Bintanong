from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from evaluation.practice_exam import main, render_exam
from tests.test_practice_exam import packet, citation


class PracticeExamCliTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.exam=packet(self.root)
        self.input=self.root/'exam.json'
        self.input.write_text(json.dumps(self.exam),encoding='utf-8')

    def test_questions_and_key_keep_answers_separate_and_source_exact(self):
        questions,key=render_exam(self.exam)
        self.assertIn(self.exam['cases'][0]['question'],questions)
        self.assertNotIn('FICTION1.',questions)
        self.assertIn('FICTION1.',key)
        self.assertIn('ver-fiction',key)
        self.assertIn(self.exam['sources'][0]['byte_sha256'],key)
        self.assertIn('physical page 1',key)
        self.assertIn('printed page 1',key)
        self.assertIn('pdf:p1:row:FICTION2:prerequisite',key)

    def test_cli_validates_and_exports_an_ungraded_exam_without_observations(self):
        out=self.root/'output'
        with redirect_stdout(io.StringIO()):
            code=main(['--exam',str(self.input),'--source-root',str(self.root),'--output-dir',str(out)])
        self.assertEqual(code,0)
        self.assertTrue((out/'questions.md').is_file())
        self.assertTrue((out/'answer-key.md').is_file())
        report=json.loads((out/'validation.json').read_text(encoding='utf-8'))
        self.assertEqual(report['case_count'],1)
        self.assertEqual(report['actual_retrieval_run'],'not_performed_by_validation')
        self.assertFalse((out/'grading.json').exists())

    def test_cli_grades_only_supplied_observations(self):
        case=self.exam['cases'][0]
        observed={case['case_id']:dict(answer=case['expected_answer'],status='answerable',
                                      citations=[citation(case['gold_evidence'][0])])}
        observation_file=self.root/'observed.json'
        observation_file.write_text(json.dumps(observed),encoding='utf-8')
        out=self.root/'graded'
        with redirect_stdout(io.StringIO()):
            code=main(['--exam',str(self.input),'--source-root',str(self.root),'--output-dir',str(out),
                       '--observations',str(observation_file)])
        self.assertEqual(code,0)
        grade=json.loads((out/'grading.json').read_text(encoding='utf-8'))
        self.assertEqual(grade['passed'],1)
        self.assertFalse(grade['institutional_gate_eligible'])

    def test_cli_refuses_writing_gold_output_inside_repository(self):
        repository=Path(__file__).resolve().parents[1]
        with self.assertRaisesRegex(ValueError,'outside'):
            main(['--exam',str(self.input),'--source-root',str(self.root),
                  '--output-dir',str(repository/'evaluation'/'unapproved-gold')])
        self.assertFalse((repository/'evaluation'/'unapproved-gold').exists())

    def test_cli_will_not_overwrite_an_exam_input(self):
        protected=self.root/'questions.md'
        original=json.dumps(self.exam)
        protected.write_text(original,encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'overwrite'):
            main(['--exam',str(protected),'--source-root',str(self.root),'--output-dir',str(self.root)])
        self.assertEqual(protected.read_text(encoding='utf-8'),original)

    def test_cli_refuses_gold_output_in_another_git_worktree(self):
        another=self.root/'another-worktree'
        another.mkdir()
        (another/'.git').write_text('gitdir: elsewhere',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'outside'):
            main(['--exam',str(self.input),'--source-root',str(self.root),
                  '--output-dir',str(another/'gold')])
        self.assertFalse((another/'gold').exists())

    def test_ungraded_export_cannot_reuse_a_stale_grading_file(self):
        out=self.root/'stale'
        out.mkdir()
        (out/'grading.json').write_text('{"passed":999}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'grading'):
            main(['--exam',str(self.input),'--source-root',str(self.root),'--output-dir',str(out)])
        self.assertFalse((out/'validation.json').exists())

    def test_output_hardlink_cannot_overwrite_original_source(self):
        out=self.root/'linked-source-output'
        out.mkdir()
        original=(self.root/'fixture.pdf').read_bytes()
        (out/'questions.md').hardlink_to(self.root/'fixture.pdf')
        with self.assertRaisesRegex(ValueError,'linked'):
            main(['--exam',str(self.input),'--source-root',str(self.root),'--output-dir',str(out)])
        self.assertEqual((self.root/'fixture.pdf').read_bytes(),original)
        self.assertFalse((out/'validation.json').exists())

    def test_output_hardlink_cannot_write_gold_into_another_git_root(self):
        out=self.root/'linked-git-output'
        out.mkdir()
        other=self.root/'separate-repository'
        other.mkdir()
        (other/'.git').mkdir()
        protected=other/'protected.md'
        protected.write_text('preserve owner content',encoding='utf-8')
        (out/'answer-key.md').hardlink_to(protected)
        with self.assertRaisesRegex(ValueError,'linked'):
            main(['--exam',str(self.input),'--source-root',str(self.root),'--output-dir',str(out)])
        self.assertEqual(protected.read_text(encoding='utf-8'),'preserve owner content')
        self.assertFalse((out/'questions.md').exists())


if __name__=='__main__':
    unittest.main()
