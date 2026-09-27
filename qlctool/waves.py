"""waves.js: the sweep plus its tail, one frame shorter on an odd span."""

# waves.js: taillength 50 %, direction Right, orientation Horizontal.
WAVES_TAIL = 0.5


def waves(span: int) -> int:
    """waves.js: the sweep plus its tail, one frame shorter on an odd span."""
    tail = max(1, round(span * WAVES_TAIL))
    return span + tail - (0 if span % 2 == 0 else 1)
