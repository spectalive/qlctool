"""Load a workspace in a real QLC+ and report what it complained about.

The toolkit's other guarantee is structural: a semantic round trip proves an
edit changed only what it targeted, but it cannot prove QLC+ accepts the result.
This runs the actual application headless (`--nowm --nogui`), which loads the
workspace and logs every problem it finds - a fixture whose definition is
missing, two fixtures overlapping, a function it could not build.

QLC+ has no "load and exit" mode: it starts its engine and stays up. So it is
launched, watched until its output goes quiet - which is when loading has
finished - then killed, and the verdict comes from the log rather than the exit
code.
"""

import os
import select
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_BINARIES = (
    "/Applications/QLC+.app/Contents/MacOS/qlcplus",
    "/usr/bin/qlcplus",
    "/usr/local/bin/qlcplus",
)

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
    return shutil.which("qlcplus")


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
    executable = binary or qlcplus_binary()
    if executable is None:
        raise FileNotFoundError(
            "no QLC+ executable found; set QLCTOOL_QLCPLUS to its path"
        )

    process = subprocess.Popen(
        [executable, "--nowm", "--nogui", "-d", "1", "-o", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    output = _read_until_quiet(process, timeout, quiet_period)

    errors = [
        line.strip()
        for line in (output or "").splitlines()
        if any(marker in line for marker in ERROR_MARKERS)
        and not any(marker in line for marker in IGNORED_MARKERS)
    ]
    return ValidationResult(ok=not errors, errors=errors, log=output or "")


def _read_until_quiet(
    process: subprocess.Popen, timeout: float, quiet_period: float
) -> str:
    """Collect output until QLC+ stops talking, then kill it.

    Loading is done when the log goes quiet; waiting the full timeout on every
    file would make validation useless in a test suite.
    """
    deadline = time.monotonic() + timeout
    last_line_at = time.monotonic()
    lines: list[str] = []
    while True:
        if process.poll() is not None:
            lines.extend(process.stdout.readlines())
            break
        now = time.monotonic()
        if now > deadline or now - last_line_at > quiet_period:
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
    process.stdout.close()
    return "".join(lines)
