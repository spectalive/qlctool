"""Every Button nested anywhere under a widget."""

from qlctool.localname import localname


def buttons_of(widget):
    return [child for child in widget.iter() if localname(child) == "Button"]
