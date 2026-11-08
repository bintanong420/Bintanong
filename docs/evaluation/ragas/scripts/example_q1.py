"""Worked example for the thesis: every RAGAS intermediate judgment for Query 1 (English, Tagalog, Taglish).
Same judge, embeddings, evidence and metric settings as the scored runs (run_ragas.py, run_faithfulness_writer.py
with fielded writer evidence). Run from the ignored audit-evidence folder (needs .env and writer-context.json):
  .venv/Scripts/python example_q1.py <bertscore_pairs.jsonl> <out.json>"""
import asyncio, json, os, sys
os.environ['RAGAS_DO_NOT_TRACK'] = 'true'
from dotenv import dotenv_values
from langchain_openai import ChatOpenAI
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (FactualCorrectness, Faithfulness, LLMContextPrecisionWithReference, LLMContextRecall,
                           ResponseRelevancy)
from ragas.metrics._answer_relevance import ResponseRelevanceInput
from ragas.metrics._context_precision import QAC
from ragas.metrics._context_recall import QCA
from run_ragas import SeaLionEmbeddings

IDS = ['Q01-en', 'Q01-tl-tagalog', 'Q01-tl-taglish']
pairs, out = sys.argv[1], sys.argv[2]
rows = {r['id']: r for r in map(json.loads, open(pairs, encoding='utf-8')) if r['id'] in IDS}
writer = json.load(open('writer-context.json', encoding='utf-8'))
key = dotenv_values('.env')['DEEPSEEK_API_KEY']
llm = LangchainLLMWrapper(ChatOpenAI(model='deepseek-chat', base_url='https://api.deepseek.com', api_key=key,
                                     temperature=0, max_retries=3, timeout=180), bypass_n=True)
faith = Faithfulness(llm=llm)
relevancy = ResponseRelevancy(llm=llm, embeddings=SeaLionEmbeddings())
precision = LLMContextPrecisionWithReference(llm=llm)
recall = LLMContextRecall(llm=llm)
factual = FactualCorrectness(llm=llm, mode='precision')


async def one(r):
    evidence = [c['fielded_text'] for c in writer[f"{r['language']} {r['query_no']}"]]
    top3 = [c['text'] for c in r['retrieved_context']]
    row = {'user_input': r['question'], 'response': r['candidate_answer'], 'retrieved_contexts': evidence}
    statements = (await faith._create_statements(row, None)).statements
    verdicts = (await faith._create_verdicts(row, statements, None)).statements
    generated = await relevancy.question_generation.generate_multiple(
        data=ResponseRelevanceInput(response=r['candidate_answer']), llm=llm, n=relevancy.strictness)
    cosines = relevancy.calculate_similarity(r['question'], [g.question for g in generated]).tolist()
    ranks = []
    for text in top3:
        v = (await precision.context_precision_prompt.generate_multiple(
            data=QAC(question=r['question'], context=text, answer=r['reference_answer']), llm=llm))[0]
        ranks.append({'context': text, 'verdict': int(v.verdict), 'reason': v.reason})
    recalled = (await recall.context_recall_prompt.generate_multiple(
        data=QCA(question=r['question'], context='\n'.join(top3), answer=r['reference_answer']), llm=llm))[0]
    claims = await factual.decompose_claims(r['candidate_answer'], None)
    supported = (await factual.verify_claims(r['reference_answer'], claims, None)).tolist()
    return {'id': r['id'], 'language': r['language'], 'question': r['question'], 'answer': r['candidate_answer'],
            'reference': r['reference_answer'], 'top3': top3, 'writer_evidence_count': len(evidence),
            'faithfulness': [v.model_dump() for v in verdicts],
            'relevancy': [{'question': g.question, 'noncommittal': g.noncommittal, 'cosine': c}
                          for g, c in zip(generated, cosines)],
            'precision': ranks,
            'recall': [c.model_dump() for c in recalled.classifications],
            'factual': [{'claim': c, 'in_reference': bool(s)} for c, s in zip(claims, supported)]}


async def main():
    result = await asyncio.gather(*(one(rows[i]) for i in IDS))
    json.dump(result, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for x in result:
        f = sum(v['verdict'] for v in x['faithfulness'])
        a = [round(g['cosine'], 3) for g in x['relevancy']]
        p = [v['verdict'] for v in x['precision']]
        c = sum(v['attributed'] for v in x['recall'])
        k = sum(v['in_reference'] for v in x['factual'])
        print(x['id'], f'F {f}/{len(x["faithfulness"])} AR {a} {[g["noncommittal"] for g in x["relevancy"]]}',
              f'CP {p} CR {c}/{len(x["recall"])} FC {k}/{len(x["factual"])}')

asyncio.run(main())
