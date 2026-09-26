"""A QLC+ of the suite's own, serving its web API on a free port, stopped by exact pid.

The workspace it runs is `offline_workspace`'s copy, so nothing it does
leaves the machine: no Art-Net, no DMX interface, no MIDI to a pad the
operator's show is using. It is this process's own child, started with
`quiet_launch_environment` so its window never takes the screen, and
stopped with `stop_own_process`: a QLC+ somebody else runs is never touched.
"""

import socket
import subprocess
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from qlctool.offline_workspace import offline_workspace
from qlctool.quiet_launch_environment import quiet_launch_environment
from qlctool.refuse_saved_io import refuse_saved_io
from qlctool.stop_own_process import stop_own_process
from qlctool.validate import qlcplus_binary


def qml_binary() -> str | None:
    """The QLC+ 5 executable, which serves the web API this suite reads; None in CI."""
    binary = qlcplus_binary()
    return binary if binary is not None and binary.endswith("-qml") else None


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


@contextmanager
def running_qlcplus(workspace: Path, folder: Path) -> Iterator[int]:
    """Yield the web port of a QLC+ running an offline copy of `workspace`."""
    binary = qml_binary()
    assert binary is not None, "no QLC+ 5 to launch"
    refuse_saved_io()
    copy = offline_workspace(workspace, folder / "live.qxw")
    port = free_port()
    assert port not in (9998, 9999)
    process = subprocess.Popen(
        [binary, "-w", "--wp", str(port), "-o", str(copy)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=quiet_launch_environment(),
    )
    try:
        _wait_for_web(port)
        yield port
    finally:
        stop_own_process(process)


def _wait_for_web(port: int) -> None:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                time.sleep(1.0)  # the workspace finishes loading after the port opens
                return
        time.sleep(0.3)
    raise TimeoutError(f"QLC+ never opened its web port {port}")
