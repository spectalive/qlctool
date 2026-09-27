"""The channel numbers the shipped input profile declares."""

from lxml import etree

from ..generate.input_profile import build_input_profile
from ..xmlutil import localname


def input_profile_channels() -> set[int]:
    """The channel numbers the shipped input profile declares."""
    profile = etree.fromstring(build_input_profile())
    return {
        int(channel.attrib["Number"])
        for channel in profile.iter()
        if localname(channel) == "Channel"
    }
