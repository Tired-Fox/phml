"""Utility functions that do something with heading tags."""
from re import match

from phml.nodes import Element

__all__ = ["heading_rank"]


def heading_rank(node: Element) -> int:
    """Get the rank of the heading element.

    Example:
        `h2` yields `2`
    """
    from phml.utils import is_heading  # pylint: disable=import-outside-toplevel

    if is_heading(node):
        rank = match(r"h([1-6])", node.tag).group(1)
        return int(rank)

    if isinstance(node, Element):
        raise TypeError(f"Node must be a heading. Was a {node.type}.{node.tag}")
    else:
        raise TypeError(f"Node must be an element. Was a {node.type}")
