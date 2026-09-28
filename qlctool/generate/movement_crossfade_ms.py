"""How long the movement rotations crossfade between blocks, in milliseconds."""

# The hand-built show kept a "(Simultaneo)" twin of every shape - all heads at
# the same phase, the whole rig tracing one figure together - and its rotation
# crossfaded 5 s between blocks (Chaser 23, FadeIn/FadeOut Common 5000). The
# generated show dropped both (old-vs-new audit, 2026-08-28); the twins come
# back as chaser steps per family, same envelope as the phased version.
MOVEMENT_CROSSFADE_MS = 5000
