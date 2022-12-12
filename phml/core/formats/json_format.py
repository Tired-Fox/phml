from json import dumps, loads
from typing import Optional

from phml.core.nodes import AST, All_Nodes, Comment, DocType, Element, Position, Root, Text
from phml.utilities import visit_children

from .format import Format


def __construct_node_type(node_type: str):
    """Takes a node type and returns a base constructed instance of the node."""
    if node_type == "root":
        return Root()

    if node_type == "element":
        return Element()

    if node_type == "doctype":
        return DocType()

    if node_type == "text":
        return Text()

    if node_type == "comment":
        return Comment()

    return None


def __construct_attributes(node, obj):
    for key in obj:
        if key not in ["children", "type", "position", "num_lines"] and hasattr(node, key):
            setattr(node, key, obj[key])


def __construct_children(node, obj):
    for child in obj["children"]:
        new_child = construct_tree(child)
        new_child.parent = node
        node.children.append(new_child)


def __construct_position(node, obj):
    start = obj["position"]["start"]
    end = obj["position"]["end"]
    node.position = Position(
        (start["line"], start["column"], start["offset"]),
        (end["line"], end["column"], end["offset"]),
        obj["position"]["indent"],
    )


def __construct_node(node, obj):
    __construct_attributes(node, obj)

    if 'children' in obj and hasattr(node, "children"):
        __construct_children(node, obj)

    if 'position' in obj and hasattr(node, 'position') and obj["position"] is not None:
        __construct_position(node, obj)

    return node


def construct_tree(obj: dict):
    """Recursivly construct ast from json."""
    if 'type' not in obj:
        raise Exception(
            'Invalid json for phml. Every node must have a type. Nodes may only have the types; \
root, element, doctype, text, or comment'
        )

    val = __construct_node_type(obj['type'])
    if val is None:
        raise Exception(f"Unkown node type <{obj['type']}>")

    return __construct_node(val, obj)


class JSONFormat(Format):
    """Logic for parsing and compiling html files."""

    extension: str = "json"

    @classmethod
    def parse(cls, data: dict | str) -> str:
        if isinstance(data, str):
            data = loads(data)

        if isinstance(data, dict):
            node = construct_tree(data)
            if not isinstance(node, Root):
                node = Root(children=[node])
            return AST(node)

        raise Exception("Data passed to JSONFormat.parse must be either a str or a dict")

    @classmethod
    def compile(
        cls,
        ast: AST,
        components: Optional[dict[str, dict[str, list | All_Nodes]]] = None,
        indent: int = 2,
        **kwargs,
    ) -> str:
        indent = indent or 2

        def compile_children(node: Root | Element) -> dict:
            data = {"type": node.type}

            if node.type == "root":
                if node.parent is not None:
                    raise Exception("Root nodes must only occur as the root of an ast/tree")

            for attr in vars(node):
                if attr not in ["parent", "children", "num_lines"]:
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
