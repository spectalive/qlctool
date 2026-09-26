"""Load a workspace in a real QLC+ and report what it complained about.

The toolkit's other guarantee is structural: a semantic round trip proves an
edit changed only what it targeted, but it cannot prove QLC+ accepts the result.
This runs the actual application, which loads the workspace and logs every
problem it finds - a fixture whose definition is missing, two fixtures
overlapping, a function it could not build.

QLC+ has no "load and exit" mode: it starts its engine and stays up. So it is
launched, watched until loading is done, then killed, and the verdict comes from
its log rather than the exit code.

What QLC+ loads is an offline copy (`validation_copy`, `offline_workspace`):
every universe kept, its `<Input>`, `<Output>` and `<Feedback>` removed, an
audio beat generator made internal and a network server's autostart off. A
validation run during a show must never open the rig's DMX interface,
Art-Net, MIDI or the microphone again, and QLC+ 5 has no flag to load without
them - so validation no longer checks the I/O map the file names (2026-09-26,
reviews of round D6). The default patches QLC+ keeps in its own settings are
beyond a copy's reach: validation refuses to start while any exist
(`refuse_saved_io`). QLC+ also records the copy in its recent-files list,
which is not restored. The only process it stops is
the one it started, by that child's exact pid (`stop_own_process`).

Two builds behave differently. The 4.x widgets build (`qlcplus`) takes
`--nogui`, loads with no window at all, and then falls silent - that is the one
to prefer. The 5.x QML build (`qlcplus-qml`) has no headless mode: it opens a
window, kept from taking the screen by `quiet_launch_environment`, and keeps
logging while it renders, so loading is considered finished once its
end-of-load markers appear and the log settles.

Versioned bundles in /Applications are found too, newest first, and a binary
this CPU cannot run is skipped (`qlcplus_candidates`).
"""

import os
import select
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

from .qlcplus_candidates import qlcplus_candidates
from .quiet_launch_environment import quiet_launch_environment
from .refuse_saved_io import refuse_saved_io
from .stop_own_process import stop_own_process
from .validation_copy import validation_copy

DEFAULT_BINARIES = (
    # 4.x first: it is the only build that loads with no GUI at all.
    "/Applications/QLC+ 4.app/Contents/MacOS/qlcplus",
    "/Applications/QLC+.app/Contents/MacOS/qlcplus",
    "/usr/bin/qlcplus",
    "/usr/local/bin/qlcplus",
    "/Applications/QLC+.app/Contents/MacOS/qlcplus-qml",
    "/usr/bin/qlcplus-qml",
    "/usr/local/bin/qlcplus-qml",
)

# The QML build logs these once the workspace is on screen; it never goes quiet
# on its own, so they are what "loading finished" means there.
QML_LOADED_MARKERS = ("renderPage", "MasterTimer", "Time is late")

# Lines that mean the workspace itself is wrong.
ERROR_MARKERS = (
    "cannot be created",
    "overlapping with fixture",
    "No fixture definition",
    "out of bounds",
    "Unable to read from",
    "failed:",
)
# Noise QLC+ prints on every start, regardless of the file.
IGNORED_MARKERS = (
    "libpng",
    "Window position",
    "Cache already contains",
    "Q Light Controller Plus",
    "licensed under",
    "Copyright",
)


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    log: str = ""

    def describe(self) -> str:
        if self.ok:
            return "QLC+ loaded the workspace with no complaints"
        return "\n".join(self.errors)


def qlcplus_binary() -> str | None:
    """The QLC+ executable to validate with, or None when none is installed."""
    override = os.environ.get("QLCTOOL_QLCPLUS")
    if override:
        return override if Path(override).exists() else None
    candidates = qlcplus_candidates(DEFAULT_BINARIES)
    if candidates:
        return candidates[0]
    return shutil.which("qlcplus") or shutil.which("qlcplus-qml")


def validate_workspace(
    path: str | Path,
    binary: str | None = None,
    timeout: float = 30.0,
    quiet_period: float = 1.0,
    allow_saved_io: bool = False,
) -> ValidationResult:
    """Load an offline copy of the workspace in QLC+ and collect its complaints.

    Raises FileNotFoundError when no QLC+ is installed - a missing validator must
    never read as a passing validation.

    `quiet_period` is how long after the end-of-load markers the log is still
    read. Measured over nine launches of the QML build (2026-09-22): a fixture
    complaint lands in the same 20 ms as the first marker and the log stops
    growing 0,2 s after it, so one second is a fivefold margin - and half of
    what every validation used to wait.

    Raises RuntimeError, before QLC+ is started, when QLC+'s own settings
    hold default I/O patches it would open at startup (`refuse_saved_io`),
    unless `allow_saved_io` or `QLCTOOL_ALLOW_SAVED_IO=1` says to go ahead.
    QLC+ adds each file it loads to its recent-files list; validation does
    not restore that list.
    """
    path = Path(path).resolve()
    executable = binary or qlcplus_binary()
    if executable is None:
        raise FileNotFoundError("no QLC+ executable found; set QLCTOOL_QLCPLUS to its path")

    qml = Path(executable).name.endswith("-qml")
    refuse_saved_io(allow_saved_io)
    try:
        with validation_copy(path) as copy:
            output = _load(executable, copy, qml, timeout, quiet_period)
    except etree.XMLSyntaxError as error:
        # QLC+ reads a broken file up to the break, I/O patches included, so it
        # is never handed one: the syntax error is the verdict.
        return ValidationResult(ok=False, errors=[f"not well-formed XML: {error}"])
    return _verdict(output)


def _load(executable: str, copy: Path, qml: bool, timeout: float, quiet_period: float) -> str:
    """Start QLC+ on `copy`, read its log until loading is done, and stop it."""
    # The QML build has no --nogui and takes -d without a level.
    arguments = (
        [executable, "-d", "-m", "-o", str(copy)]
        if qml
        else [executable, "--nowm", "--nogui", "-d", "1", "-o", str(copy)]
    )
    # Unbuffered bytes: a buffered reader takes every line waiting in the pipe
    # at once, and select() then sees none of the ones it holds - the QML
    # build's end-of-load marker sat in the buffer until the timeout.
    process = subprocess.Popen(
        arguments,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
        env=quiet_launch_environment(),
    )
    try:
        return _read_until_loaded(process, timeout, quiet_period, qml)
    finally:
        # Reaped already when loading finished; a reaped pid is not asked
        # about again, since the system may have handed it to someone else.
        if process.returncode is None:
            stop_own_process(process)


def _verdict(output: str) -> ValidationResult:
    if not (output or "").strip():
        # QLC+ prints its banner before it does anything else, so an empty log
        # means it never ran. Reporting that as "no complaints" is the one
        # failure this whole safety net exists to avoid.
        raise RuntimeError("QLC+ produced no output; the workspace was never actually loaded")
    errors = [
        line.strip()
        for line in (output or "").splitlines()
        if any(marker in line for marker in ERROR_MARKERS)
        and not any(marker in line for marker in IGNORED_MARKERS)
    ]
    return ValidationResult(ok=not errors, errors=errors, log=output or "")


def _read_until_loaded(
    process: "subprocess.Popen[bytes]", timeout: float, quiet_period: float, qml: bool
) -> str:
    """Collect output until QLC+ has finished loading, then kill it.

    For the 4.x build that means the log going quiet. The QML build keeps
    logging as it renders, so it is stopped a moment after its first
    end-of-load marker; waiting the full timeout on every file would make
    validation useless in a test suite.
    """
    stdout = process.stdout
    assert stdout is not None, "QLC+ is started with its stdout piped"
    deadline = time.monotonic() + timeout
    last_line_at = time.monotonic()
    loaded_at: float | None = None
    lines: list[str] = []
    while True:
        if process.poll() is not None:
            lines.extend(line.decode(errors="replace") for line in stdout.readlines())
            break
        now = time.monotonic()
        settled = (
            loaded_at is not None and now - loaded_at > quiet_period
            if qml
            else now - last_line_at > quiet_period
        )
        if now > deadline or settled:
            stop_own_process(process)
            lines.extend(line.decode(errors="replace") for line in stdout.readlines())
            break
        ready, _, _ = select.select([stdout], [], [], 0.2)
        if ready:
            line = stdout.readline().decode(errors="replace")
            if line:
                lines.append(line)
                last_line_at = time.monotonic()
                if loaded_at is None and any(marker in line for marker in QML_LOADED_MARKERS):
                    loaded_at = last_line_at
    stdout.close()
    return "".join(lines)
