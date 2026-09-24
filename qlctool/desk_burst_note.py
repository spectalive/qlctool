"""Explain the priority loss of an API-started burst beside the held Mac cue."""


def desk_burst_note(identifier: str) -> str | None:
    """The desk's warning for a burst, by its source accent's identifier."""
    if identifier in ("hit_smoke_now", "hit_vertical_smoke_now"):
        return None
    if identifier in ("hit_strobe", "hit_strobe_soft"):
        return "Sin prioridad Override: otro barrido de shutter puede pisar el estrobo."
    if identifier in ("hit_flash", "hit_flash_slow", "white"):
        return "Luz a máxima intensidad; rueda de color y estrobo pueden ser pisados por el show."
    if identifier == "hit_flash_colour":
        return "Conserva el color del show; otro barrido de shutter puede pisar el estrobo."
    return "Sin ForceLTP ni Override: el color se suma al show; rueda y estrobo pueden ser pisados."
