"""Development ranking metrics, independent of model execution or answer generation.

Observations must come from a separately recorded retrieval run. Synthetic vectors
exercise mechanics only; neither rankings nor these metrics prove source approval.
"""
import argparse
import json
import math
from pathlib import Path


def _validate(cases, rankings, k, threshold):
    if k not in (3,5,8) or not math.isfinite(threshold) or not -1<=threshold<=1:
        raise ValueError('invalid k or threshold')
    if not cases or len({c['case_id'] for c in cases})!=len(cases):
        raise ValueError('nonempty unique development cases required')
    for case in cases:
        if case['split']!='dev':
            raise ValueError('final cases cannot be used for development tuning')
        if case['status'] not in ('synthetic','candidate','verified'):
            raise ValueError('unknown case approval status')
        rows=rankings.get(case['case_id'])
        if not isinstance(rows,list):
            raise ValueError('every development case requires observed rankings')
        if len({r['chunk_id'] for r in rows})!=len(rows) or any(
            not math.isfinite(r['similarity']) or not -1<=r['similarity']<=1 for r in rows
        ):
            raise ValueError('rankings contain duplicate IDs or invalid scores')


def _average(rows):
    recall=[row['recall_at_k'] for row in rows if row['recall_at_k'] is not None]
    return dict(case_count=len(rows),precision_at_k=sum(r['precision_at_k'] for r in rows)/len(rows),
                recall_at_k=sum(recall)/len(recall) if recall else None)


def evaluate_rankings(cases, rankings, k=5, threshold=0.5):
    _validate(cases,rankings,k,threshold)
    measured=[]
    for case in cases:
        ranked=sorted(rankings[case['case_id']],key=lambda r:(-r['similarity'],r['chunk_id']))
        selected=[r['chunk_id'] for r in ranked if r['similarity']>=threshold][:k]
        gold=set(case['gold_chunk_ids'])
        hits=len(gold.intersection(selected))
        measured.append(dict(case_id=case['case_id'],language=case['language'],category=case['category'],
            precision_at_k=hits/k,recall_at_k=hits/len(gold) if gold else None,
            returned_count=len(selected),false_positive_count=len(set(selected)-gold),
            missing_gold=sorted(gold-set(selected)),selected_chunk_ids=selected,
            unsupported_detected=not selected if not gold else None))
    unsupported=[r['unsupported_detected'] for r in measured if r['unsupported_detected'] is not None]
    report=dict(schema_version='bintanong-retrieval-evaluation-v1',top_k=k,threshold=threshold,
        cases=measured,overall=_average(measured),
        unsupported_detection_rate=sum(unsupported)/len(unsupported) if unsupported else None,
        institutional_gate_eligible=False,
        gate_reason='ranking metrics require separate source/citation and independent approval evidence')
    for field in ('language','category'):
        report['by_'+field]={value:_average([r for r in measured if r[field]==value])
                           for value in sorted({r[field] for r in measured})}
    return report


def calibrate_threshold(cases, rankings, k=5, thresholds=(0.0,0.25,0.5,0.75,0.9)):
    candidates=[]
    for threshold in thresholds:
        report=evaluate_rankings(cases,rankings,k,threshold)
        # Equal case weighting; reward full positive recall and unsupported abstention,
        # then minimize irrelevant evidence. Conservative tie-break: higher threshold.
        recovery=sum(r['recall_at_k'] if r['recall_at_k'] is not None else float(r['unsupported_detected'])
                     for r in report['cases'])/len(cases)
        false_positives=sum(r['false_positive_count'] for r in report['cases'])
        candidates.append((recovery,-false_positives,threshold,report))
    if not candidates:
        raise ValueError('threshold grid must not be empty')
    best=max(candidates,key=lambda row:row[:3])
    return dict(threshold=best[2],top_k=k,development_recovery=best[0],
                selected_report=best[3],trials=[c[3] for c in candidates])


def main(argv=None):
    parser=argparse.ArgumentParser(description='Development-only retrieval ranking calibration')
    parser.add_argument('--cases',type=Path,required=True)
    parser.add_argument('--observations',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    cases=json.loads(args.cases.read_text(encoding='utf-8'))
    rankings=json.loads(args.observations.read_text(encoding='utf-8'))
    report={str(k):calibrate_threshold(cases,rankings,k) for k in (3,5,8)}
    serialized=json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)
    if args.output:
        args.output.write_text(serialized,encoding='utf-8')
    else:
        print(serialized)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
