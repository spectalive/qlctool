"""The small club with two gobo spots that have no colour wheel.

The spot is the BEAM 230W 7R with its colour channels taken out - the wheel,
the half-colour index and the multicolour "atomization" effect - which is what
an LED gobo spot looks like to qlctool: pan, tilt, a dimmer, a gobo wheel, a
prism, and no Color Macro. Found by the Plan C final review on 2026-09-25:
`newshow` stopped at "no fixture in this workspace has a color_macro channel".
The rest is the small club's patch (see small_rig.py), so the colour looks
have the pars and the RGB heads to fall on.
"""

import re
import shutil
from pathlib import Path

from rig_root import RIG_ROOT

from qlctool.cli import main

EMPTY = Path(__file__).resolve().parent / "data" / "empty-workspace.qxw"
DEFINITIONS = RIG_ROOT / "QLC+ Fixtures"
COLOUR_CHANNELS = ("Color Wheel", "Color Effect", "Atomization")
SPOT = "Generic|Gobo Spot No Wheel|13 channel"


def build_gobo_spot_patch(folder: Path) -> Path:
    """Write the definitions to `folder`/fixtures and the patch to `folder`; return the patch.

    The caller points QLCTOOL_FIXTURES at `folder`/fixtures before calling.
    """
    fixtures = folder / "fixtures"
    shutil.copytree(DEFINITIONS, fixtures)
    text = (DEFINITIONS / "BEAM-LIGHT-230W-7R.qxf").read_text(encoding="utf-8")
    text = text.replace("<Model>BEAM 230W 7R</Model>", "<Model>Gobo Spot No Wheel</Model>")
    for name in COLOUR_CHANNELS:
        text = re.sub(rf' <Channel Name="{name}">.*?</Channel>\n', "", text, flags=re.S)
        text = re.sub(rf'  <Channel Number="\d+">{name}</Channel>\n', "", text)
    numbers = iter(range(64))
    text = re.sub(r'<Channel Number="\d+">', lambda _: f'<Channel Number="{next(numbers)}">', text)
    text = text.replace('<Mode Name="16 channel">', '<Mode Name="13 channel">')
    assert "ColorMacro" not in text and "Multicolor" not in text
    (fixtures / "Generic-Gobo-Spot-No-Wheel.qxf").write_text(text, encoding="utf-8")

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
        adds += ["--add", f"{SPOT}|0|{address}|Spot {index}"]
        address += 13
    patched = folder / "patched.qxw"
    groups = ["--group-new", "Pars=6x1", "--group-new", "Heads=4x1", "--group-new", "Spots=2x1"]
    assert main(["patch", str(empty), *adds, *groups, "--out", str(patched)]) == 0
    cells = [arg for i in range(6) for arg in ("--group-add", f"0={i}@{i},0")]
    cells += [arg for i in range(6, 10) for arg in ("--group-add", f"1={i}@{i - 6},0")]
    cells += [arg for i in range(10, 12) for arg in ("--group-add", f"2={i}@{i - 10},0")]
    out = folder / "spot-patch.qxw"
    assert main(["patch", str(patched), *cells, "--out", str(out)]) == 0
    empty.unlink()
    patched.unlink()
    return out
