"""Diagnostic: re-verify the saved Factual Correctness claims (ar-fc-inspect.json) against expanded references
(expanded-reference.json), plain and fielded. Same judge and NLI prompt. Claims are not re-extracted.
Usage: .venv/Scripts/python reverify_fc.py <bertscore_pairs.jsonl> <ar-fc-inspect.json> <expanded-reference.json> <out.json>"""
import asyncio, json, os, sys
os.environ['RAGAS_DO_NOT_TRACK'] = 'true'
from dotenv import dotenv_values
from langchain_openai import ChatOpenAI
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import FactualCorrectness

pairs = {r['id']: r for r in map(json.loads, open(sys.argv[1], encoding='utf-8'))}
inspected = json.load(open(sys.argv[2], encoding='utf-8'))
expanded = json.load(open(sys.argv[3], encoding='utf-8'))
key = dotenv_values(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))['DEEPSEEK_API_KEY']
llm = LangchainLLMWrapper(ChatOpenAI(model='deepseek-chat', base_url='https://api.deepseek.com', api_key=key,
                                     temperature=0, max_retries=3, timeout=180), bypass_n=True)
factual = FactualCorrectness(llm=llm, mode='precision')
limit = asyncio.Semaphore(4)


async def one(r):
    claims = [c['claim'] for c in r['factual_correctness']['claims']]
    ref = expanded[str(pairs[r['id']]['query_no'])]
    result = {'id': r['id'], 'original': r['factual_correctness']['score']}
    async with limit:
        for kind in ('plain', 'fielded'):
            v = (await factual.verify_claims(ref[kind], claims, None)).tolist()
            result[kind] = sum(v) / len(v)
            result[kind + '_verdicts'] = v
    print(f"{r['id']}: original {result['original']:.2f} expanded-plain {result['plain']:.2f} "
          f"expanded-fielded {result['fielded']:.2f}", flush=True)
    return result


async def main():
    out = await asyncio.gather(*(one(r) for r in inspected))
    json.dump(out, open(sys.argv[4], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for kind in ('original', 'plain', 'fielded'):
        print(kind, round(sum(r[kind] for r in out) / len(out), 3))

asyncio.run(main())
