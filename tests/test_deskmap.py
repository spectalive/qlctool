"""The tablet's map comes out of the generated show, and says what the desk needs.

Built from the reference patch the way the console tests do: the map is a
reading of the saved console, so it is exercised on a freshly generated one.
"""

import re
from pathlib import Path

import pytest

from qlctool.deskmap import build_deskmap
from qlctool.desk_policy import split_caption
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.speed_multiplier import multiplier
from qlctool.workspace import Workspace

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"
SWATCH = re.compile(r"^#[0-9a-f]{6}$")


@pytest.fixture(scope="module")
def deskmap(tmp_path_factory):
    workspace = Workspace.load(SHOW)
    library = FixtureLibrary.load()
    build_canonical_show(workspace, library)
    out = tmp_path_factory.mktemp("desk") / "Vibra.qxw"
    workspace.save(out)
    return build_deskmap(Workspace.load(out), library, out)


def _section(deskmap, page_key, section_key):
    page = next(p for p in deskmap["pages"] if p["key"] == page_key)
    return next(s for s in page["sections"] if s["key"] == section_key)


def test_the_map_names_the_show_and_its_two_global_controls(deskmap):
    assert deskmap["schema"] == 2
    assert deskmap["qlcVersion"] == "5.2.2"
    assert re.fullmatch(r"[0-9a-f]{64}", deskmap["show"]["sha256"])
    assert deskmap["show"]["workspace"] == "Vibra.qxw"
    assert deskmap["stopAll"]["fadeOutMs"] == 1000
    assert isinstance(deskmap["stopAll"]["widget"], int)
    assert isinstance(deskmap["grandMaster"]["widget"], int)


def test_the_room_states_are_the_first_thing_on_live(deskmap):
    state = _section(deskmap, "live", "state")
    captions = [deskmap["controls"][k]["caption"] for k in state["controls"]]
    assert captions == ["AUTO", "CHARLA", "TRANQUILO", "FIESTA", "LOCURA", "BLANCO TOTAL", "TODO NEGRO"]
    auto = deskmap["controls"][state["controls"][0]]
    assert auto["detail"] == "el show se lleva solo"
    assert auto["role"] == "state" and auto["action"] == "toggle" and auto["enabled"]
    assert auto["functionType"] == "Collection"
    assert all(deskmap["controls"][k]["solo"] == state["solo"] for k in state["controls"])
    assert state["solo"] is not None


def test_the_held_hits_are_carried_disabled(deskmap):
    accents = _section(deskmap, "live", "accents")
    held = [deskmap["controls"][k] for k in accents["controls"] if deskmap["controls"][k]["action"] == "flash"]
    assert len(held) >= 6
    for control in held:
        assert control["role"] == "accent" and not control["enabled"] and control["reason"]
    toggles = [deskmap["controls"][k] for k in accents["controls"] if deskmap["controls"][k]["action"] == "toggle"]
    assert [t["caption"] for t in toggles] == ["COLOR BEAM"]
    assert toggles[0]["enabled"]


def test_safety_details_replace_words_that_would_mislead(deskmap):
    # "apaga las luces" reads as a stop; the tablet says what it is.
    assert deskmap["controls"]["todo-negro"]["detail"] == "look a negro, no un stop"
    for control in deskmap["controls"].values():
        if control["role"] == "haze":
            assert control["detail"] == "dispara ya"


def test_the_haze_rhythms_are_a_solo_section(deskmap):
    haze = _section(deskmap, "live", "haze")
    assert len(haze["controls"]) == 4
    assert all(deskmap["controls"][k]["role"] == "haze" for k in haze["controls"])


def test_the_colour_family_has_hooks_then_picks_with_swatches(deskmap):
    hooks = _section(deskmap, "color", "hooks")
    picks = _section(deskmap, "color", "picks")
    assert [deskmap["controls"][k]["caption"] for k in hooks["controls"]][:2] == ["AUTO colores", "Mezcla"]
    assert len(picks["controls"]) >= 20
    red = next(deskmap["controls"][k] for k in picks["controls"] if deskmap["controls"][k]["caption"] == "Rig Rojo")
    assert red["role"] == "pick" and red["functionType"] == "Collection"
    assert red["swatches"] and all(SWATCH.match(s) for s in red["swatches"])
    assert red["swatches"][0].startswith("#ff")
    assert hooks["solo"] == picks["solo"] is not None


def test_every_family_and_the_control_page_are_present(deskmap):
    keys = [p["key"] for p in deskmap["pages"]]
    assert keys == ["live", "color", "pixels", "heads", "gobos", "prism", "control"]
    assert len(_section(deskmap, "gobos", "picks")["controls"]) >= 20
    chases = _section(deskmap, "control", "chases")
    assert len(chases["controls"]) == 4
    assert all(deskmap["controls"][k]["role"] == "chase" for k in chases["controls"])


def test_no_widget_appears_twice_and_no_flash_is_enabled(deskmap):
    widgets = [c["widget"] for c in deskmap["controls"].values()]
    assert len(widgets) == len(set(widgets))
    assert not [c for c in deskmap["controls"].values() if c["action"] == "flash" and c["enabled"]]


def test_the_dials_carry_the_real_enum(deskmap):
    tempo = next(d for d in deskmap["dials"].values() if d["caption"] == "Tempo Show")
    assert tempo["timeMs"] > 0 and tempo["members"]
    member = tempo["members"][0]
    assert member["duration"]["raw"] in range(11)
    assert member["fadeIn"]["name"] == "None" and member["fadeIn"]["factor"] is None


def test_the_multiplier_table():
    assert multiplier(0) == {"raw": 0, "name": "None", "factor": None}
    assert multiplier(1)["factor"] == 0.0
    assert multiplier(2)["factor"] == 0.062
    assert multiplier(6)["factor"] == 1.0
    assert multiplier(10) == {"raw": 10, "name": "16", "factor": 16.0}
    with pytest.raises(ValueError):
        multiplier(11)


def test_captions_split_into_name_and_explanation():
    assert split_caption("AUTO — el show se lleva solo · Q") == ("AUTO", "el show se lleva solo")
    assert split_caption("AUTO colores · W") == ("AUTO colores", "")
    assert split_caption("Rig Rojo") == ("Rig Rojo", "")
    assert split_caption("HUMO cada 1 min · J") == ("HUMO cada 1 min", "")
    assert split_caption("Cabezas Rojo / Resto Azul") == ("Cabezas Rojo", "Resto Azul")


def test_sections_put_the_held_hits_last():
    from qlctool.desk_policy import SECTION_ORDER
    assert SECTION_ORDER[-1] == "accents" and SECTION_ORDER[0] == "state"
