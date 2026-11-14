"""Faithfulness against the writer's full evidence (top-3 + required neighbours, writer-context.json).
Usage: .venv/Scripts/python run_faithfulness_writer.py <pairs.jsonl> <writer-context.json> <out dir>"""
import argparse, json, math, os, pathlib, sys
os.environ['RAGAS_DO_NOT_TRACK'] = 'true'
from dotenv import dotenv_values
from langchain_openai import ChatOpenAI
from ragas import EvaluationDataset, evaluate
from ragas.cost import get_token_usage_for_openai
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness
from ragas.run_config import RunConfig

LANG = {'en': 'English', 'tl-tagalog': 'Tagalog', 'tl-taglish': 'Taglish'}
ap = argparse.ArgumentParser(); ap.add_argument('pairs'); ap.add_argument('writer'); ap.add_argument('out')
ap.add_argument('--field', default='text', choices=['text', 'fielded_text']); a = ap.parse_args()
rows = [json.loads(x) for x in open(a.pairs, encoding='utf-8') if x.strip()]
writer = json.load(open(a.writer, encoding='utf-8'))
out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
label = lambda r: f"{r['language']} {r['query_no']}"
samples = [{'user_input': r['question'], 'response': r['candidate_answer'],
            'retrieved_contexts': [c[a.field] for c in writer[label(r)]]} for r in rows]
key = dotenv_values(pathlib.Path(__file__).with_name('.env'))['DEEPSEEK_API_KEY']
llm = LangchainLLMWrapper(ChatOpenAI(model='deepseek-chat', base_url='https://api.deepseek.com', api_key=key,
                                     temperature=0, max_retries=3, timeout=180), bypass_n=True)
result = evaluate(EvaluationDataset.from_list(samples), metrics=[Faithfulness()], llm=llm,
                  run_config=RunConfig(max_workers=4, timeout=600, max_retries=5),
                  token_usage_parser=get_token_usage_for_openai, show_progress=False)
scores = result.to_pandas()['faithfulness'].tolist()
with (out / f'faithfulness_writer_{a.field}.jsonl').open('w', encoding='utf-8', newline='\n') as f:
    for r, s in zip(rows, scores):
        f.write(json.dumps({'id': r['id'], 'language': r['language'], 'contexts': len(writer[label(r)]),
                            'faithfulness': None if math.isnan(s) else s}) + '\n')
summary = {}
for group in ('overall', 'English', 'Tagalog', 'Taglish'):
    vals = [s for r, s in zip(rows, scores) if group in ('overall', r['language']) and not math.isnan(s)]
    summary[group] = {'mean': round(sum(vals) / len(vals), 4), 'n': len(vals)}
usage = result.total_tokens()
summary['tokens'] = {'input': usage.input_tokens, 'output': usage.output_tokens}
(out / f'faithfulness_writer_{a.field}_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary))
