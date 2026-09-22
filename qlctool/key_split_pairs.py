"""The two-colour looks on keys 9 and 0 of every colour bank.

The hand-built console's keys 9 and 0 were not solid colours: on every bank
they were the alternating two-colour looks, blue/red on 9 and red/blue on 0.
The generator put Naranja and Rosa there instead - muscle-memory regression,
old-vs-new audit 2026-08-28. These pairs go back on those keys; the two
solids stay in the bank, keyless.
"""

KEY_SPLIT_PAIRS: tuple[tuple[str, str], ...] = (("Azul", "Rojo"), ("Rojo", "Azul"))
