"""Add a small test frame with Toggle buttons for the named functions."""

from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions

from qlctool.find_local import find_local


def family_frame(workspace, function_names, *, caption="TEST FAMILY", solo=True, nested=False):
    """Add a small test frame with Toggle buttons for the named functions."""
    from qlctool.vc.build_button import build_button
    from qlctool.vc.build_frame import build_frame
    from qlctool.vc.next_widget_id import next_widget_id

    root = find_local(find_local(workspace.root, "VirtualConsole"), "Frame")
    frame = build_frame(
        root,
        next_widget_id(workspace.root),
        caption,
        x=0,
        y=0,
        width=700,
        height=100,
        solo=solo,
    )
    button_parent = frame
    if nested:
        button_parent = build_frame(
            frame,
            next_widget_id(workspace.root),
            "TEST NESTED FAMILY",
            x=0,
            y=0,
            width=680,
            height=70,
            pages=2,
        )
    functions = _functions(workspace)
    for index, name in enumerate(function_names):
        build_button(
            button_parent,
            next_widget_id(workspace.root),
            name,
            int(functions[name].attrib["ID"]),
            x=index * 110,
            y=30,
            width=105,
            height=50,
        )
    return button_parent
