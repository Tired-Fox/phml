"""phml.utilities.misc

Helpful utilities for different tasks that doesn't have a place in the other categories.
"""

from phml.core.nodes import Element, Root

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


def size(node: Root | Element) -> int:
    """Get the number of nodes recursively."""
    from phml import walk  # pylint: disable=import-outside-toplevel

    count = 0

    for _ in walk(node):
        count += 1

    return count


def offset(content: str | list[str]) -> int:
    """Get the leading offset of the first line of the string."""
    content = content.split("\n") if isinstance(content, str) else content
    return len(content[0]) - len(content[0].lstrip())
