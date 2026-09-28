"""The four-page console Frame nested under the console's root frame."""

from walk_widgets import walk_widgets

from qlctool.find_local import find_local
from qlctool.localname import localname


def console_frame_of(root_frame):
    return next(
        widget
        for widget, _, _ in walk_widgets(root_frame)
        if localname(widget) == "Frame"
        and (multipage := find_local(widget, "Multipage")) is not None
        and multipage.attrib["PagesNum"] == "4"
    )
