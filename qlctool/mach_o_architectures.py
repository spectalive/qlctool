"""The CPU architectures a Mach-O header says its binary carries."""

import struct


def mach_o_architectures(header: bytes) -> frozenset[str] | None:
    """Architecture names from a thin or universal header; None when it is not Mach-O.

    Only the types QLC+ ships for are named; anything else is its hex cputype.
    """
    names = {0x01000007: "x86_64", 0x0100000C: "arm64", 7: "i386", 12: "arm"}
    magic = header[:4]
    if magic in (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe") and len(header) >= 8:
        (cputype,) = struct.unpack_from("<i", header, 4)
        return frozenset({names.get(cputype, hex(cputype))})
    if magic in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf") and len(header) >= 8:
        (count,) = struct.unpack_from(">I", header, 4)
        size = 20 if magic == b"\xca\xfe\xba\xbe" else 32
        # A Java class file shares this magic; its "count" is a version in the 40s.
        if count == 0 or count > 16 or len(header) < 8 + count * size:
            return None
        types = [struct.unpack_from(">i", header, 8 + i * size)[0] for i in range(count)]
        return frozenset(names.get(t, hex(t)) for t in types)
    return None
