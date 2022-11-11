from phml.nodes import All_Nodes, Root, Element, Text, Comment


def validate(node: All_Nodes) -> bool:
    """Validate a node based on attributes and type."""

    if hasattr(node, "children"):
        if not hasattr(node, "type"):
            raise AssertionError("Node should be have a type")
        elif node.type not in ["root", "element"]:
            raise AssertionError(
                "Node should have a type of 'root' or 'element' to contain the 'children' attribute"
            )
        else:
            for n in node.children:
                if not isinstance(n, All_Nodes):
                    raise AssertionError("Children must be a node type")
    if hasattr(node, "properties"):
        if hasattr(node, type) and node.type != "element":
            raise AssertionError("Node must be of type 'element' to contain 'properties'")
        else:
            for prop in node.properties:
                if not isinstance(node.properties[prop], (int, str)):
                    raise AssertionError("Node 'properties' must be of type 'int' or 'str'")
    if hasattr(node, "value"):
        if not isinstance(node.value, str):
            raise AssertionError("Node 'value' must be of type 'str'")


def parent(node: Root | Element) -> bool:
    """Validate a parent node based on attributes and type."""
    if not hasattr(node, "children"):
        raise AssertionError("Parent nodes should have the 'children' attribute")
    elif node.type == "element" and not hasattr(node, "properties"):
        raise AssertionError("Parent element node shoudl have the 'properties' element.")


def literal(node: Text | Comment) -> bool:
    """Validate a literal node based on attributes."""

    if hasattr(node, "value"):
        if not isinstance(node, str):
            raise AssertionError("Literal nodes 'value' type should be 'str'")
