"""How a finding of `rule_caption_promise` names each promise, in the checks' Spanish."""

from .caption_promises import BEAM_WHEEL, BUILTIN_EFFECTS, GOBO, HAZE, PIXEL_GROUP, PRISM

PROMISE_WORDS: dict[str, str] = {
    GOBO: "rueda de gobos",
    PRISM: "prisma",
    HAZE: "maquina de humo",
    BEAM_WHEEL: "beam con rueda de color",
    PIXEL_GROUP: "grupo de pixeles",
    BUILTIN_EFFECTS: "aparato con efectos propios",
}
