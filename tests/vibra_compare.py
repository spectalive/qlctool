"""Regenerate the three Vibra workspaces and prove nothing moved.

    .venv/bin/python tests/vibra_compare.py [--descriptions] [--validate]

Exit 0 only when every regenerated workspace hashes to its baseline, every
`qlctool check` rule finds nothing in it, and - with --validate - headless QLC+
loads it without a complaint. --descriptions regenerates from the .toml
descriptions (Task 8 of the show-description plan) instead of the CLI flags.

It runs without conftest, so it names the rig's fixture folder the way conftest
does: QLCTOOL_FIXTURES, when the caller has not set it, is tests/data/rig's.
"""

import argparse
import json
import os
import tempfile
from pathlib import Path

from rig_root import RIG_ROOT
from vibra_regen import regenerate_vibra

from qlctool.checks.check_workspace import check_workspace
from qlctool.library import FixtureLibrary
from qlctool.validate import validate_workspace
from qlctool.workspace import Workspace


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--descriptions", action="store_true", help="regenerate from the .toml files"
    )
    parser.add_argument("--validate", action="store_true", help="also load each in headless QLC+")
    args = parser.parse_args(argv)
    os.environ.setdefault("QLCTOOL_FIXTURES", str(RIG_ROOT / "QLC+ Fixtures"))
    baseline = json.loads(
        Path(__file__).with_name("vibra_baseline.json").read_text(encoding="utf-8")
    )
    library = FixtureLibrary.load()
    failed = False
    with tempfile.TemporaryDirectory() as scratch:
        out_dir = Path(scratch)
        hashes = regenerate_vibra(out_dir, use_descriptions=args.descriptions)
        for name, entry in baseline.items():
            same = hashes[name] == entry["sha256"]
            findings = check_workspace(Workspace.load(out_dir / name), library)
            line = f"{name}: {'identical' if same else 'CHANGED ' + hashes[name]}, {len(findings)} finding(s)"
            failed = failed or not same or bool(findings)
            if args.validate:
                result = validate_workspace(out_dir / name)
                line += (
                    ", QLC+ loaded it"
                    if result.ok
                    else f", QLC+ reported {len(result.errors)} problem(s)"
                )
                failed = failed or not result.ok
            print(line)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
