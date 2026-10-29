"""Answer admission (owner, 24 Oct 2026): the model serves a fixed number of requests at a time, so a few
students wait in a short queue and the rest are told it is busy before any stream starts.

A reservation is taken in the route and released when its response ends, so a client that disconnects before
the stream body starts cannot leak it. Answer timeouts start only once a turn holds a running slot.
"""
from __future__ import annotations

import asyncio
import contextlib
import threading

from fastapi.responses import StreamingResponse

from backend.bintanong_api.session import ApiError


class AnswerAdmission:
    def __init__(self, *, running: int, waiting: int):
        self._limit = running + waiting
        self._slots = asyncio.Semaphore(running)
        self._admitted = 0
        self._accounts = set()
        self._lock = threading.Lock()  # the sync chat route runs in the thread pool

    @property
    def admitted(self) -> int:
        with self._lock:
            return self._admitted

    def reserve(self, *, account_id=None) -> Reservation:
        with self._lock:
            if account_id is not None and account_id in self._accounts:
                raise ApiError(409, 'account_busy')
            if self._admitted >= self._limit:
                raise ApiError(503, 'answers_busy')
            self._admitted += 1
            if account_id is not None:
                self._accounts.add(account_id)
        return Reservation(self, account_id)

    def _release(self, account_id=None) -> None:
        with self._lock:
            self._admitted -= 1
            self._accounts.discard(account_id)


class Reservation:
    def __init__(self, admission: AnswerAdmission, account_id=None):
        self._admission, self._released = admission, False
        self._account = account_id

    @contextlib.asynccontextmanager
    async def running(self, progress):
        slots = self._admission._slots
        if slots.locked():
            progress('waiting')
        async with slots:
            yield

    def release(self) -> None:
        if not self._released:
            self._released = True
            self._admission._release(self._account)


class AdmittedStream(StreamingResponse):
    def __init__(self, content, reservation: Reservation, **kwargs):
        super().__init__(content, **kwargs)
        self._reservation = reservation

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        finally:
            self._reservation.release()
