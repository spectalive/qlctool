"""2026-09-25: a head no colour look reaches still has its Effect channel parked.

Seen building the gobo-spot regression rig: a BEAM 230W 7R with only its colour
wheel channels stripped keeps `Atomization` (Effect group), and `check` said
`modo sin dueño` - `mode_park_pairs` was only called from the colour looks,
which never touch a fixture with no RGB and no colour wheel. The rig used to
strip that channel too, to hide it; it keeps it now, and the intensity levels
that light such a head park it.
"""

from gobo_spot_rig import build_gobo_spot_patch

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.rule_mode_owner import RULE
from qlctool.checks.run import check_workspace
from qlctool.cli import main
from qlctool.library import FixtureLibrary
from qlctool.outside_color_looks import outside_color_looks
from qlctool.workspace import Workspace


def test_2026_09_25_a_gobo_spot_without_colour_has_its_effect_channel_owned(tmp_path, monkeypatch):
    monkeypatch.setenv("QLCTOOL_FIXTURES", str(tmp_path / "fixtures"))
    patch = build_gobo_spot_patch(tmp_path)
    out = tmp_path / "spots.qxw"
    assert main(["newshow", str(patch), "--out", str(out)]) == 0

    library = FixtureLibrary.load([tmp_path / "fixtures"])
    workspace = Workspace.load(out)
    spots = [
        capability
        for capability in capabilities_of(workspace.root, library)
        if outside_color_looks(capability)
    ]
    # The case is really there: two heads with no colour and an Effect channel.
    assert len(spots) == 2
    assert all(capability.offsets_for_role(roles.EFFECT) for capability in spots)
    findings = check_workspace(workspace, library)
    assert [f for f in findings if f.rule == RULE] == []


def test_2026_09_25_a_wheel_whose_positions_name_no_colour_is_outside_the_looks():
    """2026-09-25, review of the gobo-spot fix: a colour wheel counted as "a
    colour look parks it", but a wheel whose positions name nothing the wheel
    looks know (`WHEEL_NAMES`) is written by no look. A 7R's wheel is renamed
    position by position; it is then outside the looks, as the spot is.
    """
    import dataclasses

    from rig_root import RIG_ROOT

    shipped = Workspace.load(RIG_ROOT / "QLC+ Setups" / "Vibra.qxw")
    beam = next(
        capability
        for capability in capabilities_of(shipped.root, FixtureLibrary.load())
        if capability.has_role(roles.GOBO) and capability.has_role(roles.COLOR_MACRO)
    )
    assert not outside_color_looks(beam)
    offset, positions = beam.wheel_for_role(roles.COLOR_MACRO)
    renamed = list(beam.capabilities_by_offset)
    renamed[offset] = tuple(
        dataclasses.replace(position, name=f"Slot {index}")
        for index, position in enumerate(positions)
    )
    assert outside_color_looks(dataclasses.replace(beam, capabilities_by_offset=renamed))
