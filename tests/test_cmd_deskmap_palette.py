"""The public deskmap command ships the expanded rig palette unchanged."""

from rig_root import RIG_ROOT

from qlctool.cli import main


def test_2026_10_21_deskmap_cli_exports_the_colour_hits(tmp_path):
    show = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
    description = RIG_ROOT / "QLC+ Setups" / "vibra.toml"
    shipped = RIG_ROOT / "QLC+ Setups" / "Vibra.desk.json"
    out = tmp_path / "Vibra.desk.json"

    assert main(["deskmap", str(show), "--description", str(description), "--out", str(out)]) == 0
    assert out.read_bytes() == shipped.read_bytes()
    assert b'"rig-rosa"' in out.read_bytes()
    assert b'"rosa"' in out.read_bytes()
