"""Read what a pipe holds until it closes or a deadline passes, never longer.

2026-09-26, second review of round D6: validation read what was left of
QLC+'s log with `readlines()`, which returns only at end of file. A process
that inherited the pipe and outlived QLC+ - a helper it forked, detached from
it, that `stop_own_process` does not reach - kept the pipe open, and the
read blocked for as long as that process lived.
"""

import os
import select
import time


def drain_pipe(fd: int, until: float) -> bytes:
    """Everything readable from `fd` before end of file or `until` (monotonic).

    Waits only while data may still come and time remains; once `until` has
    passed it takes at most what is already waiting, one read, and stops.
    """
    chunks: list[bytes] = []
    while True:
        ready, _, _ = select.select([fd], [], [], max(0.0, until - time.monotonic()))
        if not ready:
            break
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        chunks.append(chunk)
        if time.monotonic() >= until:
            break
    return b"".join(chunks)
