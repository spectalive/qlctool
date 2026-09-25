"""How far apart two hues are complementary: from here on they mix to grey.

A triad (120 degrees) still mixes to a colour. `rule_split_complementary`
reports two hues this far apart inside one wash, and the four-colour deal
(`quad_seats`) keeps them out of one; neither package owns the number.
"""

COMPLEMENTARY_FROM = 150.0
