"""Explain the priority loss of an API-started burst beside the held Mac cue."""

from .names.names import Names


def desk_burst_note(identifier: str, names: Names) -> str | None:
    """The desk's warning for a burst, by its source accent's identifier."""
    if identifier in ("hit_smoke_now", "hit_vertical_smoke_now"):
        return None
    if identifier in ("hit_strobe", "hit_strobe_soft"):
        return names.display("desk_note_strobe")
    if identifier in ("hit_flash", "hit_flash_slow", "white"):
        return names.display("desk_note_flash")
    if identifier == "hit_flash_colour":
        return names.display("desk_note_flash_colour")
    return names.display("desk_note_colour")
