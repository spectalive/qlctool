"""Page 1's tempo help and page 4's captions name only what the rig has (2026-09-25).

Plan C final review: the small club's console spoke of gobos, prism, bars,
panels and their 42 built-in effects, none of which it has.
"""

import pytest

from qlctool.generate.library_help_lines import library_help_lines
from qlctool.generate.matrices_frame_caption import matrices_frame_caption
from qlctool.generate.tempo_help_line import tempo_help_line
from qlctool.names.shipped_names import shipped_names


@pytest.mark.parametrize(
    ("has_gobo", "has_prism", "key"),
    [
        (True, True, "tempo_2"),
        (True, False, "tempo_2_no_prism"),
        (False, True, "tempo_2_no_gobo"),
        (False, False, "tempo_2_no_gobo_no_prism"),
    ],
)
def test_2026_09_25_the_tempo_help_names_only_the_animations_the_show_built(
    has_gobo, has_prism, key
):
    assert tempo_help_line(has_gobo, has_prism) == key
    for language in ("en", "es"):
        line = shipped_names(language).display(key)
        assert ("gobo" in line) == has_gobo
        assert ("prism" in line) == has_prism


@pytest.mark.parametrize(
    ("has_pixel_groups", "has_builtin_effects", "key"),
    [
        (True, True, "matrices_frame"),
        (True, False, "matrices_frame_groups"),
        (False, True, "matrices_frame_groups"),
        (False, False, "matrices_frame_groups"),
    ],
)
def test_2026_09_25_the_matrices_frame_names_bars_and_panels_only_on_a_rig_with_them(
    has_pixel_groups, has_builtin_effects, key
):
    assert matrices_frame_caption(has_pixel_groups, has_builtin_effects) == key
    for language in ("en", "es"):
        caption = shipped_names(language).display(key)
        assert ("panel" in caption) == (has_pixel_groups and has_builtin_effects)


@pytest.mark.parametrize("has_builtin_effects", [True, False])
def test_2026_09_25_the_library_help_speaks_of_built_in_effects_only_where_they_exist(
    has_builtin_effects,
):
    """The count is the rig's, filled in: 17 here, never a written-in 42."""
    for language in ("en", "es"):
        names = shipped_names(language)
        lines = library_help_lines(has_builtin_effects)
        text = " ".join(names.render(k, count=17) for k in lines if k)
        assert ("17" in text) == has_builtin_effects
        assert "42" not in text
        assert ("panel" in text) == has_builtin_effects
