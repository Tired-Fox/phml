from copy import deepcopy
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
        and the replacement mapping. The replacement mapping holds reference to a components python, script,
        and style elements along with the root replacement node.
        indent (int): The offset amount to every indent
        **kwargs (Any): Additional information that will be exposed to executed python blocks.
    """
    components = components or {}
    src = deepcopy(ast)

    # 1. Search for all python elements and get source info.
    #    - Remove when done
    vp = VirtualPython()

    for pb in find_all(src, {"tag": "python"}):
        if len(pb.children) == 1:
            if pb.children[0].type == "text":
                vp += VirtualPython(pb.children[0].value)

    remove_nodes(src, ["element", {"tag": "python"}])

    # 2. Replace specific element node with given replacement components
    replace_components(src, components, vp, **kwargs)

    for pb in find_all(src, {"tag": "python"}):
        if len(pb.children) == 1:
            if pb.children[0].type == "text":
                vp += VirtualPython(pb.children[0].value)

    remove_nodes(src, ["element", {"tag": "python"}])

    # 3. Search each element and find py-if, py-elif, py-else, and py-for
    #    - Execute those statements

    apply_conditions(src, vp, **kwargs)

    # 4. Search for python blocks and process them.

    apply_python(src, vp, **kwargs)

    return __to_html(src, indent)


def json(ast: AST, indent: int = 0) -> str:
    """Compile a given phml ast to a json string with a certain indent amount."""
    from json import dumps

    def compile_children(node: Root | Element) -> dict:
        data = {"type": node.type}

        if data["type"] == "root":
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


def markdown(ast: AST) -> str:
    """Compile a given phml ast to a markdown string with a certain indent amount."""
    raise NotImplementedError("Markdown is not supported.")


def __to_html(ast: AST, offset: int = 0) -> str:
    def compile_children(node: All_Nodes, indent: int = 0) -> list[str]:
        data = []
        if node.type == "element":
            if node.startend:
                data.append(" " * indent + node.start_tag())
            else:
                if (
                    len(node.children) == 1
                    and node.children[0].type == "text"
                    and node.children[0].num_lines == 1
                ):
                    data.append(
                        "".join(
                            [
                                " " * indent + node.start_tag(),
                                node.children[0].stringify(
                                    indent + offset if node.children[0].num_lines > 1 else 0
                                ),
                                node.end_tag(),
                            ]
                        )
                    )
                else:
                    data.append(" " * indent + node.start_tag())
                    for c in visit_children(node):
                        if c.type == "element":
                            data.extend(compile_children(c, indent + offset))
                        else:
                            data.append(c.stringify(indent + offset))
                    data.append(" " * indent + node.end_tag())
        elif node.type == "root":
            for child in visit_children(node):
                data.extend(compile_children(child))
        else:
            data.append(node.stringify(indent + offset))
        return data

    data = compile_children(ast.tree)

    return "\n".join(data)
