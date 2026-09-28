"""Write a FixtureVal element's (offset, value) pairs back, sorted by offset."""


def write_fixture_val_pairs(value, pairs):
    value.text = ",".join(f"{o},{v}" for o, v in sorted(pairs.items()))
