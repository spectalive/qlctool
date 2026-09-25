"""Why `newshow` will not build on a patch, in the show's words, or None.

2026-09-25 review: with no definition found, every fixture's channels were
unreadable, so the rig-minimum refusal said the patch lacked a pan/tilt
fixture - telling a user with a correct rig and a wrong `--fixtures` that the
rig was wrong. When nothing patched resolves, the refusal names that cause
and the folders searched instead.
"""

from lxml import etree

from .capabilities_of import capabilities_of
from .fixture import patched_fixtures
from .generate.rig_below_minimum import rig_below_minimum
from .library import FixtureLibrary
from .names.names import Names
from .searched_folders import searched_folders


def newshow_refusal(root: etree._Element, library: FixtureLibrary, names: Names) -> str | None:
    """The message to exit with, or None when the patch meets the minimum."""
    if patched_fixtures(root) and not capabilities_of(root, library):
        return names.render("rig_without_definitions", searched=searched_folders(library, names))
    missing = rig_below_minimum(root, library, names)
    if not missing:
        return None
    return names.render("rig_below_minimum", missing=", ".join(missing))
