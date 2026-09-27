"""Launch QLC+ on a workspace copy and read its log until loading is done."""

import subprocess
from pathlib import Path

from .loaded_log import LoadedLog
from .quiet_launch_environment import quiet_launch_environment
from .read_until_loaded import read_until_loaded
from .stop_own_process import stop_own_process


def run_qlcplus(
    executable: str, copy: Path, qml: bool, timeout: float, quiet_period: float
) -> LoadedLog:
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
        return read_until_loaded(process, timeout, quiet_period, qml)
    finally:
        # Reaped already when loading finished; a reaped pid is not asked
        # about again, since the system may have handed it to someone else.
        if process.returncode is None:
            stop_own_process(process)
