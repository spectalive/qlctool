"""A finding's field, made something JSON can carry."""


def json_value(value: object) -> object:
    """Numbers, text, booleans and None as they are; sequences item by item; the rest as text."""
    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, list | tuple | set | frozenset):
        return [json_value(item) for item in value]
    return str(value)
