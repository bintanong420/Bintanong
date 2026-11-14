"""Disposable actual-role tests of reviewed curriculum ledgers in a research release (23 October 2026).

Reviewed prerequisite ledgers are stored verbatim and linked to a release; runtime roles read them
only through an active research release and can never write them. Synthetic ledgers only.
"""
import json
import unittest

from tests.storage_database import sql_literal
from tests import test_storage_research_release_database as research


def ledger(curriculum='curriculum-synthetic-1', digest='c' * 64, activation=False):
    return {'schema_version': 'curriculum-authoring-ledger-v1', 'content_sha256': digest,
            'scope': {'program_id': 'program-synthetic', 'curriculum_id': curriculum},
            'activation_allowed': activation, 'synthetic': True, 'courses': []}


class CurriculumLedgerDatabaseTests(unittest.TestCase):
    # Borrow the research-release fixture without re-running its tests.
    setUp = research.ResearchReleaseDatabaseTests.setUp
    prepare, record, bind = (research.ResearchReleaseDatabaseTests.prepare, research.ResearchReleaseDatabaseTests.record,
                             research.ResearchReleaseDatabaseTests.bind)
    observed, designate, ready, runtime = (research.ResearchReleaseDatabaseTests.observed, research.ResearchReleaseDatabaseTests.designate,
                                           research.ResearchReleaseDatabaseTests.ready, research.ResearchReleaseDatabaseTests.runtime)

    def store(self, value, digest=None, curriculum=None):
        digest = digest or value['content_sha256']
        curriculum = curriculum or value['scope']['curriculum_id']
        self.db.execute(
            "insert into public.curriculum_ledgers(ledger_sha256,program_id,curriculum_id,ledger) values ("
            f"{sql_literal(digest)},'program-synthetic',{sql_literal(curriculum)},{sql_literal(json.dumps(value))}::jsonb);")

    def link(self, digest='c' * 64, curriculum='curriculum-synthetic-1'):
        self.db.execute("insert into public.release_curriculum_ledgers(release_id,curriculum_id,ledger_sha256) values "
                        f"('release-selected',{sql_literal(curriculum)},{sql_literal(digest)});")

    def test_runtime_reads_linked_ledgers_only_in_an_active_research_release(self):
        self.ready(); self.store(ledger()); self.link()
        for role in ('anon', 'authenticated'):
            self.assertEqual(self.runtime(role).select('curriculum_ledgers'), [])
        self.manager.activate_release('release-selected')
        for role in ('anon', 'authenticated'):
            rows = self.runtime(role).select('curriculum_ledgers')
            self.assertEqual([r['ledger_sha256'] for r in rows], ['c' * 64])
            self.assertEqual(rows[0]['ledger']['scope']['curriculum_id'], 'curriculum-synthetic-1')
            self.assertEqual(len(self.runtime(role).select('release_curriculum_ledgers')), 1)

    def test_unlinked_ledger_stays_hidden_from_runtime(self):
        self.ready(); self.store(ledger()); self.store(ledger('curriculum-synthetic-2', 'd' * 64)); self.link()
        self.manager.activate_release('release-selected')
        self.assertEqual([r['curriculum_id'] for r in self.runtime().select('curriculum_ledgers')], ['curriculum-synthetic-1'])

    def test_runtime_roles_cannot_write_ledgers(self):
        self.ready(); self.manager.activate_release('release-selected')
        row = (f"{sql_literal('e' * 64)},'p','curriculum-synthetic-1',"
               f"{sql_literal(json.dumps(ledger(digest='e' * 64)))}::jsonb")
        for role in ('anon', 'authenticated'):
            for verb in (f"insert into public.curriculum_ledgers(ledger_sha256,program_id,curriculum_id,ledger) values ({row})",
                         "insert into public.release_curriculum_ledgers values ('release-selected','x','" + 'e' * 64 + "')"):
                with self.assertRaisesRegex(AssertionError, 'permission denied'):
                    self.db.execute(f'begin;set local role {role};{verb};commit;')

    def test_stored_ledger_must_match_its_digest_scope_and_stay_inactive(self):
        self.ready()
        for value, digest, curriculum in ((ledger(), 'f' * 64, None), (ledger(), None, 'other-curriculum'),
                                          (ledger(activation=True), None, None)):
            with self.assertRaisesRegex(AssertionError, 'p9_ledger_binding'):
                self.store(value, digest, curriculum)

    def test_link_must_name_the_ledgers_own_curriculum(self):
        self.ready(); self.store(ledger())
        with self.assertRaisesRegex(AssertionError, 'foreign key'):
            self.link(curriculum='curriculum-synthetic-2')


if __name__ == '__main__':
    unittest.main()
