"""The fragment filename a decomposed Function is written under."""

from lxml import etree

from .slugify import slugify


def function_filename(function: etree._Element) -> str:
    fid = int(function.attrib.get("ID", "0"))
    ftype = function.attrib.get("Type", "Function")
    name = function.attrib.get("Name", "")
    return f"{fid:05d}-{ftype}-{slugify(name)}.xml"
