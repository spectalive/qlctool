"""QLC+ workspace XML constants.

Values reverse-engineered from real 4.13.1 workspaces and confirmed against the
QLC+ source (engine/src/function.cpp). See docs/qlctool-design.md.
"""

# Namespace every element in a .qxw / .qxf lives in.
QLC_NS = "http://www.qlcplus.org/Workspace"

# Emitted verbatim at the top of every saved workspace, ahead of the root.
XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>'
DOCTYPE = "<!DOCTYPE Workspace>"

# Function type strings (KSceneString, KChaserString, ... in the QLC+ source).
FUNCTION_TYPES = (
    "Scene",
    "Chaser",
    "EFX",
    "Collection",
    "Sequence",
    "RGBMatrix",
    "Show",
    "Audio",
    "Video",
    "Script",
)
