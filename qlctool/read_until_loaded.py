"""Read QLC+'s log until loading is done, stop it, and say whether it finished.

For the 4.x build that means the log going quiet. The QML build keeps logging
as it renders, so it is stopped a moment after its first end-of-load marker;
waiting the full timeout on every file would make validation useless in a
test suite.

2026-09-26, second review of round D6, two reads that could hang or lie:
the log was read a line at a time after `select()`, and `readline()` blocks
on a partial line until its newline comes, past any timeout; and what was
left after the kill was read with `readlines()`, which blocks until every
process holding the pipe has closed it. Both now read raw chunks
(`drain_pipe`) against the validation's own deadline. And a QML load that
hit the timeout without its marker counted as a pass; `marker_seen` now says
so, and `validate` fails it.
"""

import subprocess
import time

from .drain_pipe import drain_pipe
from .loaded_log import LoadedLog
from .qml_loaded_markers import QML_LOADED_MARKERS
from .stop_own_process import stop_own_process


def read_until_loaded(
    process: "subprocess.Popen[bytes]",
    timeout: float,
    quiet_period: float,
    qml: bool,
    drain_seconds: float = 1.0,
) -> LoadedLog:
    """Collect QLC+'s output until it has finished loading or `timeout` passes, then stop it.

    What is still in the pipe once QLC+ is gone is read for at most
    `drain_seconds`, and not past the deadline by more than a tenth of a
    second: enough to take what the stopped process had already written.
    """
    stdout = process.stdout
    assert stdout is not None, "QLC+ is started with its stdout piped"
    fd = stdout.fileno()
    deadline = time.monotonic() + timeout
    last_output_at = time.monotonic()
    loaded_at: float | None = None
    received = bytearray()
    longest = max(len(marker) for marker in QML_LOADED_MARKERS)
    while True:
        now = time.monotonic()
        if process.poll() is not None:
            break
        settled = (
            loaded_at is not None and now - loaded_at > quiet_period
            if qml
            else now - last_output_at > quiet_period
        )
        if now > deadline or settled:
            stop_own_process(process)
            break
        chunk = drain_pipe(fd, min(now + 0.2, deadline))
        if chunk:
            # A marker may straddle two reads: search from just before this one.
            start = max(0, len(received) - longest)
            received += chunk
            last_output_at = time.monotonic()
            window = received[start:].decode(errors="replace")
            if loaded_at is None and any(marker in window for marker in QML_LOADED_MARKERS):
                loaded_at = last_output_at
    now = time.monotonic()
    received += drain_pipe(fd, max(min(deadline, now + drain_seconds), now + 0.1))
    stdout.close()
    text = received.decode(errors="replace")
    seen = not qml or any(marker in text for marker in QML_LOADED_MARKERS)
    return LoadedLog(text=text, marker_seen=seen)
