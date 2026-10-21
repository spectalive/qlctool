"""The stage-plot command exposes the fixture aim used by the 3D review."""

from rig_root import RIG_ROOT

from qlctool.cli import main
from qlctool.workspace import Workspace


def test_2026_10_21_stage_plot_cli_reports_beam_landings(tmp_path, capsys):
    show = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
    plot = RIG_ROOT / "QLC+ Setups" / "vibra-stage-plot.json"
    out = tmp_path / "stage.qxw"

    assert main(["stage", str(show), "--plot", str(plot), "--out", str(out)]) == 0
    assert Workspace.load(out).root is not None
    report = capsys.readouterr().out
    assert "25 fixtures rigged" in report
    assert "floor at" in report
