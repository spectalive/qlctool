"""Round G review, 2026-09-26: a rig `newshow` accepts is a rig that passes `check`.

The rig minimum was loosened to "one fixture group" and the reviews found,
one shape at a time, shows that failed their own check: one beam, two
panels, one fog machine. This closes the class instead of the instance:
every model and mode in the test library, one, two and four of them in one
row group. Wherever `newshow` builds a show, `check` passes it; wherever it
refuses, the refusal is the rig minimum's. Built in-process and never
loaded in QLC+, so the whole sweep stays a few seconds of the suite.
"""

from pathlib import Path

import pytest
from rig_root import RIG_ROOT
from single_shape_rig import build_single_shape_patch

from qlctool.cli import main
from qlctool.definition import load_definition
from qlctool.names.default_names import default_names

FIXTURES = RIG_ROOT / "QLC+ Fixtures"
COUNTS = (1, 2, 4)


def _shapes() -> list[tuple[str, int, int]]:
    """(patch --add spec, channel width) for every model and mode in the library."""
    shapes = []
    for qxf in sorted(FIXTURES.glob("*.qxf")):
        definition = load_definition(qxf)
        for mode, channels in definition.modes.items():
            spec = f"{definition.manufacturer}|{definition.model}|{mode}|0|{{address}}|F {{index}}"
            shapes.append((spec, len(channels)))
    return shapes


@pytest.mark.parametrize("count", COUNTS)
@pytest.mark.parametrize(("spec", "width"), _shapes(), ids=lambda value: str(value).split("|0|")[0])
def test_2026_09_26_newshow_accepts_only_what_check_passes(
    spec, width, count, tmp_path: Path, capsys
):
    patch = build_single_shape_patch(tmp_path, spec, count, width)
    show = tmp_path / "show.qxw"
    try:
        built = main(["newshow", str(patch), "--out", str(show)])
    except SystemExit as refused:
        names = default_names()
        expected = names.render(
            "rig_below_minimum", missing=names.display("rig_needs_fixture_group")
        )
        assert refused.code == expected
        assert not show.exists()
        return
    assert built == 0
    capsys.readouterr()
    assert main(["check", str(show)]) == 0, capsys.readouterr().out
