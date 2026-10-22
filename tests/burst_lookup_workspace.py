"""An owned console with repeated buttons under one localized frame."""

from lxml import etree


def burst_lookup_workspace(caption: str, buttons: int = 40) -> etree._Element:
    root = etree.Element("Workspace")
    console = etree.SubElement(root, "VirtualConsole")
    frame = etree.SubElement(console, "Frame", ID="1", Caption=caption)
    for index in range(buttons):
        button = etree.SubElement(frame, "Button", ID=str(index + 2), Caption=f"Hit {index}")
        etree.SubElement(button, "Function", ID=str(index + 100))
        etree.SubElement(button, "Action").text = "Flash"
    return root
