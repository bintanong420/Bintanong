from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Local institutional ingestion and source-bound review.')
    commands = parser.add_subparsers(dest='command', required=True)
    prepare_command = commands.add_parser('prepare', help='Create or recheck an unreviewed packet.')
    prepare_command.add_argument('manifest', type=Path)
    prepare_command.add_argument('--out', required=True, type=Path)
    prepare_command.add_argument('--assist-mode', choices=['none', 'flagged', 'all', 'selected'], default='none')
    prepare_command.add_argument('--assist-pages', type=int, nargs='+', default=[])
    prepare_command.add_argument('--assist-items', nargs='+', default=[])
    parse_command = commands.add_parser('parse-llama', help='Parse selected public PDF pages into pending candidates.')
    parse_command.add_argument('source', type=Path)
    parse_command.add_argument('--out', required=True, type=Path)
    parse_command.add_argument('--pages', required=True, type=int, nargs='+')
    parse_command.add_argument('--batch-size', type=int, default=5)
    parse_command.add_argument('--tier', choices=['fast', 'cost_effective', 'agentic', 'agentic_plus'], default='agentic')
    parse_command.add_argument('--version', default='latest')
    parse_command.add_argument('--retry-failed', action='store_true')
    sample_command = commands.add_parser('evaluation-sample', help='Create blank matched-page measurement sheets.')
    sample_command.add_argument('sample', type=Path)
    sample_command.add_argument('--out', required=True, type=Path)
    evaluation_command = commands.add_parser('evaluate', help='Summarize recorded human measurements without filling blanks.')
    evaluation_command.add_argument('measurements', type=Path)
    evaluation_command.add_argument('--out', required=True, type=Path)
    review_command = commands.add_parser('review', help='Open the isolated local researcher interface.')
    review_command.add_argument('packet', type=Path)
    review_command.add_argument('--reviewer', required=True)
    review_command.add_argument('--api-port', type=int, default=8765)
    review_command.add_argument('--ui-port', type=int, default=3050)
    review_command.add_argument('--no-open', action='store_true')
    intake_command = commands.add_parser('intake', help='Open the local researcher tool for uploading and reviewing PDFs.')
    intake_command.add_argument('workspace', type=Path, help='ignored folder outside Git for uploads')
    intake_command.add_argument('--reviewer', required=True)
    intake_command.add_argument('--prepare-python', required=True, type=Path,
                                help='interpreter of the venv where native Docling works')
    intake_command.add_argument('--api-port', type=int, default=8765)
    intake_command.add_argument('--ui-port', type=int, default=3050)
    intake_command.add_argument('--no-open', action='store_true')
    build_command = commands.add_parser('build', help='Build reviewed candidate chunks and compatible metadata.')
    build_command.add_argument('packet', type=Path)
    build_command.add_argument('--out', required=True, type=Path)
    build_command.add_argument('--cache', type=Path)
    build_command.add_argument('--model-dir', type=Path)
    build_command.add_argument('--metadata', type=Path)
    verify_command = commands.add_parser('verify', help='Recheck all package/source/review/configuration bindings.')
    verify_command.add_argument('package', type=Path)
    verify_command.add_argument('--packet', type=Path)
    # Local Supabase only (http://127.0.0.1:54321); the key comes only from the environment.
    stage_command = commands.add_parser('stage', help='Stage a verified package as an inactive local draft.')
    stage_command.add_argument('package', type=Path)
    stage_command.add_argument('--documents', required=True, type=Path, help='JSON list of storage document metadata')
    stage_command.add_argument('--release-label', required=True)
    activate_command = commands.add_parser('activate', help='Activate a checked local draft (owner-authorized).')
    activate_command.add_argument('release_id')
    activate_command.add_argument('--package', required=True, type=Path)
    activate_command.add_argument('--checks-report', required=True, type=Path)
    rollback_command = commands.add_parser('rollback', help='Point the local active release back to a prior one.')
    rollback_command.add_argument('release_id')
    for command in (stage_command, activate_command, rollback_command):
        if command is not stage_command:
            command.add_argument('--authorization-ref', required=True)
        command.add_argument('--actor', required=True)
        command.add_argument('--baseline-dir', required=True, type=Path)
        command.add_argument('--fingerprint-script', required=True, type=Path)
        command.add_argument('--fingerprint-report', required=True, type=Path)
    args = parser.parse_args(argv)
    if args.command in ('stage', 'activate', 'rollback'):
        return _local_release(args)
    try:
        with contextlib.redirect_stdout(sys.stderr):
            if args.command == 'evaluation-sample':
                from .evaluation import create_sample
                result = create_sample(args.sample, args.out)
            elif args.command == 'evaluate':
                from .evaluation import summarize
                result = summarize(args.measurements, args.out)
            elif args.command == 'parse-llama':
                from .llamaparse import parse
                parsed = parse(args.source, args.out, pages=args.pages, batch_size=args.batch_size,
                               tier=args.tier, version=args.version, retry_failed=args.retry_failed)
                result = {'candidate_only': True, 'source_sha256': parsed['source_sha256'],
                          'returned_pages': len(parsed['pages']), 'failed_pages': parsed['failed_pages']}
            elif args.command == 'prepare':
                from .prepare import prepare
                from .vision import VisionProvider
                packet = prepare(args.manifest, args.out, assist_mode=args.assist_mode,
                    assist_provider=VisionProvider.from_environment() if args.assist_mode != 'none' else None,
                    assist_pages=args.assist_pages, assist_items=args.assist_items)
                result = {'packet_id': packet['packet_id'], 'candidate_only': True,
                          'documents': len(packet['documents']), 'items': len(packet['items'])}
            elif args.command == 'review':
                from .serve import serve
                serve(args.packet, args.reviewer, api_port=args.api_port, ui_port=args.ui_port, open_browser=not args.no_open)
                result = {'review_closed': True}
            elif args.command == 'intake':
                from .serve import serve
                serve(None, args.reviewer, api_port=args.api_port, ui_port=args.ui_port, open_browser=not args.no_open,
                      workspace=args.workspace, prepare_python=str(args.prepare_python))
                result = {'review_closed': True}
            elif args.command == 'build':
                from .build import LocalEncoder, build
                result = build(args.packet, args.out, encoder=LocalEncoder(args.model_dir) if args.model_dir else None,
                               cached_package=args.cache, metadata=args.metadata)
            else:
                from .verify import verify
                result = verify(args.package, packet_root=args.packet)
        print(json.dumps(result))
    except (ValueError, OSError, RuntimeError, ImportError) as exc:
        print(f'Ingestion incomplete: {exc}', file=sys.stderr)
        return 1
    return 2 if args.command == 'parse-llama' and result['failed_pages'] else 0


def _local_release(args) -> int:
    from . import local_release as lr
    try:
        with contextlib.redirect_stdout(sys.stderr):
            check = lr.fingerprint_script_check(args.fingerprint_script, args.fingerprint_report)
            common = dict(target_url=lr.LOCAL_TARGET, fingerprint_check=check, actor=args.actor,
                          baseline_dir=args.baseline_dir)
            if args.command == 'stage':
                documents = json.loads(args.documents.read_text(encoding='utf-8'))
            client = lr.local_client(lr.LOCAL_TARGET)
            try:
                if args.command == 'stage':
                    result = lr.stage_draft(args.package, client=client, release_label=args.release_label,
                                            documents=documents, **common)
                elif args.command == 'activate':
                    result = lr.activate_draft(args.release_id, client=client, package_path=args.package,
                        checks_report=args.checks_report, authorization_ref=args.authorization_ref, **common)
                else:
                    result = lr.rollback_to(args.release_id, client=client,
                                            authorization_ref=args.authorization_ref, **common)
            finally:
                client.close()
        print(json.dumps(result))
    except lr.LocalReleaseError as exc:
        print(f'Local release refused or incomplete: {exc}', file=sys.stderr)
        print(json.dumps({'written': exc.written}), file=sys.stderr)
        return 1
    except (ValueError, OSError) as exc:
        print(f'Local release refused: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
