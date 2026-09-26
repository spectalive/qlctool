"""2026-09-26 (ruling D-R2): the SMC-PAD LED bridge's palette is written by the toolkit.

The bridge hard-coded Vibra's pad colours in Swift, and the show's repository
compared that array with `FUNCTION_COLORS` and `SMC_PAD_BINDINGS` pad by pad.
`qlctool pad-palette` writes the palette from the saved workspace instead; this
holds it to exactly what that comparison asserted, derived from the toolkit's
own tables.
"""

import hashlib
import json
from pathlib import Path

import pytest
from rig_root import RIG_ROOT

from qlctool.build_pad_palette import FREE_PAD, build_pad_palette
from qlctool.cli import main
from qlctool.generate.smc_pad_bindings import SMC_PAD_BINDINGS
from qlctool.generate.smc_pad_colors import FUNCTION_COLORS
from qlctool.generate.smc_pad_device import PADS
from qlctool.workspace import Workspace

SHOW = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
CLUB = Path(__file__).resolve().parents[1] / "examples" / "small-club" / "club.qxw"


@pytest.fixture(scope="module")
def palette():
    return build_pad_palette(Workspace.load(SHOW), SHOW)


def test_every_coloured_function_lights_its_own_pad(palette):
    by_channel = {pad["channel"]: pad for pad in palette["pads"]}
    for name, colour in FUNCTION_COLORS.items():
        pad = by_channel[SMC_PAD_BINDINGS[name]]
        assert pad["control"] == name
        assert pad["active"] == list(colour), f"{name} on bank {pad['bank']} pad {pad['pad']}"
        assert pad["idle"] == [c // 6 for c in colour]
        assert pad["widgets"], f"{name} is lit but no widget listens on its pad"


def test_the_pads_with_no_function_stay_faint(palette):
    """A lit pad that does nothing is a pad somebody will press."""
    coloured = {SMC_PAD_BINDINGS[name] for name in FUNCTION_COLORS}
    assert len(palette["pads"]) == 2 * PADS
    for pad in palette["pads"]:
        if pad["channel"] not in coloured:
            assert pad["control"] is None
            assert pad["active"] == list(FREE_PAD), f"bank {pad['bank']} pad {pad['pad']}"


def test_the_pads_are_the_bridge_notes_in_order(palette):
    assert [pad["note"] for pad in palette["pads"]] == list(range(36, 36 + 2 * PADS))
    assert [(p["bank"], p["pad"]) for p in palette["pads"][:2]] == [(1, 1), (1, 2)]
    assert (palette["pads"][16]["bank"], palette["pads"][16]["pad"]) == (2, 1)


def test_the_file_names_its_workspace_and_is_deterministic(tmp_path, capsys):
    out = tmp_path / "Vibra.pads.json"
    assert main(["pad-palette", "--out", str(out), str(SHOW)]) == 0
    text = out.read_text(encoding="utf-8")
    written = json.loads(text)
    assert written["format"] == 1
    assert written["show"]["workspace"] == "Vibra.qxw"
    assert written["show"]["sha256"] == hashlib.sha256(SHOW.read_bytes()).hexdigest()
    assert text == json.dumps(written, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    assert "32 pads, 22 lit" in capsys.readouterr().out
    again = tmp_path / "again.json"
    main(["pad-palette", "--out", str(again), str(SHOW)])
    assert again.read_bytes() == out.read_bytes()


def test_a_rig_with_no_pad_writes_no_pads():
    """The small club binds nothing to any input: an empty list, not an error."""
    assert build_pad_palette(Workspace.load(CLUB), CLUB)["pads"] == []
