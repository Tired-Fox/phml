from typing import Iterator


def path(node) -> list:
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
        ancestors.insert(0, node.parent)
        node = node.parent

    return ancestors


def walk(node) -> Iterator:
    """Recursively traverse the node and it's chidlren as an iterator.
    Left to right depth first.
    """

    def get_children(parent) -> Iterator:
        yield parent
        if parent.type in ["root", "element"]:
            for child in parent.children:
                yield from get_children(child)

    if node.type in ["root", "element"]:
        for child in visit_children(node):
            yield from get_children(child)
    else:
        yield node


def visit_children(parent) -> Iterator:
    """Traverse the children as an iterator."""
    for child in parent.children:
        yield child


def visit_all_after(start) -> Iterator:
    """Recursively traverse the tree starting at given node."""

    def get_children(parent) -> Iterator:
        yield parent
        if parent.type in ["root", "element"]:
            for child in parent.children:
                yield from get_children(child)

    parent = start.parent
    for child in visit_children(parent):
        if child is not start:
            yield from get_children(child)
