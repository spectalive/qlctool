"""Ruling B7: a hit button's caption must name its own hit to the desk (2026-09-26).

Final review of Plan B, 2026-09-25: `[names.en] hit_button_flash = "BANG ·
Space"` loaded, and the build failed deep in the desk bursts with "burst
duration must be positive: bang", naming nothing the user wrote. The review of
round D1 then found the first refusal asking its own question instead of the
desk's: `hit_flash = "Red"` with `"Red · Space"` passed although "Red" is also
a colour, so the desk could not tell which it meant, and a leading glyph was
refused although the desk drops it.
"""

from dataclasses import replace

import pytest
from rig_root import RIG_ROOT

from qlctool.build_deskmap import build_deskmap
from qlctool.description.description_names import description_names
from qlctool.description.load_show_description import load_show_description
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.vibra.vibra_description import vibra_description
from qlctool.workspace import Workspace

SHOW = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"


def _load(tmp_path, names: str):
    path = tmp_path / "show.toml"
    path.write_text(
        '[show]\nlanguage = "en"\n[rig]\nworkspace = "Vibra.qxw"\n[names.en]\n' + names,
        encoding="utf-8",
    )
    return load_show_description(path, Workspace.load(SHOW).root)


@pytest.mark.parametrize(
    "names",
    [
        'hit_button_flash = "BANG · Space"\n',
        'hit_flash = "Red"\nhit_button_flash = "Red · Space"\n',
    ],
    ids=["button", "also-a-colour"],
)
def test_a_hit_button_the_desk_cannot_trace_to_its_hit_is_refused(tmp_path, names):
    with pytest.raises(
        ValueError, match=r"\[names\.en\] hit_\w+ = .* the desk cannot find the hit hit_flash"
    ):
        _load(tmp_path, names)


# A caption renamed alone still traces: the shipped "FLASH" stays one of
# hit_flash's spellings, and the desk looks up every spelling (checked by
# building the desk, 2026-09-26).
@pytest.mark.parametrize(
    "names",
    [
        'hit_button_flash = "Flash · Space"\n',
        'hit_button_flash = "⚡ FLASH · Space"\n',
        'hit_flash = "BANG"\n',
    ],
    ids=["respelled", "leading-glyph", "caption-alone"],
)
def test_a_hit_button_the_desk_still_traces_is_accepted(tmp_path, names):
    assert _load(tmp_path, names).names["en"]


def test_a_hit_renamed_with_its_button_builds_its_desk_burst(tmp_path):
    loaded = _load(tmp_path, 'hit_flash = "BANG"\nhit_button_flash = "BANG · Space"\n')
    workspace = Workspace.load(SHOW)
    library = FixtureLibrary.load()
    description = replace(vibra_description(), language="en", names=loaded.names)
    build_canonical_show(workspace, library, description=description)
    deskmap = build_deskmap(workspace, library, "unsaved.qxw", names=description_names(loaded))
    bursts = {c["caption"] for c in deskmap["controls"].values() if c["role"] == "burst"}
    assert "BANG" in bursts
