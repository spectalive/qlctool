"""Parse the `qlctool stage` command's WxHxD stage size in metres."""

from .generate.generate_stage_layout import DEFAULT_STAGE


def stage_size(spec: str | None) -> tuple[int, int, int]:
    """Parse a WxHxD stage in metres, e.g. '12x6x8'."""
    if not spec:
        return DEFAULT_STAGE
    parts = spec.lower().split("x")
    if len(parts) != 3:
        raise SystemExit("--stage takes WIDTHxHEIGHTxDEPTH in metres, e.g. 12x6x8")
    width, height, depth = (int(p) for p in parts)
    return width, height, depth
