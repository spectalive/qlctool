"""The first Frame or SoloFrame under a console frame whose caption starts with a name."""

from walk_widgets import walk_widgets

from qlctool.localname import localname


def frame_named(frame, caption):
    for widget, _, _ in walk_widgets(frame):
        if localname(widget) in ("Frame", "SoloFrame") and widget.attrib.get(
            "Caption", ""
        ).startswith(caption):
            return widget
    raise AssertionError(f"no frame captioned {caption!r}")
