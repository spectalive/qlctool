"""`qlctool install`: hand QLC+ the configured definitions, profile and gobos."""

import argparse
from dataclasses import replace
from pathlib import Path

from .apply_install import apply_install
from .fixture_dirs import fixture_dirs
from .install_plan import install_plan
from .qlc_gobo_dir import qlc_gobo_dir
from .qlc_user_dir import qlc_user_dir
from .toolkit_config_from import toolkit_config_from


def cmd_install(args: argparse.Namespace) -> int:
    """Hand QLC+ the configured definitions, profile and gobos - or say what it lacks.

    The fixture folders follow ruling B3 (`--fixtures`, QLCTOOL_FIXTURES, then
    the nearest qlctool.toml); the profiles and gobos come from qlctool.toml.
    A definition the repo fixed and QLC+ never received is the silent failure
    this exists for: the show loads, validates and runs on last week's channel
    map. `--check` is the question, exit 1 is the answer.
    """
    config = toolkit_config_from(Path.cwd())
    fixtures = fixture_dirs(args.fixtures or (), (), None, Path.cwd())
    if fixtures:
        config = replace(config, fixtures=fixtures)
    items = install_plan(config, user_dir=qlc_user_dir(), gobo_dir=qlc_gobo_dir())
    behind = [item for item in items if item.needs_copy]
    if not args.check:
        for item in apply_install(behind):
            print(f"  {item.state:<8} {item.source.name} -> {item.destination}")
        print(f"{len(behind)} file(s) copied, {len(items) - len(behind)} already in sync")
        return 0
    for item in behind:
        print(f"  {item.state:<8} {item.source.name} -> {item.destination}")
    if behind:
        print(
            f"QLC+ is behind the repo on {len(behind)} of {len(items)} file(s); run qlctool install"
        )
        return 1
    print(f"QLC+ has every one of the configured {len(items)} file(s)")
    return 0
