"""Transient, bounded parser job (master 15.1 step 4): untrusted file parsing runs in a spawned child.

Bytes go in and structured rows come back through a pipe; nothing touches disk. A timeout kills the
child, and a crash ends only the child; both refuse the upload. Memory is bounded by the upload page
and pixel caps (and by the container limit in deployment); Windows has no per-process rlimit here.
"""
from __future__ import annotations

import multiprocessing

from ..bintanong_routing.contracts import CatalogEntry
from .grades import ExtractionResult, extract_grade_rows
from .uploads import UploadRejected, validate_upload

PARSE_TIMEOUT_SECONDS = 30


def _child(connection, target, args):
    try:
        connection.send(('ok', target(*args)))
    except UploadRejected as error:
        connection.send(('rejected', error.reason))
    except Exception:
        connection.send(('rejected', 'unreadable'))
    finally:
        connection.close()


def run_isolated(target, *args, timeout: float = PARSE_TIMEOUT_SECONDS):
    context = multiprocessing.get_context('spawn')
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=_child, args=(sender, target, args), daemon=True)
    process.start()
    sender.close()
    try:
        if not receiver.poll(timeout):
            raise UploadRejected('parse_timeout')
        try:
            kind, value = receiver.recv()
        except EOFError:  # the child died before answering
            raise UploadRejected('unreadable') from None
    finally:
        receiver.close()
        if process.is_alive():
            process.kill()
        process.join(5)
    if kind == 'rejected':
        raise UploadRejected(value)
    return value


def extract_isolated(data: bytes, catalog: tuple[CatalogEntry, ...], *, program_id: str,
                     curriculum_id: str, timeout: float = PARSE_TIMEOUT_SECONDS) -> ExtractionResult:
    """Raw upload bytes in; every PDF/image parser (validation included) runs inside the child."""
    return run_isolated(_extract, data, tuple(catalog), program_id, curriculum_id, timeout=timeout)


def _extract(data, catalog, program_id, curriculum_id):
    return extract_grade_rows(validate_upload(data), catalog, program_id=program_id, curriculum_id=curriculum_id)
