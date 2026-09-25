"""A desk key for one caption, unique among the keys already taken."""

from collections.abc import Mapping

from .slug import slugify


def desk_unique_key(existing: Mapping[str, object], caption: str, widget_id: int) -> str:
    key = slugify(caption)
    if key in existing:
        key = f"{key}-{widget_id}"
    return key
