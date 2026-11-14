"""Invented practice-exam fixtures; institutional gold text stays outside Git."""
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from evaluation.practice_exam import validate_exam, grade_exam


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def packet(root):
    original=b'%PDF-1.4\nInvented source fixture only.\n%%EOF\n'
    (root/'fixture.pdf').write_bytes(original)
    digest=hashlib.sha256(original).hexdigest()
    source=dict(source_id='src-fiction',version_id='ver-fiction',relative_path='fixture.pdf',
                title='Invented curriculum',byte_sha256=digest,page_count=1,page_size=[612,936],
                authority_note='Synthetic fixture, no institutional authority')
    gold=dict(source_id='src-fiction',version_id='ver-fiction',byte_sha256=digest,
              page=1,printed_page_label='1',locator_ref='pdf:p1:row:FICTION2:prerequisite',
              bbox=[10,20,200,40],excerpt='FICTION2 | prerequisite FICTION1',
              excerpt_sha256=sha('FICTION2 | prerequisite FICTION1'),role='supporting')
    case=dict(case_id='dev-fiction-prereq',group_id='grp-fiction-prereq',split='dev',language='en',
              category='prerequisites',question='Which prerequisite is printed for fictional course FICTION2?',
              expected_status='answerable',expected_answer='FICTION1.',acceptable_answers=['FICTION1.','FICTION1'],
              scope={'program':'FICTION','edition':'fiction'},gold_evidence=[gold])
    return dict(schema_version='bintanong-practice-exam-v1',exam_id='dev-fiction-v1',split='dev',status='candidate',
                source_approval='not_claimed',review=dict(author='fixture-author',independent_reviewer=None,evidence_ref=None),
                sources=[source],cases=[case])


def citation(gold):
    return {key:gold[key] for key in ('version_id','byte_sha256','page','locator_ref')}


class PracticeExamTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.exam=packet(self.root)
        self.gold=self.exam['cases'][0]['gold_evidence'][0]
        self.good={'dev-fiction-prereq':dict(answer='FICTION1.',status='answerable',citations=[citation(self.gold)])}

    def test_candidate_packet_verifies_original_digest_without_approval(self):
        out=validate_exam(self.exam,self.root)
        self.assertEqual(out['case_count'],1)
        self.assertEqual(out['source_count'],1)
        self.assertFalse(out['institutional_gate_eligible'])
        self.assertEqual(out['status'],'candidate_sources_resolved')

    def test_source_mutation_and_path_escape_are_rejected(self):
        (self.root/'fixture.pdf').write_bytes(b'%PDF-1.4\nchanged')
        with self.assertRaisesRegex(ValueError,'digest'):
            validate_exam(self.exam,self.root)
        self.exam['sources'][0]['relative_path']='../outside.pdf'
        with self.assertRaisesRegex(ValueError,'source_root'):
            validate_exam(self.exam,self.root)

    def test_wrong_gold_version_hash_page_locator_and_excerpt_are_rejected(self):
        mutations=[('version_id','ver-wrong'),('byte_sha256','1'*64),('page',2),('page',True),
                   ('locator_ref',''),('excerpt','invented replacement'),('bbox',[0,0,700,20])]
        for key,value in mutations:
            with self.subTest(key=key,value=value):
                bad=copy.deepcopy(self.exam)
                bad['cases'][0]['gold_evidence'][0][key]=value
                with self.assertRaises(ValueError):
                    validate_exam(bad,self.root)

    def test_final_split_and_claimed_verification_do_not_become_dev_evidence(self):
        for field,value in [('split','final'),('status','verified'),('source_approval','approved')]:
            with self.subTest(field=field):
                bad=copy.deepcopy(self.exam)
                bad[field]=value
                with self.assertRaises(ValueError):
                    validate_exam(bad,self.root)
        self.exam['cases'][0]['split']='final'
        with self.assertRaises(ValueError):
            validate_exam(self.exam,self.root)

    def test_duplicate_case_ids_and_answerable_without_source_are_rejected(self):
        self.exam['cases'].append(copy.deepcopy(self.exam['cases'][0]))
        with self.assertRaises(ValueError):
            validate_exam(self.exam,self.root)
        self.exam['cases'].pop()
        self.exam['cases'][0]['gold_evidence']=[]
        with self.assertRaises(ValueError):
            validate_exam(self.exam,self.root)

    def test_matching_answer_and_correct_source_pass_separate_axes(self):
        report=grade_exam(self.exam,self.good)
        self.assertEqual(report['passed'],1)
        self.assertEqual(report['answer_accuracy'],1.0)
        self.assertEqual(report['source_accuracy'],1.0)
        self.assertFalse(report['institutional_gate_eligible'])

    def test_right_answer_with_wrong_source_fails(self):
        for field,value in [('version_id','ver-wrong'),('page',2),('locator_ref','wrong-row'),('byte_sha256','0'*64)]:
            with self.subTest(field=field):
                wrong=copy.deepcopy(self.good)
                wrong['dev-fiction-prereq']['citations'][0][field]=value
                report=grade_exam(self.exam,wrong)
                self.assertEqual(report['answer_accuracy'],1.0)
                self.assertEqual(report['source_accuracy'],0.0)
                self.assertEqual(report['passed'],0)

    def test_wrong_number_is_not_normalized_into_a_correct_answer(self):
        self.good['dev-fiction-prereq']['answer']='FICTION2.'
        report=grade_exam(self.exam,self.good)
        self.assertEqual(report['passed'],0)
        self.assertEqual(report['answer_accuracy'],0.0)

    def test_malformed_observation_citation_cannot_equal_a_valid_source(self):
        for field,value in [('page',True),('page',1.0),('locator_ref',{'row':'FICTION2'})]:
            with self.subTest(field=field):
                wrong=copy.deepcopy(self.good)
                wrong['dev-fiction-prereq']['citations'][0][field]=value
                self.assertEqual(grade_exam(self.exam,wrong)['passed'],0)

    def test_missing_answers_are_failures_not_silently_removed(self):
        report=grade_exam(self.exam,{})
        self.assertEqual(report['case_count'],1)
        self.assertEqual(report['passed'],0)
        self.assertEqual(report['cases'][0]['failure_reasons'],['missing_observation'])

    def test_unsupported_case_requires_correct_abstention_and_no_false_citation(self):
        case=self.exam['cases'][0]
        case.update(expected_status='insufficient_evidence',expected_answer='This source does not establish the rule.',
                    acceptable_answers=['This source does not establish the rule.'])
        case['gold_evidence'][0]['role']='background'
        good={case['case_id']:dict(answer=case['expected_answer'],status='insufficient_evidence',citations=[])}
        self.assertEqual(grade_exam(self.exam,good)['passed'],1)
        good[case['case_id']]['status']='answerable'
        self.assertEqual(grade_exam(self.exam,good)['passed'],0)

    def test_cross_edition_comparison_requires_both_gold_citations(self):
        other=copy.deepcopy(self.exam['sources'][0])
        other.update(source_id='src-fiction-other',version_id='ver-fiction-other',byte_sha256='2'*64,
                     relative_path='other.pdf')
        self.exam['sources'].append(other)
        second=copy.deepcopy(self.gold)
        second['source_id']='src-fiction-other'
        second['version_id']='ver-fiction-other'
        second['byte_sha256']='2'*64
        self.exam['cases'][0]['gold_evidence'].append(second)
        self.assertEqual(grade_exam(self.exam,self.good)['passed'],0)
        self.good['dev-fiction-prereq']['citations'].append(citation(second))
        self.assertEqual(grade_exam(self.exam,self.good)['passed'],1)


if __name__=='__main__':
    unittest.main()
