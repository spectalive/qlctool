"""Write one <Channel> element of a QLC+ input profile."""

from lxml import etree

from .profile_ns import PROFILE_NS


def profile_channel(root: etree._Element, number: int, name: str, type_: str) -> None:
    channel = etree.SubElement(root, f"{{{PROFILE_NS}}}Channel", Number=str(number))
    etree.SubElement(channel, f"{{{PROFILE_NS}}}Name").text = name
    etree.SubElement(channel, f"{{{PROFILE_NS}}}Type").text = type_
