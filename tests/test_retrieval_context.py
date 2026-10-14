import copy
import json
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


def decode_shared_context(context):
    """Independent reader for the display's source references, not its producer."""
    if not context:
        return []
    prefix, blocks = context.split('\n', 1)
    sources = json.loads(prefix)['citation_sources']
    decoded = []
    for block in blocks.split('\n\n'):
        header, text = block.split('\n', 1)
        chunk_id, encoded = header[1:-1].split(' | ', 1)
        citations = []
        for group in json.loads(encoded):
            source = sources[group['source_index']]
            for locator in group['locators']:
                citations.append({key: source[key] for key in
                    ('version_id', 'byte_sha256', 'page')} | {
                    'locator': source['locator_defaults'] | locator})
        decoded.append((chunk_id, citations, text))
    return decoded


class ContextTests(unittest.TestCase):
    def test_shared_citations_recover_full_group_below_old_display_budget(self):
        rows = [evidence('a', 'Complete condition'), evidence('b', 'Complete exception')]
        for row in rows:
            row['spans'] = [dict(row['spans'][0], span_id=row['chunk']['chunk_id']+str(i),
                text=row['chunk']['source_text']+' '+str(i), locator={
                    'kind':'text_item', 'table_index':None, 'cell_ids':[],
                    'item_ids':['synthetic:'+row['chunk']['chunk_id']+str(i)],
                    'section_path':['Undergraduate policy'], 'ref':None}) for i in range(6)]
        rows[0]['chunk']['type_fields']['required_neighbor_chunk_ids'] = ['b']
        rows[0]['neighbors'] = [rows[1]]
        before = copy.deepcopy(rows)
        old = build_context([rows[0]], 100000, len, compact_citations=True)
        budget = old['context_tokens']-1
        self.assertEqual(build_context([rows[0]], budget, len, compact_citations=True)['evidence'], [])
        shared = build_context([rows[0]], budget, len, shared_citations=True)
        self.assertEqual(shared['evidence'], old['evidence'])
        self.assertEqual(shared['gaps'], [])
        self.assertLess(shared['context_tokens'], old['context_tokens'])
        self.assertEqual(shared['context_tokens'], len(shared['context']))
        decoded = decode_shared_context(shared['context'])
        for (chunk_id, citations, text), item in zip(decoded, old['evidence']):
            self.assertEqual(chunk_id, item['chunk_id'])
            self.assertEqual(text, item['text'])
            self.assertEqual(citations, [{k:c[k] for k in
                ('version_id','byte_sha256','page','locator')} for c in item['citations']])
        self.assertEqual(len(decoded), 2)
        self.assertEqual(rows, before)
        for compact in (False, True):
            self.assertEqual(build_context([rows[0]],100000,len,compact_citations=compact),
                build_context([rows[0]],100000,len,compact_citations=compact,shared_citations=False))

    def test_shared_sources_preserve_locator_order_across_pages_and_versions(self):
        first = evidence('a', locator={'kind':'section','ref':'ñ; source','section_path':['Policy']})
        first['spans'].append(dict(first['spans'][0],span_id='a2',page=2))
        first['spans'].append(dict(first['spans'][0],span_id='a3',text='other',
            locator={'kind':'section','ref':'Different','section_path':['Policy']}))
        second = evidence('b', 'Other version', locator=copy.deepcopy(first['spans'][0]['locator']))
        second['chunk'].update(version_id='other',byte_sha256='1'*64)
        second['version'].update(version_id='other',byte_sha256='1'*64)
        second['spans'][0].update(version_id='other',byte_sha256='1'*64)
        result = build_context([first,second],100000,len,shared_citations=True)
        self.assertEqual(len(result['evidence']),2)
        decoded = decode_shared_context(result['context'])
        self.assertEqual([(c['version_id'],c['page'],c['locator']['ref'])
            for _,citations,_ in decoded for c in citations],
            [('version',1,'ñ; source'),('version',2,'ñ; source'),
             ('version',1,'Different'),('other',1,'ñ; source')])

    def test_shared_defaults_preserve_absent_keys_and_json_distinct_values(self):
        row = evidence()
        locators = [dict(kind='text_item',item_ids=[str(i)],ref=value)
                    for i,value in enumerate((False,0,0.0,None,'',[],{}))]
        locators.append(dict(kind='text_item',item_ids=['no-ref']))
        row['spans'] = [dict(row['spans'][0],span_id=str(i),text=str(i),locator=locator)
                        for i,locator in enumerate(locators)]
        result = build_context([row],100000,len,shared_citations=True)
        decoded = decode_shared_context(result['context'])
        self.assertEqual(len(decoded),1)
        actual = [c['locator'] for c in decoded[0][1]]
        self.assertEqual(json.dumps(actual,sort_keys=True),json.dumps(locators,sort_keys=True))

    def test_shared_failed_trial_does_not_change_accepted_source_defaults(self):
        first = evidence('a', 'First condition', locator={'kind':'text_item','item_ids':['a'],'ref':'same'})
        second = evidence('b', 'Later condition '*100,locator={'kind':'text_item','item_ids':['b'],'ref':'different'})
        single = build_context([first],100000,len,shared_citations=True)
        result = build_context([first,second],single['context_tokens'],len,shared_citations=True)
        self.assertEqual(result['evidence'],single['evidence'])
        self.assertEqual(result['context'],single['context'])
        self.assertEqual(result['context_tokens'],single['context_tokens'])
        self.assertEqual(result['gaps'],['context_budget:b'])

    def test_shared_group_budget_and_missing_neighbor_still_withhold_every_part(self):
        row,neighbor = evidence('a'),evidence('b','Required condition')
        row['chunk']['type_fields']['required_neighbor_chunk_ids'] = ['b']
        row['neighbors'] = [neighbor]
        complete = build_context([row],100000,len,shared_citations=True)
        self.assertEqual([e['chunk_id'] for e in complete['evidence']],['a','b'])
        withheld = build_context([row],complete['context_tokens']-1,len,shared_citations=True)
        self.assertEqual(withheld,dict(evidence=[],context='',context_tokens=0,gaps=['context_budget:a']))
        row['neighbors'] = []
        self.assertEqual(build_context([row],100000,len,shared_citations=True)['gaps'],['missing_required_neighbor:a'])

    def test_shared_citation_flag_is_explicit_boolean(self):
        for value in ('true',1,None):
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'shared_citations'):
                build_context([evidence()],1000,len,shared_citations=value)

    def test_opt_in_compact_citations_recover_complete_evidence_under_budget(self):
        row=evidence(text='Complete clause; no condition may be removed.')
        row['spans']=[dict(row['spans'][0],span_id='span-'+str(i),text='Part '+str(i),
            locator={'kind':'text_item','item_ids':['native-range-'+str(i)]}) for i in range(12)]
        before=copy.deepcopy(row)
        legacy=build_context([row],32768,len)
        budget=len(legacy['context'])-1
        self.assertFalse(build_context([row],budget,len)['evidence'])
        compact=build_context([row],budget,len,compact_citations=True)
        self.assertEqual(compact['evidence'],legacy['evidence'])
        self.assertEqual(compact['gaps'],[])
        self.assertEqual(compact['context_tokens'],len(compact['context']))
        self.assertLess(compact['context_tokens'],legacy['context_tokens'])
        self.assertEqual(row,before)
        self.assertEqual(build_context([row],32768,len,compact_citations=False),legacy)

    def test_compact_citations_preserve_every_locator_with_its_source_and_page(self):
        import json
        row=evidence()
        row['spans']=[dict(row['spans'][0],span_id='s'+str(i),page=page,text='P'+str(i),
            locator={'kind':'text_item','item_ids':['entry-'+str(i)],'ref':'Unicode ñ; ref'})
            for i,page in enumerate((1,2,1))]
        result=build_context([row],32768,len,compact_citations=True)
        groups=json.loads(result['context'].split('\n',1)[0][1:-1].split(' | ',1)[1])
        self.assertEqual([g['page'] for g in groups],[1,2])
        self.assertEqual([g['locators'] for g in groups],
            [[row['spans'][0]['locator'],row['spans'][2]['locator']],[row['spans'][1]['locator']]])
        self.assertTrue(all(g['version_id']=='version' and g['byte_sha256']=='0'*64 for g in groups))
        self.assertEqual(len(result['evidence'][0]['citations']),3)

    def test_compact_citation_budget_still_withholds_complete_required_group(self):
        row,neighbor=evidence('a'),evidence('b','Required condition',page=2)
        row['chunk']['type_fields']['required_neighbor_chunk_ids']=['b']
        row['neighbors']=[neighbor]
        complete=build_context([row],32768,len,compact_citations=True)
        self.assertEqual([e['chunk_id'] for e in complete['evidence']],['a','b'])
        withheld=build_context([row],complete['context_tokens']-1,len,compact_citations=True)
        self.assertEqual(withheld['evidence'],[])
        self.assertEqual(withheld['gaps'],['context_budget:a'])

    def test_compact_citation_flag_is_explicit_boolean(self):
        for value in ('true',1,None):
            with self.subTest(value=value),self.assertRaises(ValueError):
                build_context([evidence()],1000,len,compact_citations=value)

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

    def test_partial_textless_table_overlap_withheld_without_false_cell_binding(self):
        a=evidence('a','ROW ONE',locator={'kind':'table_cell','cell_ids':['cell-1']})
        a['spans'][0]['text']=''
        b=evidence('b','ROW ONE\nROW TWO',locator={'kind':'table_cell','cell_ids':['cell-2']})
        b['spans'][0]['text']=''
        b['spans'].insert(0,copy.deepcopy(a['spans'][0]))
        out=build_context([a,b],2000,len)
        self.assertEqual(out['context'].count('ROW ONE'),1)
        self.assertIn('partial_table_overlap:b',out['gaps'])
        self.assertEqual([r['chunk_id'] for r in out['evidence']],['a'])


if __name__ == '__main__':
    unittest.main()
