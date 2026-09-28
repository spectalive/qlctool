"""The ID of the Function a Button points at."""

from qlctool.find_local import find_local


def function_id_of(button):
    return int(find_local(button, "Function").attrib["ID"])
