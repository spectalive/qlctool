"""Load a workspace in a real QLC+ and report what it complained about.

The toolkit's other guarantee is structural: a semantic round trip proves an
edit changed only what it targeted, but it cannot prove QLC+ accepts the result.
This runs the actual application headless (`--nowm --nogui`), which loads the
workspace and logs every problem it finds - a fixture whose definition is
missing, two fixtures overlapping, a function it could not build.

QLC+ has no "load and exit" mode: it starts its engine and stays up. So it is
launched, watched until loading is done, then killed, and the verdict comes from
the log rather than the exit code.

Two builds behave differently. The 4.x widgets build (`qlcplus`) takes
`--nogui`, loads with no window at all, and then falls silent - that is the one
to prefer. The 5.x QML build (`qlcplus-qml`) has no headless mode: it opens a
window and keeps logging while it renders, so loading is considered finished once
its end-of-load markers appear and the log settles.
"""

import os
import select
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# The QML build's -g writes the debug log here instead of stdout, which is what
# makes a background launch readable: `open -g` does not give us its stdout.
QML_LOG_FILE = Path.home() / "QLC+.log"

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
    for candidate in DEFAULT_BINARIES:
        if Path(candidate).exists():
            return candidate
    return shutil.which("qlcplus") or shutil.which("qlcplus-qml")


def validate_workspace(
    path: str | Path,
    binary: str | None = None,
    timeout: float = 30.0,
    quiet_period: float = 2.0,
) -> ValidationResult:
    """Load the workspace in headless QLC+ and collect its complaints.

    Raises FileNotFoundError when no QLC+ is installed - a missing validator must
    never read as a passing validation.
    """
    # Absolute: a background launch goes through `open`, which does not
    # inherit this process's working directory.
    path = Path(path).resolve()
    executable = binary or qlcplus_binary()
    if executable is None:
        raise FileNotFoundError(
            "no QLC+ executable found; set QLCTOOL_QLCPLUS to its path"
        )

    qml = Path(executable).name.endswith("-qml")
    # The QML build has no --nogui and takes -d without a level.
    arguments = (
        [executable, "-d", "-m", "-o", str(path)] if qml
        else [executable, "--nowm", "--nogui", "-d", "1", "-o", str(path)]
    )
    bundle = _app_bundle(executable)
    if qml and bundle is not None and not os.environ.get("QLCTOOL_FOREGROUND"):
        output = _run_in_background(bundle, executable, path, timeout, quiet_period)
        if output is not None:
            return _verdict(output)

    process = subprocess.Popen(
        arguments,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    output = _read_until_loaded(process, timeout, quiet_period, qml)
    return _verdict(output)


def _verdict(output: str) -> ValidationResult:
    if not (output or "").strip():
        # QLC+ prints its banner before it does anything else, so an empty log
        # means it never ran. Reporting that as "no complaints" is the one
        # failure this whole safety net exists to avoid.
        raise RuntimeError(
            "QLC+ produced no output; the workspace was never actually loaded"
        )
    errors = [
        line.strip()
        for line in (output or "").splitlines()
        if any(marker in line for marker in ERROR_MARKERS)
        and not any(marker in line for marker in IGNORED_MARKERS)
    ]
    return ValidationResult(ok=not errors, errors=errors, log=output or "")


def _app_bundle(executable: str) -> str | None:
    """The .app this executable lives in, on macOS - None anywhere else."""
    if sys.platform != "darwin":
        return None
    for parent in Path(executable).parents:
        if parent.suffix == ".app":
            return str(parent)
    return None


def _run_in_background(
    bundle: str, executable: str, path: str | Path,
    timeout: float, quiet_period: float,
) -> str | None:
    """Load the workspace without QLC+ taking the screen, and return its log.

    `open -g` launches the bundle without bringing it to the front, which is
    what keeps a generate-and-validate run from stealing focus every time. The
    cost is that `open` returns immediately and hands back no stdout, so QLC+ is
    told to log to a file (-g) and only the processes this call started are
    killed afterwards - a QLC+ the owner has open stays open.
    """
    before = _running_pids(executable)
    QML_LOG_FILE.write_text("")
    launched = subprocess.run(
        ["open", "-g", "-a", bundle, "--args",
         "-d", "-g", "-m", "-o", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if launched.returncode != 0:
        # `open` refuses while a copy of the app is still going down (-600),
        # among other things. Rather than guess, hand the run back to the
        # foreground path, which owns its own process.
        return None

    deadline = time.monotonic() + timeout
    loaded_at: float | None = None
    while time.monotonic() < deadline:
        text = QML_LOG_FILE.read_text(errors="replace")
        if loaded_at is None and any(m in text for m in QML_LOADED_MARKERS):
            loaded_at = time.monotonic()
        if loaded_at is not None and time.monotonic() - loaded_at > quiet_period:
            break
        time.sleep(0.2)

    started = _running_pids(executable) - before
    for pid in started:
        _terminate(pid)
    if loaded_at is None:
        # Nothing ever reported a finished load. The usual reason is a QLC+ the
        # owner already has open: `open -g` activates that instance instead of
        # starting one, returns 0, and nothing is written to the log file. Hand
        # the run to the foreground path, which owns its own process, rather
        # than reading an empty log as a clean workspace.
        _wait_for_exit(started, executable)
        return None
    _wait_for_exit(started, executable)
    return QML_LOG_FILE.read_text(errors="replace")


def _wait_for_exit(started: set[int], executable: str) -> None:
    """Let the processes this call started actually go.

    `open` answers -600 if asked to launch the bundle again while a copy is
    still shutting down.
    """
    gone_by = time.monotonic() + 5.0
    while started & _running_pids(executable) and time.monotonic() < gone_by:
        time.sleep(0.1)


def _running_pids(executable: str) -> set[int]:
    result = subprocess.run(
        ["pgrep", "-f", Path(executable).name],
        capture_output=True,
        text=True,
        check=False,
    )
    return {int(line) for line in result.stdout.split() if line.isdigit()}


def _terminate(pid: int) -> None:
    try:
        os.kill(pid, 15)
    except ProcessLookupError:
        pass


def _read_until_loaded(
    process: subprocess.Popen, timeout: float, quiet_period: float, qml: bool
) -> str:
    """Collect output until QLC+ has finished loading, then kill it.

    For the 4.x build that means the log going quiet. The QML build keeps
    logging as it renders, so it is stopped a moment after its first
    end-of-load marker; waiting the full timeout on every file would make
    validation useless in a test suite.
    """
    deadline = time.monotonic() + timeout
    last_line_at = time.monotonic()
    loaded_at: float | None = None
    lines: list[str] = []
    while True:
        if process.poll() is not None:
            lines.extend(process.stdout.readlines())
            break
        now = time.monotonic()
        settled = (
            loaded_at is not None and now - loaded_at > quiet_period
            if qml
            else now - last_line_at > quiet_period
        )
        if now > deadline or settled:
            process.kill()
            process.wait()
            lines.extend(process.stdout.readlines())
            break
        ready, _, _ = select.select([process.stdout], [], [], 0.2)
        if ready:
            line = process.stdout.readline()
            if line:
                lines.append(line)
                last_line_at = time.monotonic()
                if loaded_at is None and any(
                    marker in line for marker in QML_LOADED_MARKERS
                ):
                    loaded_at = last_line_at
    process.stdout.close()
    return "".join(lines)
