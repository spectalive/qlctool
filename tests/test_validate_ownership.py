"""2026-09-26, review of round D6: validation touches only the QLC+ it started, on a copy with no I/O.

It used to hand QLC+ the workspace as it was - its DMX interface, Art-Net and
MIDI patches included - and to kill every QLC+ that appeared while it ran,
found by name. A stand-in QLC+ (a script named `qlcplus`) shows what it is
given and when it runs, so this holds where no QLC+ is installed.
"""

import os
import subprocess
import sys
import threading
import time
from pathlib import Path

from lxml import etree
from rig_root import RIG_ROOT

from qlctool.validate import validate_workspace
from qlctool.xmlutil import iter_local

VIBRA = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
STAND_IN = """#!{python}
import os, shutil, sys, time
args = sys.argv[1:]
if "-o" in args:
    shutil.copy(args[args.index("-o") + 1], os.environ["FAKE_QLC_SEEN"])
    with open(os.environ["FAKE_QLC_READY"], "w") as ready:
        ready.write(str(os.getpid()) + "\\n" + args[args.index("-o") + 1])
print("Q Light Controller Plus stand-in", flush=True)
time.sleep(60)
"""


def _stand_in(folder: Path) -> Path:
    binary = folder / "qlcplus"
    binary.write_text(STAND_IN.format(python=sys.executable))
    binary.chmod(0o755)
    return binary


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def test_qlcplus_is_given_a_copy_with_no_io(tmp_path, monkeypatch):
    monkeypatch.setenv("FAKE_QLC_SEEN", str(tmp_path / "seen.qxw"))
    monkeypatch.setenv("FAKE_QLC_READY", str(tmp_path / "ready"))
    result = validate_workspace(VIBRA, binary=str(_stand_in(tmp_path)), quiet_period=0.5)
    assert result.ok
    seen = etree.parse(str(tmp_path / "seen.qxw")).getroot()
    assert list(iter_local(seen, "Universe"))
    assert list(iter_local(etree.parse(str(VIBRA)).getroot(), "Output")), "a patch to strip"
    for io_map in iter_local(seen, "InputOutputMap"):
        assert not [e for name in ("Input", "Output", "Feedback") for e in iter_local(io_map, name)]
    given = Path((tmp_path / "ready").read_text().splitlines()[1])
    assert given.parent == VIBRA.parent, "beside the original, so relative media resolve"
    assert not given.exists(), "and removed afterwards"


def test_a_qlcplus_started_during_a_validation_survives_it(tmp_path, monkeypatch):
    monkeypatch.setenv("FAKE_QLC_SEEN", str(tmp_path / "seen.qxw"))
    ready = tmp_path / "ready"
    monkeypatch.setenv("FAKE_QLC_READY", str(ready))
    binary = _stand_in(tmp_path)
    results = []
    validation = threading.Thread(
        target=lambda: results.append(validate_workspace(VIBRA, binary=str(binary), quiet_period=3))
    )
    validation.start()
    deadline = time.monotonic() + 20
    while not ready.exists() or "\n" not in ready.read_text():
        assert time.monotonic() < deadline, "the stand-in never started"
        time.sleep(0.05)
    own = int(ready.read_text().splitlines()[0])
    # Somebody else's QLC+, started while the validation is still watching its own.
    other = subprocess.Popen([str(binary)], stdout=subprocess.DEVNULL)
    try:
        validation.join(30)
        assert results and results[0].ok
        assert not _alive(own), "validation stops the QLC+ it started"
        assert other.poll() is None, "and nothing else"
    finally:
        other.kill()
        other.wait()
