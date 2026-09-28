"""Add a one-member Collection wrapper and its Toggle button."""

from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions


def wrapper_button(workspace, frame, source_name, wrapper_name):
    """Add a one-member Collection wrapper and its Toggle button."""
    from qlctool.functions.build_collection import build_collection
    from qlctool.next_function_id import next_function_id
    from qlctool.vc.build_button import build_button
    from qlctool.vc.next_widget_id import next_widget_id

    source_id = int(_functions(workspace)[source_name].attrib["ID"])
    wrapper_id = next_function_id(workspace.root)
    workspace.add_function(build_collection(wrapper_id, wrapper_name, [source_id]))
    build_button(
        frame,
        next_widget_id(workspace.root),
        wrapper_name,
        wrapper_id,
        x=550,
        y=30,
        width=105,
        height=50,
    )
    return wrapper_id
