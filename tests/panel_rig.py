"""The small club with two pixel panels whose own programme list is short.

The panel is the HYULIGHTS WX-60WPS with its "Auto Mode" list cut to
`effects` programmes, so the show builds that many built-in effect scenes
rather than Vibra's 42. Found by the Plan C final review on 2026-09-25: page
4 said "the panels' 42 built-in effects" on every rig with built-in effects.
The rest is the small club's patch (see small_rig.py).
"""

import re
import shutil
from pathlib import Path

from rig_root import RIG_ROOT

from qlctool.cli import main

EMPTY = Path(__file__).resolve().parent / "data" / "empty-workspace.qxw"
DEFINITIONS = RIG_ROOT / "QLC+ Fixtures"
PANEL_FILE = "HYULIGHTS-WX-60WPS-48PARTITION.qxf"
PANEL = "HYULIGHTS|WX-60WPS-48PARTITION|A MODE - DMX 8 CH"


def build_panel_patch(folder: Path, effects: int) -> Path:
    """Write the definitions to `folder`/fixtures and the patch to `folder`; return the patch.

    The caller points QLCTOOL_FIXTURES at `folder`/fixtures before calling.
    """
    fixtures = folder / "fixtures"
    shutil.copytree(DEFINITIONS, fixtures)
    text = (fixtures / PANEL_FILE).read_text(encoding="utf-8")
    text = re.sub(
        r'  <Capability Min="\d+" Max="\d+">Effect (\d+)</Capability>\n',
        lambda match: "" if int(match.group(1)) > effects else match.group(0),
        text,
    )
    (fixtures / PANEL_FILE).write_text(text, encoding="utf-8")

    empty = folder / "empty.qxw"
    shutil.copy(EMPTY, empty)
    adds, address = [], 1
    for index in range(1, 7):
        adds += ["--add", f"Vortex|PC-64 LED S|Default|0|{address}|Par {index}"]
        address += 5
    for index in range(1, 3):
        adds += ["--add", f"LED Beam|Mini Led Moving Head|16 Channels|0|{address}|Beam {index}"]
        address += 16
    for index in range(1, 3):
        adds += ["--add", f"Chauvet|MiN Wash|13 Channel|0|{address}|Wash {index}"]
        address += 13
    for index in range(1, 3):
        adds += ["--add", f"{PANEL}|0|{address}|Panel {index}"]
        address += 8
    patched = folder / "patched.qxw"
    groups = ["--group-new", "Pars=6x1", "--group-new", "Heads=4x1", "--group-new", "Panels=2x1"]
    assert main(["patch", str(empty), *adds, *groups, "--out", str(patched)]) == 0
    cells = [arg for i in range(6) for arg in ("--group-add", f"0={i}@{i},0")]
    cells += [arg for i in range(6, 10) for arg in ("--group-add", f"1={i}@{i - 6},0")]
    cells += [arg for i in range(10, 12) for arg in ("--group-add", f"2={i}@{i - 10},0")]
    out = folder / "panel-patch.qxw"
    assert main(["patch", str(patched), *cells, "--out", str(out)]) == 0
    empty.unlink()
    patched.unlink()
    return out
