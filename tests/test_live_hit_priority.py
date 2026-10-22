"""2026-10-21: a live Fiesta colour wheel must not reclaim a tablet Flash."""

import json
import time
from urllib.request import urlopen

import pytest
from live_qlcplus import qml_binary, running_qlcplus
from rig_root import RIG_ROOT

pytest.importorskip("websockets")

from qlctool.build_deskmap import build_deskmap
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.mcpserver.mcp_settings import McpSettings
from qlctool.mcpserver.qlc_link import QlcLink
from qlctool.workspace import Workspace


@pytest.mark.skipif(qml_binary() is None, reason="no QLC+ 5 on this machine")
def test_2026_10_21_priority_flash_stays_white_and_expires_on_the_master(tmp_path):
    workspace = Workspace.load(RIG_ROOT / "QLC+ Setups" / "Vibra.qxw")
    library = FixtureLibrary.load()
    build_canonical_show(workspace, library)
    show = tmp_path / "Vibra.qxw"
    workspace.save(show)
    controls = build_deskmap(workspace, library, show)["controls"]
    flash = controls["flash"]["priorityWidget"]
    assert all(
        c["priorityWidget"] != c["widget"] for c in controls.values() if c["role"] == "burst"
    )

    with running_qlcplus(show, tmp_path) as port:
        with urlopen(f"http://127.0.0.1:{port}/vc.json", timeout=5) as response:
            document = json.load(response)
        if '"flashMaxHoldMs":8000' not in json.dumps(document, separators=(",", ":")):
            pytest.skip("QLC+ does not expose the bounded priority Flash extension")
        settings = McpSettings(port=port, timeout=5.0)
        for mode in ("fiesta", "locura"):
            with QlcLink(settings) as link:
                link.send(f"{controls[mode]['widget']}|255")
                time.sleep(1.0)
                link.send(f"{flash}|255")
                time.sleep(0.4)
                values = []
                for _ in range(24):
                    values.append(int(link.ask("getChannelsValues", 1, 226, 1)[1]))
                    time.sleep(0.1)
                assert values.count(4) >= 20, (mode, values)
                if mode == "locura":
                    reset_before = link.ask("getWidgetStatus", 47)
                    link.send("47|255")  # The reset strip shares Scene 2.
                    assert link.ask("getWidgetStatus", 47) == reset_before
                    assert link.ask("getChannelsValues", 1, 226, 1)[1] == "4"
                    link.send(f"{flash}|0")
            if mode == "fiesta":
                time.sleep(5.5)
                with QlcLink(settings) as link:
                    assert link.ask("getWidgetStatus", flash)[-1] == "0"
                    resumed = []
                    for _ in range(12):
                        resumed.append(int(link.ask("getChannelsValues", 1, 226, 1)[1]))
                        time.sleep(0.1)
                    assert any(value != 4 for value in resumed), resumed
