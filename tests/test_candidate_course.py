"""Synthetic offline course identities; no institutional benchmark or approval."""
import copy
import unittest

import test_candidate_curriculum as curricula
import test_reviewed_policy_chunks as fixtures
from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle
from backend.bintanong_tools.document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks


class CandidateCourseTests(unittest.TestCase):
    def setUp(self):
        self.base = curricula.CandidateCurriculumTests()
        self.base.setUp()
        self.base.chunks = []
        self.anchors = {}
        for row in list(self.base.rows):
            f = fixtures.ReviewedPolicyChunkTests(); f.setUp()
            f.sha = row['source_sha256']; f.ev = row['fields'][0]['review_event_sha256']
            code = 'CC 5/L' if row['reading_id']=='new' else 'CC 5'
            row['fields'] = [f.field('course_code', code), f.field('prerequisites', 'CC4')]
            self.anchors[row['reading_id']] = {field['name']:[f.span(field['name'],field['reviewed_value'])]
                for field in row['fields']}
            for spans in self.anchors[row['reading_id']].values():
                for span in spans:span['version_id']=row['version_id']
            if row['reading_id'] in ('old','new'):
                other = copy.deepcopy(row); other['reading_id'] += '-practicum'
                other['applicability_evidence_ref'] = 'event:'+row['owner_cohort_guidance']['event_sha256']+'#'+other['reading_id']
                other['fields'] = [f.field('course_code','CC 50'), f.field('prerequisites','CC5')]
                self.base.rows.append(other)
                self.anchors[other['reading_id']] = {field['name']:[f.span('practicum-'+field['name'],field['reviewed_value'])]
                    for field in other['fields']}
                for spans in self.anchors[other['reading_id']].values():
                    for span in spans:span['version_id']=row['version_id']
        self.rebuild()

    def rebuild(self):
        self.bundle = build_reviewed_policy_bundle(self.base.rows,sources=self.base.sources,review_events=self.base.events)
        self.pending = build_reviewed_policy_chunks(self.bundle,sources=self.base.sources,
            review_events=self.base.events,source_versions=self.base.versions,
            field_spans=self.anchors,include_source_limits=True)
        self.base.chunks = self.pending['chunks']
        for chunk in self.base.chunks:
            identity=chunk['type_fields']['reading_id']
            if identity in self.base.expected:self.base.expected[identity]['chunk']=chunk['chunk_id']

    def prep(self):
        from backend.bintanong_tools.document_ingest.candidate_course import prepare_candidate_course_index
        return prepare_candidate_course_index(self.bundle,self.pending,sources=self.base.sources,
            review_events=self.base.events,source_versions=self.base.versions,version_assignments=self.base.assignments)

    def select(self, index=None, **options):
        from backend.bintanong_tools.document_ingest.candidate_course import select_candidate_course
        return select_candidate_course(self.prep() if index is None else index,**options)

    def test_target_filters_only_reviewed_course_field_after_curriculum_selection(self):
        for identity in ('old','new'):
            with self.subTest(identity=identity):
                result = self.select(program_id='computing',version_id=self.base.expected[identity]['version'],target_course=' cC 5 ')
                self.assertEqual(result['status'],'matched')
                self.assertEqual(result['chunk_ids'],[self.base.expected[identity]['chunk']])
                self.assertEqual(result['course_identities'][0]['reading_id'],identity)
                self.assertTrue(result['candidate_only']);self.assertFalse(result['activation_eligible'])

    def test_scope_ambiguity_precedes_target_and_never_exposes_candidates(self):
        for options in ({},{'program_id':'computing'},{'program_id':'computing','student_context':'continuing'},
                {'program_id':'computing','version_id':self.base.expected['old']['version'],'student_context':'new_incoming'}):
            with self.subTest(options=options):
                result = self.select(target_course='CC5',**options)
                self.assertEqual(result['status'],'needs_scope');self.assertEqual(result['chunk_ids'],[])

    def test_missing_target_requires_explicit_role_even_with_known_scope(self):
        result = self.select(program_id='nursing')
        self.assertEqual(result['status'],'needs_target_course');self.assertEqual(result['chunk_ids'],[])

    def test_prerequisite_unknown_punctuation_and_leading_zero_do_not_match(self):
        for code in ('CC4','CC05','CC-5','AD2','CC5 CC4'):
            with self.subTest(code=code):
                result = self.select(program_id='computing',version_id=self.base.expected['old']['version'],target_course=code)
                self.assertEqual(result['status'],'unavailable');self.assertEqual(result['chunk_ids'],[])
                self.assertEqual(result['reason'],'target_course_not_in_candidates')
        result = self.select(program_id='computing',version_id=self.base.expected['old']['version'],target_course='CC50')
        self.assertTrue(result['course_identities'][0]['reading_id'].endswith('practicum'))

    def test_full_printed_code_and_incoming_guidance_preserved(self):
        result = self.select(program_id='computing',student_context='new_incoming',target_course='CC5/L')
        identity = result['course_identities'][0]
        self.assertEqual(identity['printed_code'],'CC 5/L')
        chunk = next(c for c in self.pending['chunks'] if c['chunk_id']==identity['chunk_id'])
        field = next(f for f in chunk['type_fields']['field_associations'] if f['name']=='course_code')
        self.assertEqual(identity['field'],field)
        self.assertEqual(identity['spans'],[chunk['spans'][i] for i in field['span_indexes']])

    def test_inputs_and_returned_identity_evidence_are_independent(self):
        before = copy.deepcopy((self.bundle,self.pending,self.base.assignments))
        index = self.prep(); preserved = copy.deepcopy(index)
        result = self.select(index,program_id='nursing',target_course='CC5')
        result['course_identities'][0]['spans'][0]['text']='changed'
        result['course_identities'][0]['field']['value']='changed'
        self.assertEqual(index,preserved)
        self.assertEqual((self.bundle,self.pending,self.base.assignments),before)

    def test_altered_source_review_and_chunk_bindings_are_rejected(self):
        for change in ('source','review','span','value','id'):
            with self.subTest(change=change):
                self.setUp()
                if change=='source':self.base.sources[self.base.rows[0]['source_sha256']]=b'changed'
                elif change=='review':self.base.rows[0]['fields'][0]['decision']='pending';self.rebuild()
                elif change=='span':self.pending['chunks'][0]['spans'][0]['text']='CC99'
                elif change=='value':self.pending['chunks'][0]['type_fields']['field_associations'][0]['value']='CC99'
                else:self.pending['chunks'][0]['chunk_id']='00000000-0000-0000-0000-000000000000'
                with self.assertRaises(ValueError):self.prep()

    def test_missing_blank_or_duplicate_identity_field_is_rejected(self):
        for change in ('missing','blank','duplicate'):
            with self.subTest(change=change):
                self.setUp()
                if change=='missing':self.base.rows[0]['fields'][0]['name']='other';self.anchors['old']['other']=self.anchors['old'].pop('course_code')
                elif change=='blank':
                    self.base.rows[0]['fields'][0].update(original_value='',reviewed_value='',source_blank=True)
                    self.anchors['old']['course_code']=[]
                else:
                    index=self.prep();index['rows'].append(copy.deepcopy(index['rows'][0]))
                    with self.assertRaises(ValueError):self.select(index,program_id='nursing',target_course='CC5')
                    continue
                self.rebuild()
                with self.assertRaises(ValueError):self.prep()

    def test_altered_index_and_curriculum_catalogue_are_rejected(self):
        for change in ('key','catalogue','active','binding'):
            with self.subTest(change=change):
                index=self.prep()
                if change=='key':index['rows'][0]['matching_keys']=['CC99']
                elif change=='catalogue':index['curriculum_catalogue']['entries'][0]['program_id']='other'
                elif change=='active':index['activation_eligible']=True
                else:index['rows'][0]['chunk_id']='foreign'
                with self.assertRaises(ValueError):self.select(index,program_id='nursing',target_course='CC5')

    def test_invalid_target_hint_rejected(self):
        for hint in ('','   ',[],5,'x'*2049):
            with self.subTest(hint=repr(hint)):
                with self.assertRaises(ValueError):self.select(program_id='nursing',target_course=hint)

    def test_existing_curriculum_default_remains_unchanged(self):
        from backend.bintanong_tools.document_ingest.candidate_curriculum import select_candidate_curriculum
        catalogue=self.base.prep();before=copy.deepcopy(catalogue)
        expected=select_candidate_curriculum(catalogue,program_id='computing')
        index=self.prep()
        self.assertEqual(index['curriculum_catalogue'],catalogue)
        self.assertEqual(self.select(index,program_id='computing',target_course='CC5'),expected)
        self.assertEqual(catalogue,before)

    def test_retained_source_gap_and_complete_chunk_are_not_rewritten(self):
        self.base.rows[0]['gaps']=[{'gap_id':'synthetic-cutoff','issue':'source_cutoff',
            'field_names':['prerequisites'],'visible_text':'CC4','affected_claims':['Complete conditions'],
            'locator':{'physical_pages':[1],'field':'prerequisites'}}]
        self.rebuild();before=copy.deepcopy(self.pending)
        result=self.select(program_id='computing',version_id=self.base.expected['old']['version'],target_course='CC5')
        self.assertEqual(result['status'],'matched')
        self.assertEqual(self.pending,before)
        chunk=next(c for c in self.pending['chunks'] if c['chunk_id'] in result['chunk_ids'])
        self.assertEqual(chunk['type_fields']['source_limits'][0]['gap_id'],'synthetic-cutoff')

    def test_same_target_rows_are_all_retained_without_merging(self):
        other=next(r for r in self.base.rows if r['reading_id']=='old-practicum')
        other['fields'][0].update(original_value='CC5',reviewed_value='CC5')
        self.anchors['old-practicum']['course_code'][0]['text']='CC5'
        self.rebuild()
        result=self.select(program_id='computing',version_id=self.base.expected['old']['version'],target_course='CC5')
        self.assertEqual({r['reading_id'] for r in result['course_identities']},{'old','old-practicum'})
        self.assertEqual(len(result['chunk_ids']),2)

    def test_wrong_program_or_version_stays_unavailable(self):
        for options in ({'program_id':'absent'},
                {'program_id':'nursing','version_id':self.base.expected['old']['version']}):
            with self.subTest(options=options):
                result=self.select(target_course='CC5',**options)
                self.assertEqual(result['status'],'unavailable');self.assertEqual(result['chunk_ids'],[])
