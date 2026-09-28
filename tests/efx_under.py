"""The EFX a function starts, in step order."""

from qlctool.findall_local import findall_local


def efx_under(by_id, function):
    if function.attrib.get("Type") == "EFX":
        return [function]
    return [
        efx
        for step in findall_local(function, "Step")
        for efx in efx_under(by_id, by_id[(step.text or "").strip()])
    ]
