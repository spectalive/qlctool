"""[timing]'s duration tables: each key in seconds, and the ShowTiming field it sets."""

from collections.abc import Mapping

DURATION_TABLES: Mapping[str, Mapping[str, str]] = {
    "levels": {
        "ambient_s": "ambient_ms",
        "party_s": "party_ms",
        "peak_s": "peak_ms",
        "dynamic_s": "dynamic_ms",
    },
    "dynamic": {"chase_s": "dynamic_chase_ms", "pingpong_s": "dynamic_pingpong_ms"},
    "panels": {"effects_s": "panel_effects_ms", "manual_s": "panel_manual_ms"},
}
