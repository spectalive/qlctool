"""Explain the priority loss of an API-started burst beside the held Mac cue."""


def desk_burst_note(key: str) -> str | None:
    if key in ("humo-ya", "humo-vert"):
        return None
    if key in ("strobo", "strobo-suave"):
        return "Sin prioridad Override: otro barrido de shutter puede pisar el estrobo."
    if key in ("flash", "flash-lento", "blanco"):
        return "Luz a máxima intensidad; rueda de color y estrobo pueden ser pisados por el show."
    if key == "flash-color":
        return "Conserva el color del show; otro barrido de shutter puede pisar el estrobo."
    return "Sin ForceLTP ni Override: el color se suma al show; rueda y estrobo pueden ser pisados."
