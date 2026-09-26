"""How long a live write waits before reading back what it changed."""

# QLC+ applies a press or a function start on its own thread (measured on
# QLC+ 5.2.2, 2026-09-26: the state reads back changed well within this).
SETTLE_SECONDS = 0.3
