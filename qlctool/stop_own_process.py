"""Stop the one QLC+ validation started, and nothing else.

2026-09-26, review of round D6: validation used to kill every QLC+ that
appeared while it ran, found by name - an operator's QLC+ (re)started in that
window died with it. Now the only processes signalled are the child this call
spawned and, should a wrapper script have started QLC+ under it, that child's
own children, found by parent pid. Never by name.
"""

import subprocess
from typing import Any


def stop_own_process(process: "subprocess.Popen[Any]") -> None:
    """Kill `process` and its direct children, and reap it."""
    children = subprocess.run(
        ["pgrep", "-P", str(process.pid)], capture_output=True, text=True, check=False
    )
    for pid in children.stdout.split():
        subprocess.run(["kill", "-9", pid], capture_output=True, check=False)
    if process.poll() is None:
        process.kill()
    process.wait()
