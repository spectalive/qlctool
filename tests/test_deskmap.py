"""The tablet's map comes out of the generated show, and says what the desk needs.

Built from Vibra's own patch, including both fog types: the map is a reading
of the saved console, so it is exercised on a freshly generated one.
"""

import re

import pytest
from rig_root import RIG_ROOT

from qlctool.build_deskmap import build_deskmap
from qlctool.desk_policy import split_caption
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.speed_multiplier import multiplier
from qlctool.workspace import Workspace

REPO = RIG_ROOT
SHOW = REPO / "QLC+ Setups" / "Vibra.qxw"
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
    assert captions == [
        "AUTO",
        "CHARLA",
        "TRANQUILO",
        "FIESTA",
        "LOCURA",
        "BLANCO TOTAL",
        "TODO NEGRO",
    ]
    auto = deskmap["controls"][state["controls"][0]]
    assert auto["detail"] == "el show se lleva solo"
    assert auto["role"] == "state" and auto["action"] == "toggle" and auto["enabled"]
    assert auto["functionType"] == "Collection"
    assert all(deskmap["controls"][k]["solo"] == state["solo"] for k in state["controls"])
    assert state["solo"] is not None


def test_2026_09_13_held_accents_are_replaced_by_bounded_bursts(deskmap):
    from qlctool.desk_policy import BURST_MS

    # Hard-coded, not derived from qlctool.desk_policy.BURST_MS: two accents
    # trading durations must still fail this test even if production code
    # agrees with itself.
    expected_ms = {
        "flash": 8000,
        "flash-lento": 8000,
        "flash-color": 8000,
        "strobo": 4000,
        "strobo-suave": 4000,
        "humo-ya": 3000,
        "humo-vert": 3000,
        "rojo": 8000,
        "verde": 8000,
        "azul": 8000,
        "ultravioleta": 8000,
        "amarillo": 8000,
        "cyan": 8000,
        "magenta": 8000,
        "blanco": 8000,
        "naranja": 8000,
        "rosa": 8000,
    }

    controls = deskmap["controls"]
    bursts = {key: c for key, c in controls.items() if c["role"] == "burst"}
    assert len(bursts) == len(BURST_MS)
    assert sorted(c["burstMs"] for c in bursts.values()) == sorted(BURST_MS.values())
    assert bursts.keys() == expected_ms.keys()
    for key, control in bursts.items():
        assert control["source"] == key
        assert control["burstMs"] == expected_ms[key]
        assert control["functionType"] == "Chaser"
        assert control["action"] == "toggle" and control["enabled"]
        assert control["reason"] == ""
        assert isinstance(control["widget"], int) and isinstance(control["function"], int)
        assert control["solo"] is None and control["key"] is None
        assert control["caption"]
        if key not in ("humo-ya", "humo-vert"):
            assert control["burstNote"]
    live = _section(deskmap, "live", "accents")["controls"]
    color = _section(deskmap, "color", "accents")["controls"]
    # Seven since COLOR BEAM went: a button that looked like an on/off and
    # actually stepped the wheel (owner, 2026-09-22).
    assert len(live) == 7 and len(color) == 10
    assert "color-beam" not in controls
    assert not any(c["role"] == "accent" for c in controls.values())
    assert bursts["rojo"]["swatches"][0] == "#ff0000"


def test_safety_details_replace_words_that_would_mislead(deskmap):
    # "apaga las luces" reads as a stop; the tablet says what it is.
    assert deskmap["controls"]["todo-negro"]["detail"] == "no es parar"
    for control in deskmap["controls"].values():
        if control["role"] == "haze":
            assert control["detail"] == "dispara ya"
    assert deskmap["controls"]["humo-vertical"]["caption"] == "Luz del humo vertical"
    assert deskmap["controls"]["pares"]["caption"] == "Pares / impares"
    assert deskmap["controls"]["pares"]["detail"] == ""


def test_2026_09_22_no_tile_carries_its_glyph_inside_its_caption(deskmap):
    """The console keeps a control's glyph in the caption; the desk gets it as a
    field, so a tile can draw it at icon size. A glyph left in the caption is a
    label starting with a character the tablet cannot size or align - and it
    changes the control's key, which is how the fog light's tile disappeared
    from the map on 2026-09-22."""
    for key, control in deskmap["controls"].items():
        first = control["caption"][:1]
        assert first.isalnum() or first in "¿¡#", (key, control["caption"])
        assert control["icon"] == "" or not control["icon"].isalnum()


def test_the_haze_rhythms_are_a_solo_section(deskmap):
    haze = _section(deskmap, "live", "haze")
    assert len(haze["controls"]) == 4
    assert all(deskmap["controls"][k]["role"] == "haze" for k in haze["controls"])


def test_the_colour_family_has_hooks_then_picks_with_swatches(deskmap):
    hooks = _section(deskmap, "color", "hooks")
    picks = _section(deskmap, "color", "picks")
    # The automatic colour comes in four flavours since 2026-09-22: the whole
    # palette, the simple colours, the pastels and the multicolour wheel.
    assert [deskmap["controls"][k]["caption"] for k in hooks["controls"]][:4] == [
        "Colores completos",
        "Colores simples",
        "Pastel tenue",
        "Multicolor",
    ]
    # Seventeen solid picks - the palette minus white, which no rotation
    # steps and no pick offers since 2026-09-22 - plus the two rainbows.
    assert len(picks["controls"]) == 19
    red = next(
        deskmap["controls"][k]
        for k in picks["controls"]
        if deskmap["controls"][k]["caption"] == "Rig Rojo"
    )
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


def test_2026_09_26_the_colour_flash_tile_shows_no_swatch_of_the_smoke_columns(deskmap):
    """Round D review: Flash Color lights the lit smoke machines white, but
    its look is the running colour, not white - a smoke column never adds a
    colour a tile needs, so FLASH COLOR stays swatchless beside FLASH's white."""
    assert deskmap["controls"]["flash-color"]["swatches"] == []
    assert deskmap["controls"]["flash"]["swatches"] == ["#ffffff"]


def _by_caption(deskmap, page, section):
    controls = deskmap["controls"]
    return {
        controls[k]["caption"]: controls[k] for k in _section(deskmap, page, section)["controls"]
    }


def test_2026_09_27_a_released_pick_names_the_hook_the_desk_presses(deskmap):
    """Ruling D8, then R3a (2026-09-27 review, C-1): picks stay latched, and the
    tablet presses the frame's hook when one is released, since QLC+ 5's solo
    frame restores nothing. Which hook is the running state's: `releaseTo` maps
    the widget of each room state that starts exactly one of the frame's hooks
    to that hook's widget. AUTO starts two or three heads, gobo and prism hooks
    through its energy levels, so it has no entry there: the desk presses
    nothing and the floor holds the family.
    """
    assert deskmap["schema"] == 2
    controls = deskmap["controls"]
    by_widget = {c["widget"]: c for c in controls.values()}
    states = {c["caption"]: str(c["widget"]) for c in controls.values() if c["role"] == "state"}
    released = [c for c in controls.values() if "releaseTo" in c]
    assert released
    for control in released:
        assert control["releaseTo"] and control["action"] == "toggle"
        for state, hook in control["releaseTo"].items():
            assert by_widget[int(state)]["role"] == "state"
            assert by_widget[hook]["role"] == "hook" and by_widget[hook]["solo"] == control["solo"]
            assert hook != control["widget"]
    assert not [c for c in controls.values() if c["role"] == "state" and "releaseTo" in c]

    auto, charla, fiesta = states["AUTO"], states["CHARLA"], states["FIESTA"]
    colour_hooks = _by_caption(deskmap, "color", "hooks")
    luz_charla = next(c for caption, c in colour_hooks.items() if "Charla" in caption)["widget"]
    for pick in _by_caption(deskmap, "color", "picks").values():
        assert pick["releaseTo"][charla] == luz_charla
        assert pick["releaseTo"][auto] == colour_hooks["Colores completos"]["widget"]
    heads = {c["function"]: c["widget"] for c in _by_caption(deskmap, "heads", "hooks").values()}
    cabezas = next(
        widget
        for function, widget in heads.items()
        if by_widget[widget]["caption"] == "AUTO normal"
    )
    for page in ("heads", "gobos", "prism"):
        for pick in _by_caption(deskmap, page, "picks").values():
            assert auto not in pick["releaseTo"], page
    for pick in _by_caption(deskmap, "heads", "picks").values():
        assert pick["releaseTo"][fiesta] == cabezas


def test_2026_09_27_a_desk_hook_carries_release_only_when_the_graph_calls_it_a_pick(deskmap):
    """Review M-1: `Colores simples`, `Pastel tenue`, `Multicolor` and `Mezcla`
    sit among the tablet's colour hooks but are latched picks of the colour
    frame in the graph, so they carry `releaseTo`; the frame's graph hooks
    (`Colores completos`, `Luz Charla`) carry none.
    """
    hooks = _by_caption(deskmap, "color", "hooks")
    carrying = {caption for caption, c in hooks.items() if "releaseTo" in c}
    assert carrying == {"Colores simples", "Pastel tenue", "Multicolor", "Mezcla"}
    targets = {w for c in hooks.values() for w in c.get("releaseTo", {}).values()}
    assert all("releaseTo" not in c for c in hooks.values() if c["widget"] in targets)


def test_2026_09_27_a_state_that_starts_no_hook_of_the_frame_has_no_entry(tmp_path):
    """R3a re-injection: take `Luz Charla` out of `Momento Charla` and CHARLA
    starts no hook of the colour frame, so its key disappears from every
    colour pick's `releaseTo`.
    """
    from qlctool.xmlutil import findall_local

    workspace = Workspace.load(SHOW)
    library = FixtureLibrary.load()
    build_canonical_show(workspace, library)
    functions = {f.get("Name"): f for f in findall_local(workspace.engine, "Function")}
    moment, light = functions["Momento Charla"], functions["Luz Charla"]
    for step in findall_local(moment, "Step"):
        if step.text == light.get("ID"):
            moment.remove(step)
    out = tmp_path / "Vibra.qxw"
    workspace.save(out)
    deskmap = build_deskmap(Workspace.load(out), library, out)
    charla = next(
        str(c["widget"]) for c in deskmap["controls"].values() if c["caption"] == "CHARLA"
    )
    picks = _by_caption(deskmap, "color", "picks").values()
    assert picks and all(charla not in p["releaseTo"] for p in picks)
    assert all(len(p["releaseTo"]) == 4 for p in picks)
