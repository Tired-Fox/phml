"""Helper methods for converting an ast to phml, html, and json."""

from copy import deepcopy
from json import dumps
from typing import Optional

from phml.nodes import AST, All_Nodes, Element, Position, Root
from phml.utils import find_all, remove_nodes, visit_children
from phml.virtual_python import VirtualPython

from .util import apply_conditions, apply_python, replace_components


def phml(ast: AST, indent: int = 0) -> str:
    """Compile a given phml ast to a phml string with a certain indent amount."""
    return __to_html(ast, indent)


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

    return __to_html(src, indent)


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


def __to_html(ast: AST, offset: int = 0) -> str:
    def one_line(node, indent: int = 0) -> str:
        return "".join(
            [
                " " * indent + node.start_tag(),
                node.children[0].stringify(
                    indent + offset if node.children[0].num_lines > 1 else 0
                ),
                node.end_tag(),
            ]
        )

    def many_children(node, indent: int = 0) -> list:
        lines = []
        for child in visit_children(node):
            if child.type == "element":
                lines.extend(compile_children(child, indent + offset))
            else:
                lines.append(child.stringify(indent + offset))
        return lines

    def construct_element(node, indent: int = 0) -> list:
        lines = []
        if (
            len(node.children) == 1
            and node.children[0].type == "text"
            and node.children[0].num_lines == 1
        ):
            lines.append(one_line(node, indent))
        else:
            lines.append(" " * indent + node.start_tag())
            lines.extend(many_children(node, indent))
            lines.append(" " * indent + node.end_tag())
        return lines

    def compile_children(node: All_Nodes, indent: int = 0) -> list[str]:
        lines = []
        if node.type == "element":
            if node.startend:
                lines.append(" " * indent + node.start_tag())
            else:
                lines.extend(construct_element(node, indent))
        elif node.type == "root":
            for child in visit_children(node):
                lines.extend(compile_children(child))
        else:
            lines.append(node.stringify(indent + offset))
        return lines

    lines = compile_children(ast.tree)
    return "\n".join(lines)
