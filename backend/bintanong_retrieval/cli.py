"""Internal JSON debug command. Exit 2 means a retrieval gate remains open."""
import argparse
import json
from pathlib import Path

from backend.bintanong_storage.client import SupabaseStorageClient
from .engine import RetrievalEngine
from .query import QueryEncoder
from .types import RetrievalRequest, RetrievalSettings


def main(argv=None):
    parser=argparse.ArgumentParser(description='Retrieve cited context without generating an answer')
    parser.add_argument('--query',required=True)
    parser.add_argument('--release-id',required=True)
    parser.add_argument('--scope',action='append',default=[])
    parser.add_argument('--entity',action='append',default=[])
    parser.add_argument('--document-version',action='append',default=[])
    parser.add_argument('--top-k',type=int,choices=[3,5,8],default=5)
    parser.add_argument('--context-budget',type=int,default=2048)
    parser.add_argument('--min-similarity',type=float,default=0.5)
    parser.add_argument('--asset-manifest',type=Path,help='External JSON mapping model-relative paths to verified SHA-256')
    args=parser.parse_args(argv)
    request=RetrievalRequest(args.query,args.release_id,tuple(args.scope),tuple(args.entity),tuple(args.document_version))
    settings=RetrievalSettings(args.top_k,args.context_budget,args.min_similarity)
    digests=json.loads(args.asset_manifest.read_text(encoding='utf-8')) if args.asset_manifest else {}
    encoder=QueryEncoder(asset_digests=digests)
    client=SupabaseStorageClient()
    try:
        result=RetrievalEngine(client,encoder,settings).retrieve(request)
    finally:
        client.close()
    print(json.dumps(result,ensure_ascii=False,sort_keys=True,allow_nan=False))
    return 0 if result['status']=='ok' else 2
