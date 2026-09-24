"""The Vibra functions held while pressed rather than latched."""

# Held, not latched. The smoke burst is one of them on purpose: a pump on a
# Toggle button is how a tank ends up empty when somebody walks away from it.
# Holding it only *releases* because both pumps sit in the Intensity group,
# which is the group QLC+ resets every cycle - see `Generic-LED-Spray-Fog.qxf`.
FLASH_FUNCTIONS = (
    "Flash 100%",
    "Flash 50%",
    "Flash Color",
    "Humo ON",
    "Humo Vertical YA",
    "Golpe Graves",
    # A strobe is a button somebody holds (the show's own rule), and since
    # 2026-09-02 these two are shutter scenes rather than white/black chasers.
    "Strobo Rapido",
    "Strobo Medio",
    # The stage aim: a latched aim under a moving state lasted one movement
    # step; held with Override priority it lasts as long as the hand does.
    "Escenario",
)
