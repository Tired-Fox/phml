"""Helper method to parse a dict to a phml ast."""

from phml.core.nodes import Comment, DocType, Element, Position, Root, Text

__all__ = ["json_to_ast"]


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
        if key not in ["children", "type", "position"] and hasattr(node, key):
            setattr(node, key, obj[key])


def __construct_children(node, obj):
    for child in obj["children"]:
        new_child = __construct_tree(child)
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


def __construct_tree(obj: dict):
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


def json_to_ast(json_obj: dict):
    """Convert a json object to a string."""

    return __construct_tree(json_obj)
