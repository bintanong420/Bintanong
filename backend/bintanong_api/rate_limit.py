"""Per-person question limit (owner, 3 Nov 2026).

The model answers one question at a time, so one person asking back to back could hold the only answer slot.
Each person may ask `limit` admitted questions per sliding `window_seconds`. Signed-in students are counted per
account; guests per browser, by a random anonymous cookie that New chat (a new chat session) does not reset.
Clearing browser cookies does reset it: the owner chose this over IP limits, which would block a whole campus
network behind one address. Only admitted questions count, so a busy refusal never uses the quota.
"""
from __future__ import annotations

import collections
import re
import secrets
import threading
import time

CLIENT_COOKIE = '__Host-bintanong_client'
CLIENT_COOKIE_MAX_AGE = 30 * 24 * 60 * 60
_CLIENT_ID = re.compile(r'^[A-Za-z0-9_-]{43}$')


def client_id(cookie: str | None) -> tuple[str, bool]:
    """The browser's anonymous id and whether it was newly issued (the caller then sets the cookie)."""
    if cookie is not None and _CLIENT_ID.fullmatch(cookie):
        return cookie, False
    return secrets.token_urlsafe(32), True


class QuestionRateLimit:
    def __init__(self, *, limit: int, window_seconds: int, clock=time.monotonic):
        self._limit, self._window, self._clock = limit, window_seconds, clock
        self._asked: dict[str, collections.deque[float]] = {}
        self._lock = threading.Lock()  # the sync chat route runs in the thread pool

    def admit(self, key: str) -> int | None:
        """Count a question for `key` and return None, or return whole seconds until one is allowed."""
        with self._lock:
            now = self._clock()
            asked = self._asked.setdefault(key, collections.deque())
            while asked and asked[0] <= now - self._window:
                asked.popleft()
            if len(asked) >= self._limit:
                return max(1, int(asked[0] + self._window - now + 0.999))
            asked.append(now)
            self._forget_idle(now)
            return None

    def _forget_idle(self, now: float) -> None:
        # Keep memory bounded: drop people whose questions have all left the window.
        if len(self._asked) > 4096:
            for key in [k for k, v in self._asked.items() if not v or v[-1] <= now - self._window]:
                del self._asked[key]
