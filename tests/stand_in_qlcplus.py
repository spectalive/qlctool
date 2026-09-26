"""A script that answers to QLC+'s name, for validation tests that run without QLC+.

Named `qlcplus` it plays the 4.x build (validation waits for its log to go
quiet); named `qlcplus-qml` it plays the QML build and logs `renderPage`, the
end-of-load marker. Given `-o`, it copies the workspace it was handed to
`$FAKE_QLC_SEEN`, starts a `sleep` child when `$FAKE_QLC_CHILD` is set, and
writes its pid, that child's pid (0 for none) and the path it was given to
`$FAKE_QLC_READY`, one per line. Then it sleeps until it is killed.
"""

import sys
from pathlib import Path

SCRIPT = """#!PYTHON
import os, shutil, subprocess, sys, time
args = sys.argv[1:]
if "-o" in args:
    given = args[args.index("-o") + 1]
    if os.environ.get("FAKE_QLC_SEEN"):
        shutil.copy(given, os.environ["FAKE_QLC_SEEN"])
    child = subprocess.Popen(["sleep", "60"]) if os.environ.get("FAKE_QLC_CHILD") else None
    if os.environ.get("FAKE_QLC_READY"):
        with open(os.environ["FAKE_QLC_READY"] + ".part", "w") as ready:
            ready.write("\\n".join([str(os.getpid()), str(child.pid if child else 0), given]))
        os.rename(os.environ["FAKE_QLC_READY"] + ".part", os.environ["FAKE_QLC_READY"])
print("Q Light Controller Plus stand-in", flush=True)
if sys.argv[0].endswith("-qml"):
    print("[VC] renderPage", flush=True)
time.sleep(60)
"""


def stand_in_qlcplus(folder: Path, name: str = "qlcplus") -> Path:
    """Write the stand-in into `folder` under `name`, executable; return its path."""
    binary = folder / name
    binary.write_text(SCRIPT.replace("PYTHON", sys.executable))
    binary.chmod(0o755)
    return binary
