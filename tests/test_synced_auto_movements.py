"""2026-10-21: the room's moving heads share one shape and one clock."""

from rig_root import RIG_ROOT

from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.generate_movement_families import generate_movement_families
from qlctool.house_right_fixture_ids import house_right_fixture_ids
from qlctool.iter_local import iter_local
from qlctool.strip_to_skeleton import strip_to_skeleton
from qlctool.workspace import Workspace


def test_2026_10_21_auto_pairs_simultaneous_beam_and_wash_shapes():
    workspace = strip_to_skeleton(Workspace.load(RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"))
    generated = generate_movement_families(
        workspace, FixtureLibrary.load(), mirrored_ids=house_right_fixture_ids(workspace.root)
    )
    functions = {int(f.get("ID")): f for f in iter_local(workspace.root, "Function") if f.get("ID")}
    owner = functions[generated.cabezas_id]
    assert owner.get("Type") == "Collection"
    owner_steps = findall_local(owner, "Step")
    assert len(owner_steps) == 1
    chaser = functions[int(owner_steps[0].text)]
    assert chaser.get("Type") == "Chaser"
    steps = findall_local(chaser, "Step")
    assert len(steps) == 8
    assert findall_local(chaser, "RunOrder")[0].text == "Loop"
    for step in steps[:7]:
        pair = functions[int(step.text)]
        assert pair.get("Type") == "Collection"
        members = [functions[int(member.text)] for member in findall_local(pair, "Step")]
        assert len(members) == 2
        shape = pair.get("Name").removeprefix("Movimientos Cabezas ")
        assert [member.get("Name") for member in members] == [
            f"Wash {shape} Simultaneo",
            f"Beam {shape} Simultaneo",
        ]
        for member in members:
            parts = (
                [member]
                if member.get("Type") == "EFX"
                else [functions[int(part.text)] for part in findall_local(member, "Step")]
            )
            assert parts
            for part in parts:
                assert part.get("Type") == "EFX"
                assert findall_local(part, "Speed")[0].get("Duration") == "16000"
                assert all(
                    fixture.findtext("{*}StartOffset") == "0"
                    for fixture in findall_local(part, "Fixture")
                )
    cascade = functions[int(steps[-1].text)]
    assert cascade.get("Name") == "Movimientos Cabezas Cascada Beams"
    assert len(findall_local(cascade, "Step")) == 2
