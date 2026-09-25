"""2026-09-25, Plan C final review: captions built on rigs that are neither the club nor Vibra.

The club proves a rig without gobos, prism or built-in effects; Vibra's frozen
bytes prove a rig with all of them. These two build the mixed cases, so the
captions are checked against what the generator really put in the show.
"""

from console_captions import console_captions
from gobo_spot_rig import build_gobo_spot_patch
from panel_rig import build_panel_patch

from qlctool.cli import main
from qlctool.names.default_names import default_names

PANEL_EFFECTS = 7


def test_2026_09_25_a_gobo_spot_with_no_prism_is_told_its_gobos_follow_the_tap(
    tmp_path, monkeypatch
):
    """2026-09-25, Plan C final review (finding 4): no mixed rig was built end to end.

    The spot keeps its gobo wheel and loses its prism, so the gobo animation
    is built and the prism one is not; the tempo help must say exactly that.
    """
    monkeypatch.setenv("QLCTOOL_FIXTURES", str(tmp_path / "fixtures"))
    patch = build_gobo_spot_patch(tmp_path, without=("Prism", "Prism Rotation"))
    out = tmp_path / "spots.qxw"
    assert main(["newshow", str(patch), "--out", str(out)]) == 0
    names = default_names()
    captions = console_captions(out)
    assert names.display("tempo_2_no_prism") in captions
    assert not [c for c in captions if "prism" in c.casefold()]


def test_2026_09_25_page_4_counts_the_built_in_effects_the_rig_has(tmp_path, monkeypatch):
    """2026-09-25, Plan C final review (finding 1): "the panels' 42 built-in effects".

    The count was Vibra's, written into the catalogue. Panels with seven
    programmes get seven scenes, and page 4 must say seven.
    """
    monkeypatch.setenv("QLCTOOL_FIXTURES", str(tmp_path / "fixtures"))
    patch = build_panel_patch(tmp_path, PANEL_EFFECTS)
    out = tmp_path / "panels.qxw"
    assert main(["newshow", str(patch), "--out", str(out)]) == 0
    names = default_names()
    captions = console_captions(out)
    for key in ("panels_frame", "library_2", "library_6"):
        assert names.render(key, count=PANEL_EFFECTS) in captions, key
    assert not [c for c in captions if "42" in c]
    # 2026-09-25, the owner's delegated decision: panels and no bars, so the
    # matrices frame names the panels alone.
    assert names.display("matrices_frame_panels") in captions
    # The build is Spanish: "bars" could never match (review of 655b97d). Neither
    # caption naming the bars is on the console, and no caption says "barra".
    for key in ("matrices_frame", "matrices_frame_bars"):
        assert names.display(key) not in captions, key
    assert not [c for c in captions if "barra" in c.casefold()]
