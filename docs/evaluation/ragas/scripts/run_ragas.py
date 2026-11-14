"""RAGAS scoring of the 42 saved Bintanong answers (judge: DeepSeek; embeddings: local SEA-LION E5).

Input: the committed BERTScore export (candidate answer, retrieved top-3 context, shared source-text reference).
Key: DEEPSEEK_API_KEY from .env next to this file (never printed).
Usage: .venv/Scripts/python run_ragas.py <bertscore_pairs.jsonl> <out dir> [--ids Q01-en,Q05-tl-taglish]
"""
import argparse
import json
import math
import pathlib
import os
import time

os.environ['RAGAS_DO_NOT_TRACK'] = 'true'  # no usage analytics leave this machine

from dotenv import dotenv_values
from langchain_openai import ChatOpenAI
from ragas import EvaluationDataset, evaluate
from ragas.cost import get_token_usage_for_openai
from ragas.embeddings import BaseRagasEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (FactualCorrectness, Faithfulness, LLMContextPrecisionWithReference, LLMContextRecall,
                           ResponseRelevancy)
from ragas.run_config import RunConfig
from sentence_transformers import SentenceTransformer

HERE = pathlib.Path(__file__).parent
EMBEDDING_MODEL = 'C:/Coding-projects/bintanong_workspace/MODELS/SEA-LION-E5-Embedding-600M'
JUDGE_MODEL = 'deepseek-chat'


class SeaLionEmbeddings(BaseRagasEmbeddings):
    """Local sentence-transformers model; STS prompt because Answer Relevancy compares question to question."""

    def __init__(self):
        super().__init__()
        self.encoder = SentenceTransformer(EMBEDDING_MODEL, device='cpu')
        self.model = 'SEA-LION-E5-Embedding-600M'  # ragas reads .model as a name string

    def _encode(self, texts):
        return self.encoder.encode(list(texts), prompt_name='STS', normalize_embeddings=True).tolist()

    def embed_query(self, text):
        return self._encode([text])[0]

    def embed_documents(self, texts):
        return self._encode(texts)

    async def aembed_query(self, text):
        return self.embed_query(text)

    async def aembed_documents(self, texts):
        return self.embed_documents(texts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pairs')
    parser.add_argument('out')
    parser.add_argument('--ids', default='')
    args = parser.parse_args()

    rows = [json.loads(x) for x in pathlib.Path(args.pairs).read_text(encoding='utf-8').splitlines() if x.strip()]
    if args.ids:
        wanted = args.ids.split(',')
        rows = [r for r in rows if r['id'] in wanted]
        assert len(rows) == len(wanted), 'unknown id'
    assert all(r['reference_answer'] for r in rows), 'missing reference'

    samples = [{'user_input': r['question'], 'response': r['candidate_answer'],
                'retrieved_contexts': [c['text'] for c in r['retrieved_context']],
                'reference': r['reference_answer']} for r in rows]

    key = dotenv_values(HERE / '.env').get('DEEPSEEK_API_KEY')
    assert key and key.startswith('sk-'), 'DEEPSEEK_API_KEY missing in .env'
    llm = LangchainLLMWrapper(ChatOpenAI(model=JUDGE_MODEL, base_url='https://api.deepseek.com', api_key=key,
                                         temperature=0, max_retries=3, timeout=180),
                              bypass_n=True)  # DeepSeek accepts only n=1; ragas then sends n separate calls
    metrics = [Faithfulness(), ResponseRelevancy(), LLMContextPrecisionWithReference(), LLMContextRecall(),
               FactualCorrectness(mode='precision')]

    started = time.time()
    result = evaluate(EvaluationDataset.from_list(samples), metrics=metrics, llm=llm, embeddings=SeaLionEmbeddings(),
                      run_config=RunConfig(max_workers=4, timeout=600, max_retries=5),
                      token_usage_parser=get_token_usage_for_openai, show_progress=True)
    frame = result.to_pandas()
    names = [c for c in frame.columns if c not in ('user_input', 'response', 'retrieved_contexts', 'reference')]

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    per_row = []
    for row, (_, scored) in zip(rows, frame.iterrows()):
        per_row.append({'id': row['id'], 'query_no': row['query_no'], 'language': row['language'],
                        'answer_status': row['answer_status'], **{n: scored[n] for n in names}})
    with (out / 'ragas_scores.jsonl').open('w', encoding='utf-8', newline='\n') as f:
        for r in per_row:
            f.write(json.dumps({k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in r.items()},
                               ensure_ascii=False) + '\n')

    def mean(items, name):
        values = [r[name] for r in items if not (isinstance(r[name], float) and math.isnan(r[name]))]
        return {'mean': round(sum(values) / len(values), 4) if values else None, 'n': len(values)}

    groups = {'overall': per_row, **{lang: [r for r in per_row if r['language'] == lang]
                                     for lang in ('English', 'Tagalog', 'Taglish')}}
    usage = result.total_tokens()
    summary = {'judge': JUDGE_MODEL, 'embeddings': 'SEA-LION-E5-Embedding-600M (STS prompt)',
               'factual_correctness_mode': 'precision', 'rows': len(per_row),
               'seconds': round(time.time() - started, 1),
               'tokens': {'input': usage.input_tokens, 'output': usage.output_tokens},
               'scores': {g: {n: mean(items, n) for n in names} for g, items in groups.items() if items}}
    (out / 'ragas_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
