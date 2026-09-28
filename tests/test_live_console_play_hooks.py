"""The JUGAR play page: each family solo, its state hooks first, its picks isolated.

Split by topic out of the original `test_live_console.py` (over the codeality
test-file line cap).
"""

import pytest
from buttons_of import buttons_of as _buttons
from console_frame_of import console_frame_of as _console_frame
from frame_named import frame_named as _frame_named
from function_id_of import function_id_of as _function_id
from functions_by_id_of_root import functions_by_id_of_root as _functions_by_id
from members_of_functions import members_of as _members
from rig_root import RIG_ROOT
from walk_widgets import walk_widgets as _walk

from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.generate.console_layout import BIG_FONT, ROOM_STATES
from qlctool.leading_glyph import leading_glyph
from qlctool.localname import localname
from qlctool.names.default_names import default_names
from qlctool.workspace import Workspace

REPO = RIG_ROOT
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


@pytest.fixture(scope="module")
def console(tmp_path_factory):
    ws = Workspace.load(SHOW)
    build_canonical_show(ws, FixtureLibrary.load())
    out = tmp_path_factory.mktemp("console") / "Vibra.qxw"
    ws.save(out)
    root = Workspace.load(out).root
    return root, find_local(find_local(root, "VirtualConsole"), "Frame")


def _fixture_ids(function):
    return {value.attrib["ID"] for value in findall_local(function, "FixtureVal")}


def test_the_play_page_and_gobo_picker_declare_their_pages(console):
    """2026-09-02: JUGAR is page two and gobos remain legible on two inner pages."""
    _, outer = console
    console_frame = _console_frame(outer)

    play_labels = [
        widget
        for widget in console_frame
        if localname(widget) == "Label" and widget.attrib.get("Caption", "").startswith("2 · JUGAR")
    ]
    assert len(play_labels) == 1
    assert play_labels[0].attrib.get("Page") == "1"

    gobos = _frame_named(outer, "GOBOS")
    inner = next(
        child
        for child in gobos
        if localname(child) == "Frame" and find_local(child, "Multipage") is not None
    )
    assert find_local(inner, "Multipage").attrib["PagesNum"] == "2"

    strip = _frame_named(outer, "VOLVER AL SHOW")
    assert localname(strip) == "Frame"


def test_every_play_family_is_solo_and_starts_with_its_hooks(console):
    """2026-09-02: each family has every state owner before any manual pick."""
    root, outer = console
    functions = _functions_by_id(root)
    expected = {
        "COLOR": (
            ("Rueda Colores", "Colores completos · W"),
            ("Rueda Simples", "Colores simples · C"),
            ("Rueda Pastel", "Pastel tenue · L"),
            ("Rueda Multicolor", "Multicolor · R"),
            ("Rueda Mezcla", "Mezcla · E"),
            ("Luz Charla", "Luz Charla"),
        ),
        "PIXELES": (
            ("Ciclo Paneles Mixto", "AUTO paneles"),
            ("Paneles Charla", "Paneles Charla"),
        ),
        "CABEZAS": (
            ("Movimientos Suaves", "AUTO lento"),
            ("Movimientos Cabezas", "AUTO normal · A"),
            ("Movimientos Rapidos", "AUTO rapido"),
            ("Cabezas Centro", "Centro"),
        ),
        "GOBOS": (("Gobo Animacion", "AUTO gobos · G"), ("Gobo Reposo", "Reposo")),
        "PRISMA": (("Prisma Animacion", "AUTO prisma · P"), ("Prisma Reposo", "Reposo")),
    }
    for caption, hooks in expected.items():
        family = _frame_named(outer, caption)
        assert localname(family) == "SoloFrame"
        buttons = _buttons(family)
        names = [functions[_function_id(button)].attrib["Name"] for button in buttons]
        assert names[: len(hooks)] == [name for name, _ in hooks], caption
        assert [leading_glyph(button.attrib["Caption"])[1] for button in buttons[: len(hooks)]] == [
            hook_caption for _, hook_caption in hooks
        ]
        for hook in buttons[: len(hooks)]:
            appearance = find_local(hook, "Appearance")
            assert find_local(appearance, "Font").text == BIG_FONT
            assert find_local(appearance, "BackgroundColor").text != "Default"


def test_the_play_hooks_restore_their_global_keys_and_captions(console):
    """2026-09-02: the operator's JUGAR shortcuts are exact.

    Ten since 2026-09-22: the automatic colour split into the whole palette,
    the simple colours and the pastels, which the owner asked for by name -
    and the multicolour wheel the same evening, "solo por si acaso".
    """
    root, outer = console
    functions = _functions_by_id(root)
    expected = {
        "Rueda Colores": ("Colores completos · W", "W"),
        "Rueda Simples": ("Colores simples · C", "C"),
        "Rueda Pastel": ("Pastel tenue · L", "L"),
        "Rueda Multicolor": ("Multicolor · R", "R"),
        "Rueda Mezcla": ("Mezcla · E", "E"),
        "Movimientos Cabezas": ("AUTO normal · A", "A"),
        "Gobo Animacion": ("AUTO gobos · G", "G"),
        "Prisma Animacion": ("AUTO prisma · P", "P"),
        "Arcoiris Simultaneo": ("Arcoiris junto · '", "'"),
        "Arcoiris Pasos": ("Arcoiris fases · ¡", "¡"),
    }
    actual = {}
    play_widgets = [child for child in _console_frame(outer) if child.get("Page") == "1"]
    for button in [button for widget in play_widgets for button in _buttons(widget)]:
        function = functions[_function_id(button)]
        name = function.attrib["Name"].removeprefix("Jugar · ")
        if name in expected:
            actual[name] = (
                leading_glyph(button.attrib["Caption"])[1],
                find_local(button, "Key").text,
            )
    assert actual == expected


def test_the_play_page_carries_the_exact_operator_guidance(console):
    """2026-09-02: recovery instructions must be readable on the page itself."""
    _, outer = console
    labels = [
        widget.attrib.get("Caption", "")
        for widget, _, _ in _walk(outer)
        if localname(widget) == "Label"
    ]
    assert labels.count("Volver del todo: AUTO dos veces si ya esta verde, o Backspace y Q.") == 1
    assert (
        labels.count(
            "Pick fijo; repetirlo lo para y deja la familia quieta. AUTO colores o "
            "Q/F1-F4 devuelve la rueda; pararla corta su fundido de 800 ms."
        )
        == 1
    )
    assert (
        labels.count(
            "Bajo AUTO, el ciclo de energia lo recupera en su siguiente paso "
            "(8 min como mucho); para jugar largo pon antes un Momento."
        )
        == 3
    )


def test_no_play_pick_is_reachable_from_a_room_state(console):
    """2026-09-02: state starts release picks through hooks, never start the picks."""
    root, outer = console
    functions = _functions_by_id(root)
    ids_by_name = {
        function.attrib["Name"]: function_id for function_id, function in functions.items()
    }
    reachable = set()
    members = _members(root)
    for state, _, _, _ in ROOM_STATES:
        state_id = ids_by_name[default_names().display(state)]
        reachable.add(state_id)
        reachable.update(members.get(state_id, set()))

    hook_names = {
        "Rueda Colores",
        "Rueda Simples",
        "Rueda Pastel",
        "Rueda Multicolor",
        "Rueda Mezcla",
        "Luz Charla",
        "Ciclo Paneles Mixto",
        "Paneles Charla",
        "Movimientos Suaves",
        "Movimientos Cabezas",
        "Movimientos Rapidos",
        "Cabezas Centro",
        "Gobo Animacion",
        "Gobo Reposo",
        "Prisma Animacion",
        "Prisma Reposo",
    }
    for caption in ("COLOR", "PIXELES", "CABEZAS", "GOBOS", "PRISMA"):
        family = _frame_named(outer, caption)
        for pick in _buttons(family):
            function_id = _function_id(pick)
            if functions[function_id].attrib["Name"] in hook_names:
                continue
            assert function_id not in reachable, functions[function_id].attrib["Name"]


def test_every_play_pick_is_a_one_member_family_wrapper(console):
    """2026-09-02: picks monitor isolated wrappers, never state-owned leaves."""
    root, outer = console
    functions = _functions_by_id(root)
    hooks_per_family = {
        "COLOR": 6,  # 2026-09-22: four colour modes, the mix, and Luz Charla
        "PIXELES": 2,
        "CABEZAS": 4,
        "GOBOS": 2,
        "PRISMA": 2,
    }
    paths = {
        "COLOR": "Jugar/Color",
        "PIXELES": "Jugar/Pixeles",
        "CABEZAS": "Jugar/Cabezas",
        "GOBOS": "Jugar/Gobos",
        "PRISMA": "Jugar/Prisma",
    }
    for caption, hook_count in hooks_per_family.items():
        picks = _buttons(_frame_named(outer, caption))[hook_count:]
        assert picks
        for pick in picks:
            function = functions[_function_id(pick)]
            assert function.attrib["Type"] == "Collection"
            assert function.attrib["Path"] == paths[caption]
            # 2026-09-26, ruling D7: a beam-only look also holds the washes -
            # a Scene on heads the pick itself leaves alone (review, 2026-09-27).
            steps = [functions[int(step.text)] for step in findall_local(function, "Step")]
            for companion in steps[1:]:
                assert caption == "CABEZAS"
                assert companion.attrib["Type"] == "Scene"
                held = _fixture_ids(companion)
                assert held and not held & _fixture_ids(steps[0])
