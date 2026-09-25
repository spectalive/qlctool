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
