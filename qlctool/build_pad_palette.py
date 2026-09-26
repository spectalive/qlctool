"""The SMC-PAD LED bridge's palette, read from the saved workspace.

The bridge lights the pad under the finger, dimmed while the function is idle
and full-bright while QLC+'s feedback says it is active. It used to hard-code
that palette in Swift, and a test in the show's repository compared it with
the toolkit's tables by hand (ruling D-R2, 2026-09-26). This writes it instead,
from the SMC-PAD profile the console is generated with: the colour comes from
the pad profile (`smc_pad_colors`), not from the console button, which on some
page-2 hooks wears its page's colour. A pad is lit when the workspace binds a
widget to its channel on the pad's input universe and the profile colours that
channel; every other pad of the two banks the show uses glows the faint free
grey, so a lit pad always does something.
"""

import hashlib
from pathlib import Path
from typing import Any

from .checks.bound_inputs import bound_inputs
from .controllers.smc_pad_profile import SMC_PAD
from .generate.smc_pad_device import PAD_MIDI_CHANNEL, PADS, pad_channel
from .generate.smc_pad_note import pad_note
from .pad_idle_colour import pad_idle_colour
from .pad_input_universe import pad_input_universe
from .slug import slugify
from .workspace import Workspace

FORMAT = 1
GENERATOR = "qlctool pad-palette"
BANKS = (1, 2)
# A pad no function is bound to: dark enough to read as off, lit enough to
# find in a dark room (the bridge's `FREE_PAD`).
FREE_PAD = (20, 20, 20)


def build_pad_palette(workspace: Workspace, path: str | Path) -> dict[str, Any]:
    """Every pad's note, control and colours; no pads at all when nothing is bound to one."""
    root = workspace.root
    bound: dict[int, list[int]] = {}
    for channel, element in bound_inputs(root, pad_input_universe(root)):
        bound.setdefault(channel, []).append(int(element.get("ID", "-1")))
    control_of = {channel: name for name, channel in SMC_PAD.bindings.items()}
    pads: list[dict[str, Any]] = []
    for bank in BANKS:
        for pad in range(1, PADS + 1):
            channel = pad_channel(pad, bank)
            widgets = bound.get(channel, [])
            control = control_of.get(channel) if widgets else None
            colour = SMC_PAD.colors.get(control or "")
            active = FREE_PAD if colour is None else colour
            pads.append(
                {
                    "bank": bank,
                    "pad": pad,
                    "note": pad_note(pad, bank),
                    "channel": channel,
                    "control": control,
                    "widgets": widgets,
                    "lit": colour is not None,
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
        "device": SMC_PAD.name,
        "midiChannel": PAD_MIDI_CHANNEL,
        "show": {
            "key": slugify(path.stem),
            "workspace": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "",
        },
        "pads": pads,
    }
