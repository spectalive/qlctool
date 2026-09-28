"""A copy of a scene under a new id: the old burst chasers' white/black."""


def twin_scene(workspace, functions, source_name, twin_name):
    """A copy of a scene under a new id: the old burst chasers' white/black."""
    import copy

    from qlctool.next_function_id import next_function_id

    twin = copy.deepcopy(functions[source_name])
    twin.set("ID", str(next_function_id(workspace.root)))
    twin.set("Name", twin_name)
    workspace.add_function(twin)
    return twin
