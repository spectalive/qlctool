"""Page 3's title promises only the haze and beam wheels the rig has (Plan C Task 4, 2026-09-25)."""

import pytest

from qlctool.generate.page_control_title import page_control_title
from qlctool.names.shipped_names import shipped_names


@pytest.mark.parametrize(
    ("has_haze_light", "has_beam_wheel", "key"),
    [
        (True, True, "page_control"),
        (False, True, "page_control_no_haze"),
        (True, False, "page_control_no_beam_wheel"),
        (False, False, "page_control_no_haze_no_beam_wheel"),
    ],
)
def test_each_rig_gets_the_title_that_names_what_it_has(has_haze_light, has_beam_wheel, key):
    assert page_control_title(has_haze_light, has_beam_wheel) == key
    title = shipped_names("en").display(key)
    assert ("haze" in title) == has_haze_light
    assert ("BEAM" in title) == has_beam_wheel
