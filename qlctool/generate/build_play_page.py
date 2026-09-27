"""Build the JUGAR page: one releasable manual surface per channel family."""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.default_names import default_names
from ..names.names import Names
from ..palette import PALETTE
from .build_color_family import build_color_family
from .build_colour_hits import build_colour_hits
from .build_gobo_family import build_gobo_family
from .build_movement_family import build_movement_family
from .build_pixel_family import build_pixel_family
from .build_prism_family import build_prism_family
from .build_reset_strip import build_reset_strip
from .generated_play_wrappers import GeneratedPlayWrappers
from .play_page_layout import LEFT, WIDTH

# Catalogue identifiers of the frames a consumer (the tablet's map) finds the
# page's parts by.
FAMILY_FRAMES = ("family_colour", "family_pixels", "family_heads", "family_gobos", "family_prism")


def build_play_page(
    outer: etree._Element,
    button: Callable[..., object],
    master_button: Callable[..., object],
    frame: Callable[..., etree._Element],
    label: Callable[..., object],
    names: Mapping[int, str],
    master: Mapping[str, int],
    play_wrappers: GeneratedPlayWrappers,
    colour_flash_ids: Mapping[str, int],
    flash_functions: Sequence[str],
    page: int,
    title_font: str,
    big_font: str,
    small_font: str,
    palette: Mapping[str, tuple[int, int, int]] | None = None,
    vocabulary: Names | None = None,
) -> None:
    """Append page two; only its picks and reset-strip duplicates stay keyless.

    `names` maps function id to function name; the page's own words come from
    `vocabulary`, None meaning `default_names()`.
    """
    vocabulary = default_names() if vocabulary is None else vocabulary
    ids_by_name = {name: function_id for function_id, name in names.items()}
    flashes = set(flash_functions)

    label(
        outer,
        vocabulary.display("page_play"),
        LEFT,
        30,
        WIDTH,
        22,
        page=page,
        font=title_font,
    )
    build_reset_strip(
        outer,
        button,
        frame,
        label,
        master,
        flashes,
        page,
        title_font,
        small_font,
        vocabulary,
    )
    build_colour_hits(
        outer,
        button,
        frame,
        colour_flash_ids,
        page,
        title_font,
        small_font,
        PALETTE if palette is None else palette,
        vocabulary,
    )
    build_color_family(
        outer,
        button,
        master_button,
        frame,
        label,
        names,
        ids_by_name,
        play_wrappers,
        page,
        title_font,
        big_font,
        small_font,
        vocabulary,
    )
    build_pixel_family(
        outer,
        button,
        master_button,
        frame,
        label,
        names,
        ids_by_name,
        play_wrappers,
        page,
        title_font,
        big_font,
        small_font,
        vocabulary,
    )
    build_movement_family(
        outer,
        button,
        master_button,
        frame,
        label,
        names,
        ids_by_name,
        play_wrappers,
        page,
        title_font,
        big_font,
        small_font,
        vocabulary,
    )
    build_gobo_family(
        outer,
        button,
        master_button,
        frame,
        label,
        names,
        ids_by_name,
        play_wrappers,
        page,
        title_font,
        big_font,
        small_font,
        vocabulary,
    )
    build_prism_family(
        outer,
        button,
        master_button,
        frame,
        label,
        names,
        ids_by_name,
        play_wrappers,
        page,
        title_font,
        big_font,
        small_font,
        vocabulary,
    )
