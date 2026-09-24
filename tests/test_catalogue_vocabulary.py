"""The Spanish catalogue is exactly the vocabulary the generator writes (2026-09-24).

Until the generators take their names from the catalogue (the next plan), the
Spanish strings exist twice - here and in the generator. This pins them together
so neither can drift without the suite failing.
"""

from qlctool.desk_policy import BURST_FRAME, split_caption
from qlctool.generate.live_console import (
    CHASES_FRAME,
    HITS,
    HITS_FRAME,
    ROOM_FRAME,
    SMOKE_FRAME,
    SMOKE_LIGHT_CAPTION,
)
from qlctool.generate.play_page import COLOR_HITS_FRAME, FAMILY_FRAMES, PICK_PREFIX
from qlctool.names.load_catalogue import load_catalogue
from qlctool.palette import PALETTE
from qlctool.vibra.flash_functions import FLASH_FUNCTIONS
from qlctool.vibra.keys import KEYS
from qlctool.vibra.timing import VIBRA_TIMING

SPANISH = load_catalogue("es")
HIT_IDS = (
    "hit_flash",
    "hit_flash_slow",
    "hit_flash_colour",
    "hit_smoke_now",
    "hit_vertical_smoke_now",
    "hit_strobe",
    "hit_strobe_soft",
)


def test_the_spanish_colours_are_the_palette_in_order():
    assert list(SPANISH["colors"].values()) == list(PALETTE)


def test_every_function_the_vibra_tables_name_is_catalogued():
    named = set(KEYS) | set(FLASH_FUNCTIONS) | set(VIBRA_TIMING.beat_timings)
    assert named <= set(SPANISH["functions"].values())


def test_the_spanish_frames_are_the_captions_the_console_writes():
    frames = SPANISH["frames"]
    assert frames["room_states"] == ROOM_FRAME
    assert frames["hits"] == HITS_FRAME
    assert frames["haze"] == SMOKE_FRAME
    assert frames["intensity_chases"] == CHASES_FRAME
    assert frames["colour_hits"] == COLOR_HITS_FRAME
    assert frames["desk_bursts"] == BURST_FRAME
    families = ("colour", "pixels", "heads", "gobos", "prism")
    assert [frames[f"family_{family}"] for family in families] == list(FAMILY_FRAMES)


def test_the_spanish_captions_are_the_console_hits():
    captions = SPANISH["captions"]
    assert [split_caption(caption)[0] for _, caption in HITS] == [captions[i] for i in HIT_IDS]
    assert captions["vertical_smoke_light"] == SMOKE_LIGHT_CAPTION
    assert captions["pick_prefix"] == PICK_PREFIX
