"""Frame placement observes current XML and vocabulary on every invocation."""

from burst_lookup_workspace import burst_lookup_workspace

from qlctool.desk_burst_sources import desk_burst_sources
from qlctool.find_local import find_local
from qlctool.names.names import Names


def test_frame_lookup_is_rebuilt_after_caption_or_vocabulary_changes() -> None:
    names = Names("en", {"en": {"frames": {"hits": "Hits", "room_states": "States"}}})
    root = burst_lookup_workspace("Hits", buttons=2)
    console = find_local(root, "VirtualConsole")
    assert console is not None
    frame = find_local(console, "Frame")
    assert frame is not None
    assert len(desk_burst_sources(root, names)) == 2
    frame.set("Caption", "States")
    assert desk_burst_sources(root, names) == {}
    frame.set("Caption", "Hits")
    assert len(desk_burst_sources(root, names)) == 2
    renamed = Names("en", {"en": {"frames": {"hits": "Fresh", "room_states": "States"}}})
    assert desk_burst_sources(root, renamed) == {}
