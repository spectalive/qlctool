"""`qlctool input-profile`: write the SMC-PAD's QLC+ input profile from the show's own map."""

import argparse
from pathlib import Path

from .generate.input_profile import build_input_profile


def cmd_input_profile(args: argparse.Namespace) -> int:
    """Write the SMC-PAD's QLC+ input profile from the map the show uses."""
    Path(args.out).write_bytes(build_input_profile())
    print(f"Wrote {args.out}")
    return 0
