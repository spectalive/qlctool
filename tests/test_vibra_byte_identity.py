"""The three Vibra workspaces regenerate byte for byte (2026-09-24).

The show-description refactor (docs/superpowers/specs/
2026-09-24-show-description-design.md) moves every table the generator reads.
The rule that governs it: a changed byte in Vibra.qxw, Vibra-beats.qxw or
Vibra-split.qxw is a failed step until the owner accepts the difference.
"""

import hashlib
import json
from pathlib import Path

from vibra_regen import regenerate_vibra

SETUPS = Path(__file__).resolve().parents[3] / "QLC+ Setups"
BASELINE = json.loads(Path(__file__).with_name("vibra_baseline.json").read_text(encoding="utf-8"))


def test_the_baseline_is_what_the_repository_ships():
    for name, entry in BASELINE.items():
        assert hashlib.sha256((SETUPS / name).read_bytes()).hexdigest() == entry["sha256"], name


def test_the_three_vibra_workspaces_regenerate_byte_for_byte(tmp_path):
    assert regenerate_vibra(tmp_path) == {name: entry["sha256"] for name, entry in BASELINE.items()}


def test_the_three_vibra_descriptions_regenerate_byte_for_byte(tmp_path):
    hashes = regenerate_vibra(tmp_path, use_descriptions=True)
    assert hashes == {name: entry["sha256"] for name, entry in BASELINE.items()}
