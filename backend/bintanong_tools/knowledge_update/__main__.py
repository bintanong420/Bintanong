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
    args = parser.parse_args(argv)
    try:
        from .prepare import prepare
        with contextlib.redirect_stdout(sys.stderr):
            packet = prepare(args.manifest, args.out)
        print(json.dumps({'packet_id': packet['packet_id'], 'candidate_only': True,
                          'documents': len(packet['documents']), 'items': len(packet['items'])}))
    except (ValueError, OSError, RuntimeError) as exc:
        print(f'Ingestion incomplete: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
