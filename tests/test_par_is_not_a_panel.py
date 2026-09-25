"""2026-09-25, review of 4b50144..655b97d: a plain PAR with a programme is not a panel.

`is_panel` took any one-cell fixture with an internal programme that neither
pans nor tilts, so 26 one-cell modes of the upstream library, every PAR among
them, were panels and page 4 would name panels on a rig of PARs. A one-cell
fixture must now also have a panel's body (`has_panel_face`). The PAR here is
Vibra's panel definition with a PAR's `<Dimensions>`: the same channels and
programme, so only the body can tell them apart.
"""

import re
from dataclasses import replace

import pytest
from console_captions import console_captions
from panel_rig import PANEL_FILE, build_panel_patch
from rig_root import RIG_ROOT

from qlctool.capability import FixtureCapabilities
from qlctool.cli import main
from qlctool.definition import Dimensions, load_definition
from qlctool.fixture import PatchedFixture
from qlctool.is_panel import is_panel
from qlctool.names.default_names import default_names

# Upstream QLC+ library: Litecraft LED PAR 64 AT3 and Chauvet SlimPAR T6 USB.
PAR_64_AT3 = Dimensions(width=274, height=268, depth=433)
SLIMPAR_T6 = Dimensions(width=84, height=226, depth=181)


def _vibra_panel() -> FixtureCapabilities:
    definition = load_definition(RIG_ROOT / "QLC+ Fixtures" / PANEL_FILE)
    mode = next(iter(definition.modes))
    fixture = PatchedFixture(1, definition.manufacturer, definition.model, mode, 0, 0, 8, "Panel")
    return FixtureCapabilities.resolve(fixture, definition)


def test_vibra_panel_is_a_panel():
    assert is_panel(_vibra_panel())


@pytest.mark.parametrize("body", [PAR_64_AT3, SLIMPAR_T6, None])
def test_2026_09_25_a_par_body_is_not_a_panel(body):
    assert not is_panel(replace(_vibra_panel(), dimensions=body))


def test_2026_09_25_page_4_names_no_panels_on_a_rig_of_programmed_pars(tmp_path, monkeypatch):
    monkeypatch.setenv("QLCTOOL_FIXTURES", str(tmp_path / "fixtures"))
    patch = build_panel_patch(tmp_path, 7)
    definition = tmp_path / "fixtures" / PANEL_FILE
    text, count = re.subn(
        r"<Dimensions [^>]*/>",
        '<Dimensions Weight="3.5" Width="274" Height="268" Depth="433"/>',
        definition.read_text(encoding="utf-8"),
    )
    assert count == 1
    definition.write_text(text, encoding="utf-8")
    out = tmp_path / "pars.qxw"
    assert main(["newshow", str(patch), "--out", str(out)]) == 0
    names = default_names()
    captions = console_captions(out)
    assert names.render("builtins_frame", count=7) in captions
    for key in ("panels_frame", "library_2", "library_6"):
        assert names.render(key, count=7) not in captions, key
    assert names.display("matrices_frame_panels") not in captions
    assert names.display("matrices_frame") not in captions
