import copy
import unittest

from backend.bintanong_retrieval.context import build_context


def evidence(chunk_id='a', text='Main clause', page=1, locator=None):
    return dict(chunk=dict(chunk_id=chunk_id, document_id='doc', version_id='version',
                          edition_id='edition', byte_sha256='0'*64, source_text=text,
                          text=text, section_path=['Policy'], scope=[], type_fields={}),
                version=dict(version_id='version', byte_sha256='0'*64, filename='synthetic.pdf'),
                similarity=0.9, spans=[dict(span_id=chunk_id, text=text, version_id='version',
                    byte_sha256='0'*64, page=page, locator=locator or {'kind':'section','section_path':['Policy']})],
                neighbors=[])


class ContextTests(unittest.TestCase):
    def test_overlap_deduplicated_by_location_instead_of_text_alone(self):
        a, b, c = evidence('a'), evidence('b'), evidence('c', page=2)
        out = build_context([a,b,c], 1000, len)
        self.assertEqual([x['chunk_id'] for x in out['evidence']], ['a','c'])
        self.assertEqual(out['context_tokens'], len(out['context']))
        self.assertEqual(len(out['evidence'][0]['citations']), 1)

    def test_required_neighbors_are_whole_atomic_groups(self):
        a, b = evidence('a'), evidence('b','Required exception',page=2)
        a['chunk']['type_fields']['required_neighbor_chunk_ids'] = ['b']
        missing = build_context([a], 1000, len)
        self.assertEqual(missing['evidence'], [])
        self.assertIn('missing_required_neighbor:a', missing['gaps'])
        a['neighbors'] = [b]
        complete = build_context([a], 1000, len)
        self.assertEqual([x['chunk_id'] for x in complete['evidence']], ['a','b'])
        too_small = build_context([a], len(complete['context'])-1, len)
        self.assertEqual(too_small['evidence'], [])
        self.assertIn('context_budget:a', too_small['gaps'])

    def test_shared_span_removed_without_removing_distinct_clause(self):
        a, b = evidence('a', 'Clause one'), evidence('b', 'Clause two',page=2)
        b['spans'].insert(0, copy.deepcopy(a['spans'][0]))
        out = build_context([a,b], 1000, len)
        self.assertEqual(out['context'].count('Clause one'), 1)
        self.assertIn('Clause two', out['context'])

    def test_unresolvable_citation_is_not_evidence(self):
        a = evidence()
        a['spans'][0]['page'] = None
        result = build_context([a], 1000, len)
        self.assertFalse(result['evidence'])
        self.assertIn('invalid_citation:a',result['gaps'])

    def test_textless_table_uses_table_text_and_locator(self):
        a = evidence(text='Course | Units',locator={'kind':'table_cell','cell_ids':['cell-1']})
        a['spans'][0]['text'] = ''
        a['chunk']['source_text'] = ''
        result = build_context([a], 1000, len)
        self.assertIn('Course | Units',result['context'])
        self.assertEqual(result['evidence'][0]['citations'][0]['locator']['cell_ids'],['cell-1'])


if __name__ == '__main__':
    unittest.main()
