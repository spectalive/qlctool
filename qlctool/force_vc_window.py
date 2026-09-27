"""Force a workspace copy to open on the Virtual Console, whatever it was saved on.

The QLC+ 5 QML build has one window, filled by a single `Loader`
(`qmlui/qml/MainView.qml`). `App::loadXML` switches that loader to the view
named by the root `<Workspace>` element's `CurrentWindow` attribute
(`qmlui/app.cpp`), and the Virtual Console page area - the only thing that
logs `renderPage` (`qml_loaded_markers.py`) - is instantiated only once
`VirtualConsole.qml` is what got loaded. A workspace last saved from Fixtures
& Functions, Show Manager, Simple Desk or I/O (`CurrentWindow` anything but
`"VC"`) therefore never renders that page, and validation's end-of-load wait
never sees its marker (C-1, 2026-09-27 final review; `Vibra-split.qxw` ships
with `CurrentWindow="IOMGR"`).

The saved value only records where the operator last left the window; it is
not a fact validation needs to preserve, so a validation copy is free to
override it.
"""

from lxml import etree

VC_WINDOW = "VC"


def force_vc_window(root: etree._Element) -> None:
    """Set the root `<Workspace>` element's `CurrentWindow` to `"VC"`."""
    root.set("CurrentWindow", VC_WINDOW)
