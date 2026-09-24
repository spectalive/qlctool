"""Regenerate the three Vibra workspaces into a directory and hash them.

The recipes are the verified ones in AGENTS.md ("Regenerating the show"), read
from vibra_baseline.json so the recipe and the hash it must produce sit side by
side. Output never touches QLC+ Setups/: the shipped files are the baseline.
"""

import hashlib
import json
from pathlib import Path

from qlctool.cli import main


def regenerate_vibra(out_dir: Path, use_descriptions: bool = False) -> dict[str, str]:
    """Workspace name -> sha256 of the file `qlctool newshow` writes for it."""
    setups = Path(__file__).resolve().parents[3] / "QLC+ Setups"
    recipes = json.loads(
        Path(__file__).with_name("vibra_baseline.json").read_text(encoding="utf-8")
    )
    hashes: dict[str, str] = {}
    for name, recipe in recipes.items():
        out = out_dir / name
        if use_descriptions:
            argv = ["newshow", "--description", str(setups / recipe["description"])]
        else:
            argv = [
                "newshow",
                str(setups / recipe["source"]),
                "--plot",
                str(setups / recipe["plot"]),
            ]
            if recipe["beats"]:
                argv.append("--beats")
        if main([*argv, "--out", str(out)]) != 0:
            raise RuntimeError(f"qlctool {' '.join(argv)} failed for {name}")
        hashes[name] = hashlib.sha256(out.read_bytes()).hexdigest()
    return hashes
