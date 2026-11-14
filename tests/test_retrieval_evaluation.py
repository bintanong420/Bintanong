import unittest

from evaluation.retrieval import evaluate_rankings, calibrate_threshold


class RetrievalEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.cases=[dict(case_id='positive',split='dev',status='synthetic',language='en',category='grades',
                         gold_chunk_ids=['a'],expected_status='ok'),
                    dict(case_id='unsupported',split='dev',status='synthetic',language='tl',category='enrollment',
                         gold_chunk_ids=[],expected_status='insufficient_evidence')]
        self.rankings={'positive':[{'chunk_id':'a','similarity':0.9},{'chunk_id':'b','similarity':0.2}],
                       'unsupported':[{'chunk_id':'b','similarity':0.3}]}

    def test_precision_recall_and_language_category_breakdown(self):
        report=evaluate_rankings(self.cases,self.rankings,k=3,threshold=0.5)
        self.assertAlmostEqual(report['cases'][0]['precision_at_k'],1/3)
        self.assertEqual(report['cases'][0]['recall_at_k'],1.0)
        self.assertIsNone(report['cases'][1]['recall_at_k'])
        self.assertEqual(report['unsupported_detection_rate'],1.0)
        self.assertFalse(report['institutional_gate_eligible'])
        self.assertEqual(set(report['by_language']),{'en','tl'})
        self.assertEqual(set(report['by_category']),{'grades','enrollment'})

    def test_calibration_uses_only_development_cases_and_detects_unsupported(self):
        selected=calibrate_threshold(self.cases,self.rankings,3,[0.0,0.5,0.95])
        self.assertEqual(selected['threshold'],0.5)
        self.cases[0]['split']='final'
        with self.assertRaises(ValueError):
            calibrate_threshold(self.cases,self.rankings,3,[0.0,0.5])

    def test_missing_duplicate_and_invalid_rankings_are_errors(self):
        for observations in ({}, {'positive':[{'chunk_id':'a','similarity':float('nan')}],'unsupported':[]},
                             {'positive':[{'chunk_id':'a','similarity':0.9},{'chunk_id':'a','similarity':0.8}], 'unsupported':[]}):
            with self.assertRaises(ValueError):
                evaluate_rankings(self.cases,observations,k=3,threshold=0.5)
