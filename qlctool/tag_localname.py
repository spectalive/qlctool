"""Strip the namespace from an XML tag, so comparison ignores prefix bindings."""


def tag_localname(tag: object) -> str:
    if not isinstance(tag, str):
        # Comments / processing instructions compare by their callable tag.
        return str(tag)
    return tag.rsplit("}", 1)[-1]
