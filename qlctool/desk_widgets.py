"""Every Virtual Console widget with the frames above it, flattened for the map.

The console is a tree of frames; the desk wants each widget with its ancestry,
its nearest solo frame, its action and its function, so that a control can be
placed by the frame it sits in and validated against what the master serves
at /vc.json.
"""

from dataclasses import dataclass

FRAME_TAGS = ("Frame", "SoloFrame")
WIDGET_TAGS = ("Button", "Slider", "SpeedDial", "XYPad", "Label")


@dataclass(frozen=True)
class DeskWidget:
    id: int
    kind: str  # Frame, SoloFrame, Button, Slider, SpeedDial, XYPad, Label
    caption: str
    page: int
    function: int | None  # a button's function; None for the rest or when unbound
    action: str  # Toggle, Flash, Blackout, StopAll; "" for non-buttons
    key: str | None
    frames: tuple[int, ...]  # ancestor frame ids, outermost first
    solo: int | None  # nearest SoloFrame id
    fade_out_ms: int  # StopAll only
    slider_mode: str  # Slider only: Level, Playback, GrandMaster, ...
