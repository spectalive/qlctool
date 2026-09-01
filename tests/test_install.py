"""`qlctool install`: QLC+ runs on copies, and a stale copy fails silently.

On 2026-09-01 four of the eleven definitions installed on the author's Mac
were behind the repo - the BEAM's blade ranges, the fog machine's pump group,
the MAC WASH's three heads - and every `--validate` for a week had validated
against them. The plan has to see a missing copy, a stale one, and nothing
else; the copy has to leave the folder in sync.
"""

import shutil
from pathlib import Path

from qlctool.apply_install import apply_install
from qlctool.install_item import MISSING, STALE, SYNCED
from qlctool.install_plan import install_plan

REPO = Path(__file__).resolve().parents[3]


def _fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "QLC+ Fixtures").mkdir(parents=True)
    (repo / "QLC+ InputProfiles").mkdir()
    (repo / "QLC+ Setups" / "Gobos" / "BEAM-LIGHT-230W-7R").mkdir(parents=True)
    shutil.copy(REPO / "QLC+ Fixtures" / "BEAM-LIGHT-230W-7R.qxf", repo / "QLC+ Fixtures")
    shutil.copy(REPO / "QLC+ Fixtures" / "Vortex-PC-64-LED-S.qxf", repo / "QLC+ Fixtures")
    shutil.copy(REPO / "QLC+ InputProfiles" / "M-VAVE-SMC-PAD.qxi", repo / "QLC+ InputProfiles")
    (repo / "QLC+ Setups" / "Gobos" / "BEAM-LIGHT-230W-7R" / "Gobo1.png").write_bytes(b"png")
    (repo / "QLC+ Setups" / "Gobos" / "BEAM-LIGHT-230W-7R" / "Unreferenced.png").write_bytes(b"x")
    return repo


def test_plan_sees_missing_stale_and_synced(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    user = tmp_path / "user"
    gobos = tmp_path / "bundle-gobos"
    (user / "Fixtures").mkdir(parents=True)
    shutil.copy(repo / "QLC+ Fixtures" / "Vortex-PC-64-LED-S.qxf", user / "Fixtures")
    (user / "Fixtures" / "BEAM-LIGHT-230W-7R.qxf").write_text("<old/>")

    plan = {item.source.name: item for item in install_plan(repo, user, gobos)}

    assert plan["Vortex-PC-64-LED-S.qxf"].state == SYNCED
    assert plan["BEAM-LIGHT-230W-7R.qxf"].state == STALE
    assert plan["M-VAVE-SMC-PAD.qxi"].state == MISSING
    assert plan["M-VAVE-SMC-PAD.qxi"].destination == user / "InputProfiles" / "M-VAVE-SMC-PAD.qxi"
    # A gobo lands under the folder the definition's Res1 names, not the
    # repo folder's name; an image no definition refers to is not shipped.
    assert plan["Gobo1.png"].destination == gobos / "BEAM-230W-7R" / "Gobo1.png"
    assert "Unreferenced.png" not in plan


def test_apply_copies_only_what_is_behind_and_leaves_it_in_sync(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    user = tmp_path / "user"
    gobos = tmp_path / "bundle-gobos"
    (user / "Fixtures").mkdir(parents=True)
    shutil.copy(repo / "QLC+ Fixtures" / "Vortex-PC-64-LED-S.qxf", user / "Fixtures")

    copied = apply_install(install_plan(repo, user, gobos))

    assert sorted(item.source.name for item in copied) == [
        "BEAM-LIGHT-230W-7R.qxf",
        "Gobo1.png",
        "M-VAVE-SMC-PAD.qxi",
    ]
    assert all(item.state == SYNCED for item in install_plan(repo, user, gobos))


def test_no_qlcplus_means_no_gobo_items(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    assert all(item.source.suffix != ".png" for item in install_plan(repo, tmp_path / "user", None))
