"""A GDTF model drawn from a primitive, with no mesh file behind it."""

from pygdtf import Model, PrimitiveType


def geometry_model(name: str, length: float, width: float, height: float, primitive: str) -> Model:
    model = Model(
        name=name,
        length=length,
        width=width,
        height=height,
        primitive_type=PrimitiveType(primitive),
    )
    # No mesh file: the primitive is the model. pygdtf would otherwise write
    # `File="None"`, which BlenderDMX reads as a file called None and fails to
    # load before falling back to the primitive anyway.
    model.file_attr = ""
    return model
