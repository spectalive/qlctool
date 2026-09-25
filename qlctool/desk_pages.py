"""The desk map's pages: each page's sections in order, titled in the show's words."""

from typing import Any

from .desk_policy import PAGES, SECTION_ORDER, SECTION_TITLES
from .names.names import Names


def desk_pages(
    sections: dict[tuple[str, str], list[str]],
    section_solo: dict[tuple[str, str], int | None],
    vocabulary: Names,
) -> list[dict[str, Any]]:
    """Moved out of `build_deskmap` verbatim (2026-09-25), to keep it under the cap."""
    pages = []
    for page_key, title in PAGES:
        page_sections = sorted(
            (
                {
                    "key": section,
                    "title": vocabulary.display(SECTION_TITLES[section]),
                    "solo": section_solo[(page_key, section)],
                    "controls": keys,
                }
                for (page, section), keys in sections.items()
                if page == page_key
            ),
            key=lambda s: SECTION_ORDER.index(s["key"]),
        )
        if page_sections:
            pages.append(
                {"key": page_key, "title": vocabulary.display(title), "sections": page_sections}
            )
    return pages
