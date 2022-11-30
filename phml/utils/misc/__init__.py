"""phml.utils.misc

Helpful utilities for different tasks that doesn't have a place in the other categories.
"""

from phml.nodes import Element, Root

from .classes import *
from .component import *
from .heading import *
from .inspect import *

# __all__ = [
#     "depth",
#     "size",
#     "heading_rank",
#     "classnames",
#     "ClassList",
#     "inspect",
#     "normalize_indent",
# ]


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
