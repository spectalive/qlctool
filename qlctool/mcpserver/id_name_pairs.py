"""The `id|name|id|name` lists QLC+ answers `getFunctionsList` and `getWidgetsList` with."""


def id_name_pairs(fields: list[str]) -> list[tuple[int, str]]:
    """(id, name) pairs; an empty console or show answers one empty field and gives none.

    QLC+ does not escape the separator, so a caption or name holding `|`
    shifts every pair after it and can read as an id that is not there.
    That is why the write tools confirm their target with
    `getWidgetType` / `getFunctionType` before sending anything.
    """
    return [
        (int(fields[index]), fields[index + 1])
        for index in range(0, len(fields) - 1, 2)
        if fields[index].isdigit()
    ]
