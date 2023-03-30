"""utilities.travel

Collection of utilities that hep with traversing an ast or node tree.
"""

from typing import Iterator

from phml.nodes import Node, Element, Parent 

__all__ = ["path", "path_names", "walk", "visit_all_after"]


def path(node: Node) -> list[Node]:
    """Get a list of nodes where each one is a child of
    the other leading to the node passed in. This gives a
    path to the node.

    Does not include given node.

    Args:
        node (Node): Node to find ancestors of.

    Returns:
        list[Node]: List of nodes leading to the given node
        starting from the root.
    """
    ancestors = []
    while node.parent is not None:
        ancestors = [node.parent, *ancestors]
        node = node.parent

    return ancestors

def path_names(node: Node) -> list[str]:
    """Get a list of nodes where each one is a child of
    the other leading to the node passed in. This gives a
    path to the node.

    Does not include given node.

    Args:
        node (Node): Node to find ancestors of.

    Returns:
        list[str]: List of nodes leading to the given node
        starting from the root.
    """
    ancestors = []
    while node.parent is not None and isinstance(node.parent, Element):
        ancestors = [node.parent.tag, *ancestors]
        node = node.parent

    return ancestors


def walk(node: Parent) -> Iterator:
    """Recursively traverse the node and it's chidlren as an iterator.
    Left to right depth first.
    """

    def get_children(n: Node) -> Iterator:
        yield n
        if isinstance(n, Parent) and len(n) > 0:
            for child in n:
                yield from get_children(child)

    yield node
    if isinstance(node, Parent) and len(node) > 0:
        for child in node:
            yield from get_children(child)


def visit_all_after(start: Node) -> Iterator:
    """Recursively traverse the tree starting at given node."""

    def get_children(parent) -> Iterator:
        yield parent
        if parent.type in ["root", "element"]:
            for child in parent.children:
                yield from get_children(child)

    parent = start.parent
    if parent is not None:
        idx = parent.index(start)
        if idx < len(parent) - 1:
            for child in parent[idx + 1 :]:
                yield from get_children(child)
