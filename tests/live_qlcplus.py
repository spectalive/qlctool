"""A QLC+ of the suite's own, serving its web API on a free port, killed by exact pid.

The workspace it runs is a copy with every `<Input>`, `<Output>` and
`<Feedback>` removed from `<InputOutputMap>`, so nothing it does leaves the
machine: no Art-Net, no DMX interface, no MIDI to a pad the operator's show is
using. It is started with `open -n -g` - a new instance, in the background, so
a QLC+ somebody already runs is neither activated nor touched - and found by
the copy's unique path on its command line. The launch holds
`validate.LAUNCH_LOCK` for the whole test: validation's background launch
kills the QLC+ processes that appeared while it ran, and must never count
this one among them.
"""

import fcntl
import socket
import subprocess
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from lxml import etree

from qlctool.validate import LAUNCH_LOCK, qlcplus_binary
from qlctool.xmlutil import iter_local

STRIPPED = ("Input", "Output", "Feedback")


def qml_bundle() -> str | None:
    """The QLC+ 5 app bundle to launch, or None where there is none (CI)."""
    binary = qlcplus_binary()
    if binary is None or not binary.endswith("-qml"):
        return None
    bundle = next((p for p in Path(binary).parents if p.suffix == ".app"), None)
    return str(bundle) if bundle else None


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def offline_copy(workspace: Path, folder: Path) -> Path:
    """`workspace` without any input, output or feedback patch."""
    tree = etree.parse(str(workspace))
    for io_map in iter_local(tree.getroot(), "InputOutputMap"):
        for element in [e for name in STRIPPED for e in iter_local(io_map, name)]:
            element.getparent().remove(element)
    copy = folder / f"mcp-live-{time.monotonic_ns()}.qxw"
    tree.write(str(copy), xml_declaration=True, encoding="UTF-8")
    return copy


@contextmanager
def running_qlcplus(workspace: Path, folder: Path) -> Iterator[int]:
    """Yield the web port of a QLC+ running an offline copy of `workspace`."""
    bundle = qml_bundle()
    assert bundle is not None, "no QLC+ 5 bundle to launch"
    copy = offline_copy(workspace, folder)
    port = free_port()
    assert port not in (9998, 9999)
    with LAUNCH_LOCK.open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        subprocess.run(
            ["open", "-n", "-g", "-a", bundle, "--args", "-w", "--wp", str(port), "-o", str(copy)],
            check=True,
        )
        pid = _pid_of(copy)
        try:
            _wait_for_web(port)
            yield port
        finally:
            _kill(pid)


def _pid_of(copy: Path) -> int:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        found = subprocess.run(
            ["pgrep", "-f", str(copy)], capture_output=True, text=True, check=False
        )
        pids = [int(p) for p in found.stdout.split()]
        if pids:
            assert len(pids) == 1, pids
            return pids[0]
        time.sleep(0.2)
    raise TimeoutError(f"no QLC+ appeared running {copy}")


def _wait_for_web(port: int) -> None:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                time.sleep(1.0)  # the workspace finishes loading after the port opens
                return
        time.sleep(0.3)
    raise TimeoutError(f"QLC+ never opened its web port {port}")


def _kill(pid: int) -> None:
    """SIGTERM the one process this helper started, SIGKILL if it lingers."""
    subprocess.run(["kill", str(pid)], check=False)
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if (
            subprocess.run(["kill", "-0", str(pid)], capture_output=True, check=False).returncode
            != 0
        ):
            return
        time.sleep(0.2)
    subprocess.run(["kill", "-9", str(pid)], check=False)
