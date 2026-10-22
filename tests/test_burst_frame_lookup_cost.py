"""A frame's vocabulary is classified once, regardless of its button count."""

from unittest.mock import patch

from burst_lookup_workspace import burst_lookup_workspace

from qlctool.desk_burst_sources import desk_burst_sources
from qlctool.names.default_names import default_names
from qlctool.names.names import Names


def test_repeated_buttons_do_not_repeat_frame_catalogue_search() -> None:
    names = default_names()
    root = burst_lookup_workspace(names.display("hits"))
    with patch.object(Names, "spellings", autospec=True, side_effect=Names.spellings) as spellings:
        sources = desk_burst_sources(root, names)
    assert len(sources) == 40
    assert spellings.call_count <= len(names.identifiers("frames"))
