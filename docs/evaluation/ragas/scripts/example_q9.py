"""Worked example for the thesis: all RAGAS intermediate judgments for Q09-en (fielded writer evidence)."""
import asyncio, json, os
os.environ['RAGAS_DO_NOT_TRACK'] = 'true'
import numpy as np
from dotenv import dotenv_values
from langchain_openai import ChatOpenAI
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness, ResponseRelevancy, LLMContextRecall
from ragas.metrics._answer_relevance import ResponseRelevanceInput
from run_ragas import SeaLionEmbeddings

rows = {r['id']: r for r in map(json.loads, open('C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p12/docs/evaluation/bertscore/bertscore_pairs.jsonl', encoding='utf-8'))}
writer = json.load(open('writer-context.json', encoding='utf-8'))
r = rows['Q09-en']
key = dotenv_values('.env')['DEEPSEEK_API_KEY']
llm = LangchainLLMWrapper(ChatOpenAI(model='deepseek-chat', base_url='https://api.deepseek.com', api_key=key, temperature=0, timeout=180), bypass_n=True)
emb = SeaLionEmbeddings()
row = {'user_input': r['question'], 'response': r['candidate_answer'], 'reference': r['reference_answer'],
       'retrieved_contexts': [c['fielded_text'] for c in writer['English 9']]}
top3 = [c['text'] for c in r['retrieved_context']]


async def main():
    out = {'question': r['question'], 'answer': r['candidate_answer'], 'reference': r['reference_answer'],
           'writer_evidence': row['retrieved_contexts'], 'top3': top3}
    f = Faithfulness(llm=llm)
    st = (await f._create_statements(row, None)).statements
    v = await f._create_verdicts(row, st, None)
    out['faithfulness'] = [x.model_dump() for x in v.statements]
    rr = ResponseRelevancy(llm=llm, embeddings=emb)
    gens = await rr.question_generation.generate_multiple(data=ResponseRelevanceInput(response=r['candidate_answer']), llm=llm, n=3)
    q = np.array(emb.embed_query(r['question'])); sims = []
    for g in gens:
        e = np.array(emb.embed_query(g.question)); sims.append(float(q @ e))
    out['relevancy'] = [{'question': g.question, 'noncommittal': g.noncommittal, 'cosine': s} for g, s in zip(gens, sims)]
    cr = LLMContextRecall(llm=llm)
    cls = await cr.context_recall_prompt.generate(data=cr.context_recall_prompt.input_model(question=r['question'], context='\n'.join(top3), answer=r['reference_answer']), llm=llm)
    out['recall'] = [c.model_dump() for c in cls.classifications]
    json.dump(out, open('example-q9.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sup = sum(x['verdict'] for x in out['faithfulness'])
    print('FAITH', sup, '/', len(out['faithfulness']))
    for x in out['faithfulness']: print(' ', x['verdict'], '|', x['statement'])
    print('REL', out['relevancy'])
    att = sum(c['attributed'] for c in out['recall'])
    print('RECALL', att, '/', len(out['recall']))
    for c in out['recall']: print(' ', c['attributed'], '|', c['statement'][:150])
asyncio.run(main())
