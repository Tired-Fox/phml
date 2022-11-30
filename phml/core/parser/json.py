"""Helper method to parse a dict to a phml ast."""

from phml.nodes import Comment, DocType, Element, Point, Position, Root, Text

__all__ = ["json_to_ast"]


def construct_node_type(node_type: str):
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


def json_to_ast(json_obj: dict):
    """Convert a json object to a string."""

    def recurse(obj: dict):
        """Recursivly construct ast from json."""
        if 'type' in obj:
            val = construct_node_type(obj['type'])
            if val is not None:
                for key in obj:
                    if key not in ["children", "type", "position"] and hasattr(val, key):
                        setattr(val, key, obj[key])
                if 'children' in obj and hasattr(val, "children"):
                    for child in obj["children"]:
                        new_child = recurse(child)
                        new_child.parent = val
                        val.children.append(new_child)
                if 'position' in obj and hasattr(val, 'position') and obj["position"] is not None:
                    # start, end, indent
                    # line, column, offset
                    start = obj["position"]["start"]
                    end = obj["position"]["end"]
                    val.position = Position(
                        Point(start["line"], start["col"], start["offset"]),
                        Point(end["line"], end["col"], end["offset"]),
                        obj["position"]["indent"],
                    )
                return val
            raise Exception(f"Unkown node type <{obj['type']}>")
        raise Exception(
            'Invalid json for phml. Every node must have a type. Nodes may only have the types; \
root, element, doctype, text, or comment'
        )

    return recurse(json_obj)
