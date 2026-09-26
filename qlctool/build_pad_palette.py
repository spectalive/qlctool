"""The SMC-PAD LED bridge's palette, read from the saved workspace.

The bridge paints the pad under the finger the colour the console paints the
button, dimmed while the function is idle and full-bright while QLC+'s
feedback says it is active. It used to hard-code that palette in Swift, and a
test in the show's repository compared the two by hand (ruling D-R2,
2026-09-26). This writes it instead, from the same profile the console is
generated with: a pad is lit when the workspace binds a widget to its channel
and the profile gives that channel a colour; every other pad of the two banks
the show uses glows the faint free-pad grey, so a lit pad always does something.
"""

import hashlib
from pathlib import Path
from typing import Any

from .bound_widget_ids import bound_widget_ids
from .controllers.midi_pad_profile import MidiPadProfile
from .controllers.smc_pad_profile import SMC_PAD
from .generate.smc_pad_device import (
    FIRST_PAD_NOTE,
    PAD_MIDI_CHANNEL,
    PADS,
    pad_channel,
)
from .pad_idle_colour import pad_idle_colour
from .slug import slugify
from .workspace import Workspace

FORMAT = 1
GENERATOR = "qlctool pad-palette"
BANKS = (1, 2)
# A pad no function is bound to: dark enough to read as off, lit enough to
# find in a dark room (the bridge's `FREE_PAD`).
FREE_PAD = (20, 20, 20)


def build_pad_palette(
    workspace: Workspace, path: str | Path, profile: MidiPadProfile = SMC_PAD
) -> dict[str, Any]:
    """Every pad's note, control and colours; no pads at all when nothing is bound to one."""
    bound = bound_widget_ids(workspace.root)
    control_of = {channel: name for name, channel in profile.bindings.items()}
    pads: list[dict[str, Any]] = []
    for bank in BANKS:
        for pad in range(1, PADS + 1):
            channel = pad_channel(pad, bank)
            widgets = bound.get(channel, [])
            control = control_of.get(channel) if widgets else None
            active = profile.colors.get(control or "", FREE_PAD)
            pads.append(
                {
                    "bank": bank,
                    "pad": pad,
                    "note": FIRST_PAD_NOTE + (bank - 1) * PADS + pad - 1,
                    "channel": channel,
                    "control": control,
                    "widgets": widgets,
                    "active": list(active),
                    "idle": list(pad_idle_colour(active)),
                }
            )
    if not any(p["widgets"] for p in pads):
        pads = []

    path = Path(path)
    return {
        "format": FORMAT,
        "generator": GENERATOR,
        "device": profile.name,
        "midiChannel": PAD_MIDI_CHANNEL,
        "show": {
            "key": slugify(path.stem),
            "workspace": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "",
        },
        "pads": pads,
    }
