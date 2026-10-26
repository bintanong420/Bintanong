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
    review_command = commands.add_parser('review', help='Open the isolated local researcher interface.')
    review_command.add_argument('packet', type=Path)
    review_command.add_argument('--reviewer', required=True)
    review_command.add_argument('--api-port', type=int, default=8765)
    review_command.add_argument('--ui-port', type=int, default=3001)
    review_command.add_argument('--no-open', action='store_true')
    build_command = commands.add_parser('build', help='Build reviewed candidate chunks and compatible metadata.')
    build_command.add_argument('packet', type=Path)
    build_command.add_argument('--out', required=True, type=Path)
    build_command.add_argument('--cache', type=Path)
    build_command.add_argument('--model-dir', type=Path)
    build_command.add_argument('--metadata', type=Path)
    verify_command = commands.add_parser('verify', help='Recheck all package/source/review/configuration bindings.')
    verify_command.add_argument('package', type=Path)
    verify_command.add_argument('--packet', type=Path)
    args = parser.parse_args(argv)
    try:
        with contextlib.redirect_stdout(sys.stderr):
            if args.command == 'prepare':
                from .prepare import prepare
                packet = prepare(args.manifest, args.out)
                result = {'packet_id': packet['packet_id'], 'candidate_only': True,
                          'documents': len(packet['documents']), 'items': len(packet['items'])}
            elif args.command == 'review':
                from .serve import serve
                serve(args.packet, args.reviewer, api_port=args.api_port, ui_port=args.ui_port, open_browser=not args.no_open)
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
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
