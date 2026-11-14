"""Offline candidate selection never publishes or infers a student's curriculum."""
import copy
import hashlib
import json
import unittest

import test_reviewed_policy_chunks as fixtures
from backend.bintanong_tools.document_ingest.register import mint_pending_register
from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle
from backend.bintanong_tools.document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks


class CandidateCurriculumTests(unittest.TestCase):
    def setUp(self):
        self.sources = {}; self.events = {}; self.versions = []; self.rows = []; self.chunks = []
        self.assignments = {}; self.expected = {}
        self.add('old', 'computing', 'older_coexisting')
        self.add('new', 'computing', 'newer_incoming')
        self.add('nursing', 'nursing', 'single_supplied')

    def add(self, identity, program, usage):
        f = fixtures.ReviewedPolicyChunkTests(); f.setUp()
        f.data = ('%PDF-synthetic-'+identity).encode(); f.sha = hashlib.sha256(f.data).hexdigest()
        f.sources = {f.sha:f.data}
        f.version = mint_pending_register([{'filename':identity+'.pdf','sha256':f.sha,
            'acquisition_locator':'synthetic:'+identity}],synthetic=True)[0]
        f.event = json.dumps({'source_sha256':f.sha,'owner_statement':'Synthetic fields confirmed.'}).encode()
        f.ev = hashlib.sha256(f.event).hexdigest(); f.events = {f.ev:f.event}
        f.rows = [f.row(identity)]
        f.anchors = {identity:{'instruction':[f.span(identity,'Submit the form.')]}}
        owner = json.dumps({'source_sha256':f.sha,'owner_statement':'Synthetic cohort guidance.',
            'decision_kind':'curriculum_validity_and_cohort_guidance'}).encode()
        owner_sha = hashlib.sha256(owner).hexdigest();f.events[owner_sha]=owner
        f.rows[0]['owner_cohort_guidance'] = {'event_sha256':owner_sha,
            'condition':'Synthetic conditional curriculum use.',
            'unknown_student_curriculum_requires_clarification':True,'institutional_approval_inferred':False}
        f.rows[0]['applicability_evidence_ref'] = 'event:'+owner_sha+'#'+identity
        f.rows[0]['preserved_evidence'].append({'artifact':'event:'+owner_sha,'sha256':owner_sha})
        prepared = build_reviewed_policy_bundle(f.rows,sources=f.sources,review_events=f.events)
        result = build_reviewed_policy_chunks(prepared,sources=f.sources,review_events=f.events,
            source_versions=[f.version],field_spans=f.anchors,include_source_limits=True)
        self.sources.update(f.sources);self.events.update(f.events);self.versions.append(f.version)
        self.rows.extend(f.rows);self.chunks.extend(result['chunks'])
        self.assignments[f.version.version_id] = {'program_id':program,'program_label':program.title(),
            'curriculum_label':identity,'usage':usage,'owner_event_sha256':owner_sha,
            'assignment_evidence_ref':'event:'+f.ev+'#program-version','assignment_event_sha256':f.ev}
        self.expected[identity] = {'version':f.version.version_id,'chunk':result['chunks'][0]['chunk_id']}

    def prep(self):
        from backend.bintanong_tools.document_ingest.candidate_curriculum import prepare_candidate_curriculum_catalogue
        bundle = build_reviewed_policy_bundle(self.rows,sources=self.sources,review_events=self.events)
        return prepare_candidate_curriculum_catalogue(bundle,
            {'candidate_only':True,'activation_eligible':False,'chunks':self.chunks,'withheld':[]},
            sources=self.sources,review_events=self.events,source_versions=self.versions,
            version_assignments=self.assignments)

    def select(self, catalogue=None, **options):
        from backend.bintanong_tools.document_ingest.candidate_curriculum import select_candidate_curriculum
        return select_candidate_curriculum(self.prep() if catalogue is None else catalogue,**options)

    def test_explicit_old_curriculum_keeps_old_candidates_only_and_preserves_inputs(self):
        before = copy.deepcopy((self.rows,self.chunks,self.assignments,self.events))
        result = self.select(program_id='computing',version_id=self.expected['old']['version'])
        self.assertEqual(result['status'],'matched')
        self.assertEqual(result['version_ids'],[self.expected['old']['version']])
        self.assertEqual(result['chunk_ids'],[self.expected['old']['chunk']])
        self.assertFalse(result['activation_eligible'])
        self.assertTrue(result['candidate_only'])
        self.assertEqual((self.rows,self.chunks,self.assignments,self.events),before)

    def test_unknown_program_and_coexisting_curriculum_require_scope_without_chunk_ids(self):
        for options,reason in [({},'program_required'),({'program_id':'computing'},'curriculum_required'),
            ({'program_id':'computing','student_context':'continuing'},'curriculum_required')]:
            with self.subTest(options=options):
                result = self.select(**options)
                self.assertEqual(result['status'],'needs_scope');self.assertEqual(result['reason'],reason)
                self.assertEqual(result['chunk_ids'],[]);self.assertEqual(result['version_ids'],[])
        self.assertEqual(len(self.select(program_id='computing')['available_curricula']),2)

    def test_incoming_context_selects_only_the_owner_assigned_incoming_version(self):
        result = self.select(program_id='computing',student_context='new_incoming')
        self.assertEqual(result['status'],'matched')
        self.assertEqual(result['version_ids'],[self.expected['new']['version']])
        self.assertEqual(result['chunk_ids'],[self.expected['new']['chunk']])

    def test_incoming_context_conflicting_with_explicit_old_version_needs_clarification(self):
        result = self.select(program_id='computing',version_id=self.expected['old']['version'],
            student_context='new_incoming')
        self.assertEqual(result['status'],'needs_scope')
        self.assertEqual(result['reason'],'contradictory_curriculum_context');self.assertEqual(result['chunk_ids'],[])

    def test_single_supplied_program_selects_preserved_version_for_every_context(self):
        for context in (None,'continuing','new_incoming'):
            with self.subTest(context=context):
                result = self.select(program_id='nursing',student_context=context)
                self.assertEqual(result['status'],'matched')
                self.assertEqual(result['version_ids'],[self.expected['nursing']['version']])

    def test_wrong_program_or_foreign_version_returns_unavailable_without_substitution(self):
        for options in ({'program_id':'unlisted'}, {'program_id':'nursing','version_id':self.expected['old']['version']},
            {'program_id':'computing','version_id':'ver-'+'0'*64}):
            with self.subTest(options=options):
                result = self.select(**options)
                self.assertEqual(result['status'],'unavailable');self.assertEqual(result['chunk_ids'],[])

    def test_invalid_or_guessed_context_is_rejected(self):
        for options in ({'program_id':''},{'program_id':False},{'version_id':[]},
            {'student_context':'2026'},{'student_context':'senior'},{'student_context':True}):
            with self.subTest(options=options),self.assertRaises(ValueError):self.select(**options)

    def test_catalogue_digest_and_flags_cannot_be_tampered(self):
        catalogue = self.prep()
        for change in ('program','chunk','conditions','activation','candidate'):
            with self.subTest(change=change):
                altered = copy.deepcopy(catalogue)
                if change=='program':altered['entries'][0]['program_id']='wrong'
                elif change=='chunk':altered['entries'][0]['chunk_ids'].append('0'*64)
                elif change=='conditions':altered['entries'][0]['row_conditions'][0]['condition']='all students'
                elif change=='activation':altered['activation_eligible']=True
                else:altered['candidate_only']=False
                with self.assertRaises(ValueError):self.select(altered,program_id='computing')

    def test_preparation_rejects_missing_duplicate_changed_or_unreviewed_chunks(self):
        old_chunks = copy.deepcopy(self.chunks)
        for change in ('missing','duplicate','value','hash','reading','source','reviewed'):
            with self.subTest(change=change):
                self.chunks = copy.deepcopy(old_chunks)
                if change=='missing':self.chunks.pop()
                elif change=='duplicate':self.chunks.append(copy.deepcopy(self.chunks[0]))
                elif change=='value':self.chunks[0]['type_fields']['field_associations'][0]['value']='wrong'
                elif change=='hash':self.chunks[0]['content_hash']='0'*64
                elif change=='reading':self.chunks[0]['type_fields']['reading_id']='unlisted'
                elif change=='source':self.chunks[0]['byte_sha256']='0'*64
                else:self.rows[0]['fields'][0]['decision']='pending'
                with self.assertRaises(ValueError):self.prep()
        self.chunks = old_chunks

    def test_preparation_rejects_unbound_or_mixed_owner_guidance(self):
        original = copy.deepcopy(self.rows)
        for change in ('absent','event','condition','guess','approval','binding'):
            with self.subTest(change=change):
                self.rows = copy.deepcopy(original)
                guide = self.rows[0]['owner_cohort_guidance']
                if change=='absent':self.rows[0].pop('owner_cohort_guidance')
                elif change=='event':guide['event_sha256']='0'*64
                elif change=='condition':guide['condition']=''
                elif change=='guess':guide['unknown_student_curriculum_requires_clarification']=False
                elif change=='approval':guide['institutional_approval_inferred']=True
                else:self.rows[0]['applicability_evidence_ref']='unbound'
                with self.assertRaises(ValueError):self.prep()
        self.rows = original

    def test_version_assignments_require_bound_evidence_and_coherent_program_use(self):
        original = copy.deepcopy(self.assignments)
        old,new = self.expected['old']['version'],self.expected['new']['version']
        for change in ('missing','foreign','event','reference','id','label','usage','single_mix','duplicate_incoming','labels'):
            with self.subTest(change=change):
                self.assignments = copy.deepcopy(original)
                entry = self.assignments[old]
                if change=='missing':self.assignments.pop(old)
                elif change=='foreign':self.assignments['ver-'+'0'*64]=entry
                elif change=='event':entry['assignment_event_sha256']='0'*64
                elif change=='reference':entry['assignment_evidence_ref']='unbound'
                elif change=='id':entry['program_id']='Wrong program!'
                elif change=='label':entry['curriculum_label']=''
                elif change=='usage':entry['usage']='latest_is_active'
                elif change=='single_mix':entry['usage']='single_supplied'
                elif change=='duplicate_incoming':entry['usage']='newer_incoming'
                else:self.assignments[new]['program_label']='Different Computing Label'
                with self.assertRaises(ValueError):self.prep()
        self.assignments = original

    def test_only_old_supplied_version_does_not_guess_incoming_use_if_marked_coexisting(self):
        self.chunks = self.chunks[:1];self.rows=self.rows[:1]
        self.assignments={self.expected['old']['version']:self.assignments[self.expected['old']['version']]}
        result=self.select(program_id='computing',student_context='new_incoming')
        self.assertEqual(result['status'],'needs_scope')
        self.assertEqual(result['reason'],'incoming_curriculum_not_identified')

    def test_candidate_cannot_omit_a_known_limit_from_the_reviewed_row(self):
        self.rows[0]['gaps']=[{'gap_id':'synthetic-cutoff','issue':'source_cutoff',
            'field_names':['instruction'],'visible_text':'Submit the form.',
            'affected_claims':['Complete process'],
            'locator':{'physical_pages':[1],'field':'instruction'}}]
        with self.assertRaises(ValueError):self.prep()

    def test_preparation_rejects_mutated_chunk_identity_citation_page_and_applicability_reference(self):
        original=copy.deepcopy(self.chunks)
        for change in ('identity','page','applicability','source_label','scope','token_count'):
            with self.subTest(change=change):
                self.chunks=copy.deepcopy(original)
                if change=='identity':self.chunks[0]['chunk_id']='0'*64
                elif change=='page':self.chunks[0]['spans'][0]['page']=99
                elif change=='applicability':self.chunks[0]['type_fields']['applicability_basis_ref']='unbound'
                elif change=='source_label':self.chunks[0]['source_label']='wrong.pdf'
                elif change=='scope':self.chunks[0]['scope'].append('program:wrong')
                else:self.chunks[0]['token_count']['count']=1
                with self.assertRaises(ValueError):self.prep()
        self.chunks=original


if __name__=='__main__':unittest.main()
