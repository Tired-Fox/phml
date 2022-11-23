from phml.nodes import All_Nodes, Root, Element, Text, AST, Comment
from phml.builder import p


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

    def concat_text(el: Element | Root) -> list[str]:
        result = []

        for child in el.children:
            if isinstance(child, (Element, Root)):
                result.extend(concat_text(child))
            elif isinstance(child, Text):
                result.append(child.value)
        return result

    if isinstance(node, Root | Element):
        # Recursive concat
        return "".join(concat_text(node))

    return None