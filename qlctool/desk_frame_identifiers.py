"""Resolve each current console frame's vocabulary once per inspection."""

from .desk_frame_identifier import desk_frame_identifier
from .desk_widget import DeskWidget
from .names.names import Names


def desk_frame_identifiers(frames: dict[int, DeskWidget], names: Names) -> dict[int, str | None]:
    return {
        identifier: desk_frame_identifier(frame.caption, names)
        for identifier, frame in frames.items()
    }
