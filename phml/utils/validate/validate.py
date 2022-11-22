from re import match, split, sub

from phml.nodes import All_Nodes, Root, Element, Text, Comment

__all__ = [
    "validate",
    "parent",
    "literal",
    "generated",
    "has_property",
    "is_heading",
    "is_css_link",
    "is_css_style",
    "is_javascript",
    "is_element",
    "is_event_handler"
]


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


def generated(node: All_Nodes) -> bool:
    """Checks if a node has been generated. A node is concidered
    generated if it does not have a position.

    Args:
        node (All_Nodes): Node to check for position with.

    Returns:
        bool: Whether a node has a position or not.
    """
    return hasattr(node, "position") and node.position is not None


def is_heading(node) -> bool:
    """Check if an element is a heading."""

    return node.type == "element" and match(r"h[1-6]", node.tag) is not None


def is_css_link(node) -> bool:
    """Check if an element is a `link` to a css file.

    Returns `true` if `node` is a `<link>` element with a `rel` list that
    contains `'stylesheet'` and has no `type`, an empty `type`, or `'text/css'`
    as its `type`
    """

    return (
        # Verify it is a element with a `link` tag
        is_element(node, "link")
        # Must have a rel list with stylesheet
        and has_property(node, "rel")
        and "stylesheet" in split(r" ", sub(r" +", " ", node.properties["rel"]))
        and (
            # Can have a `type` of `text/css` or empty or no `type`
            not has_property(node, "type")
            or (
                has_property(node, "type")
                and (node.properties["type"] == "text/css" or node.properties["type"] == "")
            )
        )
    )


def is_css_style(node) -> bool:
    """Check if an element is a css `style` element.

    Returns `true` if `node` is a `<style>` element that
    has no `type`, an empty `type`, or `'text/css'` as its `type`.
    """

    return is_element(node, "style") and (
        not has_property(node, "type")
        or (
            has_property(node, "type")
            and (node.properties["type"] == "" or node.properties["type"] == "text/css")
        )
    )


def is_javascript(node) -> bool:
    """Check if an element is a javascript `script` element.

    Returns `true` if `node` is a `<script>` element that has a valid JavaScript `type`, has no `type` and a valid JavaScript `language`, or has neither.
    """
    return is_element(node, "script") and (
        (
            has_property(node, "type")
            and node.properties["type"] in ["text/ecmascript", "text/javascript"]
            and not has_property(node, "language")
        )
        or (
            has_property(node, "language")
            and node.properties["language"] in ["ecmascript", "javascript"]
            and not has_property(node, "type")
        )
        or (not has_property(node, "type") and not has_property(node, "language"))
    )


def is_element(node, condition: str | list) -> bool:
    """Checks if the given node is a certain element.

    When providing an str it will check that the elements tag matches.
    If a list is provided it checks that one of the conditions in the list
    passes.
    """

    if node.type != "element":
        return False

    if isinstance(condition, str):
        return node.tag == condition
    elif isinstance(condition, list):
        for c in condition:
            if node.tag == c:
                return True
        return False


def is_event_handler(attribute: str) -> bool:
    """Takes a attribute name and returns true if
    it starts with `on` and its length is `5` or more.
    """
    return attribute.startswith("on") and len(attribute) >= 5


def has_property(node, attribute: str) -> bool:
    """Check to see if an element has a certain property in properties."""
    if node.type == "element":
        if attribute in node.properties:
            return True
    return False
