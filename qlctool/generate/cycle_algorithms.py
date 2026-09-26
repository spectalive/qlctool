"""What the unattended matrix cycle steps.

"Strobe" is generated but left out of it: it is a strobe, and this show's own
rule is that a strobe is a button somebody holds, not one look in a rotation
that loops all night. On the bars it was a third of the reason the pixels read
as "off half the time".
"""

CYCLE_ALGORITHMS: tuple[str | None, ...] = ("Fill", "Even/Odd", "Waves", None)
