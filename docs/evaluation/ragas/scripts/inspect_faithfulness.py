"""Show RAGAS faithfulness statements and verdicts for chosen rows. Usage: python inspect_faithfulness.py <pairs> <writer-context.json> <out.json> ID..."""
import asyncio, json, os, sys
os.environ['RAGAS_DO_NOT_TRACK'] = 'true'
from dotenv import dotenv_values
from langchain_openai import ChatOpenAI
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness

pairs, writer, out, ids = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
writer = json.load(open(writer, encoding='utf-8'))
rows = {r['id']: r for r in map(json.loads, open(pairs, encoding='utf-8'))}
key = dotenv_values(os.path.join(os.path.dirname(__file__), '.env'))['DEEPSEEK_API_KEY']
llm = LangchainLLMWrapper(ChatOpenAI(model='deepseek-chat', base_url='https://api.deepseek.com', api_key=key,
                                     temperature=0, timeout=180), bypass_n=True)
metric = Faithfulness(llm=llm)


async def one(rid):
    r = rows[rid]
    row = {'user_input': r['question'], 'response': r['candidate_answer'],
           'retrieved_contexts': [c['text'] for c in writer[f"{r['language']} {r['query_no']}"]]}
    statements = (await metric._create_statements(row, None)).statements
    verdicts = await metric._create_verdicts(row, statements, None)
    return {'id': rid, 'verdicts': [v.model_dump() for v in verdicts.statements]}


async def main():
    result = await asyncio.gather(*(one(i) for i in ids))
    json.dump(result, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for r in result:
        print('==', r['id'])
        for v in r['verdicts']:
            if not v['verdict']:
                print(' X', v['statement'][:160], '|', v['reason'][:160])
asyncio.run(main())
