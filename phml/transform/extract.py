from phml.nodes import AST, All_Nodes, Comment, Element, Root, Text

__all__ = ["to_string"]


def to_string(node: AST | All_Nodes) -> str:
    """Get the raw text content of the element. Works similar to
    the DOMs Node#textContent getter.

    Args:
        node (Root | Element | Text): Node to get the text content from

    Returns:
        str: Raw inner text without formatting.
    """

    if isinstance(node, AST):
        node = node.tree

    if isinstance(node, Text | Comment):
        return node.value

    def concat_text(element: Element | Root) -> list[str]:
        result = []

        for child in element.children:
            if isinstance(child, (Element, Root)):
                result.extend(concat_text(child))
            elif isinstance(child, Text):
                result.append(child.value)
        return result

    if isinstance(node, Root | Element):
        # Recursive concat
        return " ".join(concat_text(node))

    return None
