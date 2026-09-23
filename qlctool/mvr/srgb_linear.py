"""One sRGB channel (0-1) undone to linear light, the IEC 61966-2-1 curve."""


def srgb_linear(channel: float) -> float:
    if channel <= 0.04045:
        return channel / 12.92
    return float(((channel + 0.055) / 1.055) ** 2.4)
