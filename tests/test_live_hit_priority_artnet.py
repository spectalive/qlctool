"""2026-10-21: the actual Art-Net stream must keep every 7R white during Flash."""

import json
import socket
import time
from urllib.request import urlopen

import pytest
from artnet_wheels import artnet_wheels
from live_qlcplus import qml_binary, running_qlcplus
from rig_root import RIG_ROOT

pytest.importorskip("websockets")
from websockets.sync.client import connect


@pytest.mark.skipif(qml_binary() is None, reason="no QLC+ 5 on this machine")
def test_2026_10_21_artnet_keeps_all_7r_white_until_the_master_timeout(tmp_path):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
        try:
            receiver.bind(("127.0.0.1", 6454))
        except OSError:
            pytest.skip("loopback Art-Net listener is already in use")
        receiver.settimeout(0.1)
        with running_qlcplus(
            RIG_ROOT / "QLC+ Setups" / "Vibra.qxw", tmp_path, loopback_artnet=True
        ) as port:
            with urlopen(f"http://127.0.0.1:{port}/vc.json", timeout=5) as response:
                document = json.load(response)
            if '"flashMaxHoldMs":8000' not in json.dumps(document, separators=(",", ":")):
                pytest.skip("QLC+ does not expose the bounded priority Flash extension")
            with connect(
                f"ws://127.0.0.1:{port}/qlcplusWS",
                open_timeout=5,
                close_timeout=0.1,
                ping_interval=None,
            ) as link:
                link.send("7|255")  # Fiesta's state button
                time.sleep(1)
                pressed_at = time.monotonic()
                link.send("12|255")  # Override Flash, never released by this client
                settle_until = time.monotonic() + 0.75
                while time.monotonic() < settle_until:
                    try:
                        receiver.recvfrom(2048)
                    except socket.timeout:
                        pass
                held = []
                capture_until = time.monotonic() + 2
                while time.monotonic() < capture_until:
                    try:
                        wheels = artnet_wheels(receiver.recvfrom(2048)[0])
                    except socket.timeout:
                        continue
                    if wheels is not None:
                        held.append(wheels)
                assert len(held) >= 50, len(held)
                assert all(wheels == (4, 4, 4, 4) for wheels in held), held[:12]

            after = []
            capture_until = pressed_at + 10
            while time.monotonic() < capture_until:
                try:
                    wheels = artnet_wheels(receiver.recvfrom(2048)[0])
                except socket.timeout:
                    continue
                if wheels is not None:
                    after.append((time.monotonic() - pressed_at, wheels))
            late = [wheels for elapsed, wheels in after if elapsed > 8.5]
            assert len(late) >= 20 and sum(wheels != (4, 4, 4, 4) for wheels in late) > len(late) // 2
