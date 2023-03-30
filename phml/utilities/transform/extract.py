from phml.nodes import AST, Node, Element, Parent, Literal, LiteralType

__all__ = ["to_string"]


def to_string(node: Node) -> str:
    """Get the raw text content of the element. Works similar to
    the DOMs Node#textContent getter.

    Args:
        node (Root | Element | Text): Node to get the text content from

    Returns:
        str: Raw inner text without formatting.
    """

    if isinstance(node, Literal):
        return node.content

    def concat_text(element: Parent) -> list[str]:
        result = []

        for child in element:
            if isinstance(child, Parent):
                result.extend(concat_text(child))
            elif Literal.is_text(child):
                result.append(child.content)
        return result

    if isinstance(node, Parent):
        # Recursive concat
        return " ".join(concat_text(node))

    return ""
