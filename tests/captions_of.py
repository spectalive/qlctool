"""The captions of a widget's direct Button children."""

from qlctool.localname import localname


def captions_of(widget):
    return [child.attrib.get("Caption", "") for child in widget if localname(child) == "Button"]
