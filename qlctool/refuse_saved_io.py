"""Validation's guard against the I/O patches QLC+ opens from its own settings."""

import os

from .saved_io_patches import saved_io_patches

OVERRIDE = "QLCTOOL_ALLOW_SAVED_IO"


def refuse_saved_io(allowed: bool = False) -> None:
    """Raise, naming the settings keys, when QLC+ would open saved I/O patches at startup.

    `allowed` (or `QLCTOOL_ALLOW_SAVED_IO=1`) validates anyway, knowingly.
    """
    if allowed or os.environ.get(OVERRIDE) == "1":
        return
    keys = saved_io_patches()
    if not keys:
        return
    shown = "; ".join(keys[:4]) + (f"; and {len(keys) - 4} more" if len(keys) > 4 else "")
    raise RuntimeError(
        f"QLC+'s own settings hold default I/O patches ({shown}); QLC+ opens them at "
        "startup, before any workspace is loaded, so validating would open the rig's "
        "outputs whatever the workspace says. Clear them in QLC+'s Inputs/Outputs, or "
        f"set {OVERRIDE}=1 to validate anyway."
    )
