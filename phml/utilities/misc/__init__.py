"""phml.utilities.misc

Helpful utilities for different tasks that doesn't have a place in the other categories.
"""

from phml.nodes import Parent

from .classes import *
from .heading import *


def depth(node) -> int:
    """Get the depth in the tree for a given node.

    -1 means that you passed in the tree itself and you are at the
    ast's root.
    """

    level = -1
    while node.parent is not None:
        level += 1
        node = node.parent

    return level


def size(node: Parent) -> int:
    """Get the number of nodes recursively."""
    from phml.utilities import walk  # pylint: disable=import-outside-toplevel

    count = 0

    for _ in walk(node):
        count += 1

    return count
