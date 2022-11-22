from phml.nodes import Root, Element
from .classes import *
from .heading import *

__all__ = ["depth", "size", "heading_rank", "classnames", "ClassList"]


def depth(el) -> int:
    """Get the depth in the tree for a given node.

    -1 means that you passed in the tree itself and you are at the
    ast's root.
    """

    level = -1
    while el.parent is not None:
        level += 1
        el = el.parent

    return level


def size(node: Root | Element) -> int:
    """Get the number of nodes recursively."""
    from phml.utils import walk
    
    count = 0

    for _ in walk(node):
        count += 1

    return count
