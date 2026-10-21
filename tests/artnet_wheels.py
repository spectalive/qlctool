"""Read the four 7R colour wheels from one loopback ArtDmx datagram."""


def artnet_wheels(packet: bytes) -> tuple[int, int, int, int] | None:
    if packet[:8] != b"Art-Net\0" or packet[8:10] != b"\x00\x50" or len(packet) <= 291:
        return None
    return tuple(packet[18 + offset] for offset in (225, 241, 257, 273))
