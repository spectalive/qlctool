"""2026-09-26: a wheel whose only nameable detent is one no look asks for is parked.

`outside_color_looks` tried every colour in `WHEEL_NAMES`, but the looks only
ask for the show's palette. A BEAM 230W 7R whose wheel names only "UV", on a
show whose palette has neither purple nor ultraviolet, counted as inside the
looks: no wheel look writes it and no intensity level parked its
`Atomization` channel, so `check` said `modo sin dueño`. The predicate now asks
over the palette the looks request (review of ecc61b5).
"""

import re
import shutil
from dataclasses import replace
from pathlib import Path

from rig_root import RIG_ROOT

from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.rule_mode_owner import RULE_ID
from qlctool.cli import main
from qlctool.color_pair import ColorPair
from qlctool.description.colour_settings import ColourSettings
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.vibra.vibra_description import vibra_description
from qlctool.workspace import Workspace

EMPTY = Path(__file__).resolve().parent / "data" / "empty-workspace.qxw"
DEFINITIONS = RIG_ROOT / "QLC+ Fixtures"
UNASKED = {"purple", "ultraviolet"}


def _uv_only_beams(folder: Path) -> Path:
    """The definitions with a BEAM 230W 7R copy whose wheel names only "UV"; the patch."""
    fixtures = folder / "fixtures"
    shutil.copytree(DEFINITIONS, fixtures)
    text = (DEFINITIONS / "BEAM-LIGHT-230W-7R.qxf").read_text(encoding="utf-8")
    text = text.replace("<Model>BEAM 230W 7R</Model>", "<Model>Beam UV Wheel</Model>")
    slots = iter(range(64))
    text = re.sub(
        r'(Preset="ColorMacro" Res1="#[0-9a-f]+">)(?!UV<)[^<]+<',
        lambda match: f"{match.group(1)}Slot {next(slots)}<",
        text,
    )
    assert ">UV<" in text and ">Red<" not in text
    (fixtures / "Generic-Beam-UV-Wheel.qxf").write_text(text, encoding="utf-8")

    empty = folder / "empty.qxw"
    shutil.copy(EMPTY, empty)
    adds, address = [], 1
    for index in range(1, 7):
        adds += ["--add", f"Vortex|PC-64 LED S|Default|0|{address}|Par {index}"]
        address += 5
    for index in range(1, 3):
        adds += ["--add", f"Generic|Beam UV Wheel|16 channel|0|{address}|Beam {index}"]
        address += 16
    groups = ["--group-new", "Pars=6x1", "--group-new", "Beams=2x1"]
    patched = folder / "patched.qxw"
    assert main(["patch", str(empty), *adds, *groups, "--out", str(patched)]) == 0
    cells = [arg for i in range(6) for arg in ("--group-add", f"0={i}@{i},0")]
    cells += [arg for i in range(6, 8) for arg in ("--group-add", f"1={i}@{i - 6},0")]
    out = folder / "patch.qxw"
    assert main(["patch", str(patched), *cells, "--out", str(out)]) == 0
    return out


def _without_unasked(colours: ColourSettings) -> ColourSettings:
    def kept(names: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(n for n in names if n not in UNASKED)

    def pairs(values: tuple[ColorPair, ...]) -> tuple[ColorPair, ...]:
        return tuple(p for p in values if not {p.lead, p.bed} & UNASKED)

    return replace(
        colours,
        palette={k: v for k, v in colours.palette.items() if k not in UNASKED},
        primary=kept(colours.primary),
        simple=kept(colours.simple),
        matrix_colors=kept(colours.matrix_colors),
        analogous_pairs=pairs(colours.analogous_pairs),
        complementary_pairs=pairs(colours.complementary_pairs),
        key_split_pairs=tuple(p for p in colours.key_split_pairs if not set(p) & UNASKED),
    )


def test_2026_09_26_a_uv_only_wheel_on_a_show_without_purple_is_parked(tmp_path, monkeypatch):
    monkeypatch.setenv("QLCTOOL_FIXTURES", str(tmp_path / "fixtures"))
    workspace = Workspace.load(_uv_only_beams(tmp_path))
    library = FixtureLibrary.load([tmp_path / "fixtures"])
    described = vibra_description()
    description = replace(described, colours=_without_unasked(described.colours), matrices={})
    build_canonical_show(workspace, library, description=description)
    findings = check_workspace(workspace, library)
    assert [f for f in findings if f.rule_id == RULE_ID] == []
