"""The ids of a parsed module's docstring nodes, so a scan over string literals can skip them."""

import ast


def docstring_ids(tree: ast.AST) -> set[int]:
    """`id()` of every module, function and class docstring constant in `tree`."""
    return {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef))
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
    }
