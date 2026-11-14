"""Show the judge's working for Answer Relevancy (generated questions, noncommittal flags, cosines) and
Factual Correctness in precision mode (answer claims, verdict against the reference).
Same judge, embeddings and metric settings as run_ragas.py. Usage:
  .venv/Scripts/python inspect_ar_fc.py <bertscore_pairs.jsonl> <out.json> [ID ...]   (no IDs = all 42)"""
import asyncio, json, os, sys
os.environ['RAGAS_DO_NOT_TRACK'] = 'true'
from dotenv import dotenv_values
from langchain_openai import ChatOpenAI
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import FactualCorrectness, ResponseRelevancy
from ragas.metrics._answer_relevance import ResponseRelevanceInput
from run_ragas import SeaLionEmbeddings

pairs, out, ids = sys.argv[1], sys.argv[2], sys.argv[3:]
rows = [json.loads(x) for x in open(pairs, encoding='utf-8') if x.strip()]
rows = [r for r in rows if not ids or r['id'] in ids]
key = dotenv_values(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))['DEEPSEEK_API_KEY']
llm = LangchainLLMWrapper(ChatOpenAI(model='deepseek-chat', base_url='https://api.deepseek.com', api_key=key,
                                     temperature=0, max_retries=3, timeout=180), bypass_n=True)
embeddings = SeaLionEmbeddings()
relevancy = ResponseRelevancy(llm=llm, embeddings=embeddings)
factual = FactualCorrectness(llm=llm, mode='precision')
limit = asyncio.Semaphore(4)


async def one(r):
    async with limit:
        generated = await relevancy.question_generation.generate_multiple(
            data=ResponseRelevanceInput(response=r['candidate_answer']), llm=llm, callbacks=None,
            n=relevancy.strictness)
        questions = [g.question for g in generated]
        cosines = relevancy.calculate_similarity(r['question'], questions).tolist()
        flags = [g.noncommittal for g in generated]
        claims = await factual.decompose_claims(r['candidate_answer'], None)
        verdicts = (await factual.verify_claims(r['reference_answer'], claims, None)).tolist()
    ar = 0.0 if all(flags) else sum(cosines) / len(cosines)
    fc = sum(verdicts) / len(verdicts) if verdicts else None
    print(f"{r['id']}: AR {ar:.2f} (noncommittal {flags}) FC {fc}", flush=True)
    return {'id': r['id'], 'question': r['question'],
            'answer_relevancy': {'score': ar, 'generated': [{'question': q, 'cosine': c, 'noncommittal': f}
                                                            for q, c, f in zip(questions, cosines, flags)]},
            'factual_correctness': {'score': fc, 'claims': [{'claim': c, 'in_reference': v}
                                                           for c, v in zip(claims, verdicts)]}}


async def main():
    result = await asyncio.gather(*(one(r) for r in rows))
    json.dump(result, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

asyncio.run(main())
