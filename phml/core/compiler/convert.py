"""Helper methods for converting an ast to phml, html, and json."""

from copy import deepcopy
from json import dumps
from typing import Optional

from phml.core.nodes import AST, All_Nodes, Element, Position, Root
from phml.core.virtual_python import VirtualPython
from phml.utilities import find_all, remove_nodes, visit_children

from .to_html import ToHTML
from .util import apply_conditions, apply_python, replace_components


def phml(ast: AST, indent: int = 0) -> str:
    """Compile a given phml ast to a phml string with a certain indent amount."""
    return ToHTML(ast, indent).compile()


def html(
    ast: AST,
    components: Optional[dict[str, dict[str, list | All_Nodes]]] = None,
    indent: int = 0,
    **kwargs,
) -> str:
    """Compile a given phml ast to a html string with a certain indent amount.

    Can provide components that replace certain elements in the ast tree along with additional
    kwargs that are exposed to executed python blocks.

    Args:
        ast (AST): The phml ast to compile
        components (dict[str, dict[str, list | All_Nodes]] | None): key value pairs of element name
        and the replacement mapping. The replacement mapping holds reference to a components python,
        script, and style elements along with the root replacement node.
        indent (int): The offset amount to every indent
        **kwargs (Any): Additional information that will be exposed to executed python blocks.
    """
    components = components or {}
    src = deepcopy(ast)

    # 1. Search for all python elements and get source info.
    #    - Remove when done
    virtual_python = VirtualPython()

    for python_block in find_all(src, {"tag": "python"}):
        if len(python_block.children) == 1:
            if python_block.children[0].type == "text":
                virtual_python += VirtualPython(python_block.children[0].value)

    remove_nodes(src, ["element", {"tag": "python"}])

    # 2. Replace specific element node with given replacement components
    replace_components(src, components, virtual_python, **kwargs)

    for python_block in find_all(src, {"tag": "python"}):
        if len(python_block.children) == 1:
            if python_block.children[0].type == "text":
                virtual_python += VirtualPython(python_block.children[0].value)

    remove_nodes(src, ["element", {"tag": "python"}])

    # 3. Search each element and find py-if, py-elif, py-else, and py-for
    #    - Execute those statements

    apply_conditions(src, virtual_python, **kwargs)

    # 4. Search for python blocks and process them.

    apply_python(src, virtual_python, **kwargs)

    return ToHTML(src, indent).compile()


def json(ast: AST, indent: int = 0) -> str:
    """Compile a given phml ast to a json string with a certain indent amount."""

    def compile_children(node: Root | Element) -> dict:
        data = {"type": node.type}

        if node.type == "root":
            if node.parent is not None:
                raise Exception("Root nodes must only occur as the root of an ast/tree.")

        for attr in vars(node):
            if attr not in ["parent", "children"]:
                value = getattr(node, attr)
                if isinstance(value, Position):
                    data[attr] = value.as_dict()
                else:
                    data[attr] = value

        if hasattr(node, "children"):
            data["children"] = []
            for child in visit_children(node):
                data["children"].append(compile_children(child))

        return data

    data = compile_children(ast.tree)
    return dumps(data, indent=indent)
