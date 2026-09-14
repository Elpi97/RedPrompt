"""Stdout bridge that forwards lines to a queue for the GUI."""

from __future__ import annotations

import queue
import re
from typing import TextIO


_SECRET_RE = re.compile(
    r'(Authorization:\s*Bearer\s+)\S+|([A-Za-z0-9_]*(?:API_KEY|TOKEN|SECRET)[A-Za-z0-9_]*\s*[:=]\s*)\S+',
    re.IGNORECASE,
)


def redact(line: str) -> str:
    """Mask obvious secrets before they hit the live log."""
    return _SECRET_RE.sub(r'\1***', line)


class QueueWriter:
    """File-like object that pushes text chunks into a queue as log lines."""

    def __init__(self, q: queue.Queue, fallback: TextIO | None = None):
        self.q = q
        self.fallback = fallback
        self._buf = ''

    def write(self, data: str) -> int:
        if not data:
            return 0
        if self.fallback is not None:
            try:
                self.fallback.write(data)
            except Exception:
                pass
        self._buf += data
        while '\n' in self._buf:
            line, self._buf = self._buf.split('\n', 1)
            self.q.put(('log', redact(line)))
        return len(data)

    def flush(self) -> None:
        if self._buf:
            self.q.put(('log', redact(self._buf)))
            self._buf = ''
        if self.fallback is not None:
            try:
                self.fallback.flush()
            except Exception:
                pass
