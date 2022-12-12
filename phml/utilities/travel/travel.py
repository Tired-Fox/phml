"""utilities.travel

Collection of utilities that hep with traversing an ast or node tree.
"""

from typing import Iterator

from phml.core.nodes import All_Nodes, Element, Root

__all__ = ["path", "walk", "visit_children", "visit_all_after"]


def path(node: All_Nodes) -> list[All_Nodes]:
    """Get a list of nodes where each one is a child of
    the other leading to the node passed in. This gives a
    path to the node.

    Does not include given node.

    Args:
        node (All_Nodes): Node to find ancestors of.

    Returns:
        list[All_Nodes]: List of nodes leading to the given node
        starting from the root.
    """
    ancestors = []
    while node.parent is not None:
        ancestors = [node.parent, *ancestors]
        node = node.parent

    return ancestors


def walk(node: Root | Element) -> Iterator:
    """Recursively traverse the node and it's chidlren as an iterator.
    Left to right depth first.
    """

    def get_children(parent) -> Iterator:
        yield parent
        if parent.type in ["root", "element"]:
            for child in parent.children:
                yield from get_children(child)

    yield node
    if node.type in ["root", "element"]:
        for child in visit_children(node):
            yield from get_children(child)


def visit_children(parent: Root | Element) -> Iterator:
    """Traverse the children of a Root or Element as an iterator."""
    for child in parent.children:
        yield child


def visit_all_after(start: All_Nodes) -> Iterator:
    """Recursively traverse the tree starting at given node."""

    def get_children(parent) -> Iterator:
        yield parent
        if parent.type in ["root", "element"]:
            for child in parent.children:
                yield from get_children(child)

    parent = start.parent
    idx = parent.children.index(start)
    if idx < len(parent.children) - 1:
        for child in parent.children[idx + 1 :]:
            yield from get_children(child)
