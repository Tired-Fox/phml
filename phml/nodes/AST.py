# pylint: disable=invalid-name
"""Basic node that holds a root node and has basic utilties.

You can check the size of the tree, iterate over the tree, and directly access
the children of the root node.
"""

from __future__ import annotations

from functools import cached_property
from typing import Iterator

__all__ = ["AST"]


class AST:
    """PHML ast.

    Contains utility functions that can manipulate the ast.
    """

    def __init__(self, tree):
        if tree is not None and hasattr(tree, "type") and tree.type in ["root", "element"]:
            self.tree = tree
        else:
            raise TypeError("The given tree/root node for AST must be of type `Root` or `Element`")

    def __iter__(self) -> Iterator:
        from phml.utils import walk  # pylint: disable=import-outside-toplevel

        return walk(self.tree)

    def __eq__(self, obj) -> bool:
        if isinstance(obj, self.__class__):
            if self.tree == obj.tree:
                return True
        return False

    @cached_property
    def size(self) -> int:
        """Get the number of nodes in the ast tree."""
        from phml.utils import size  # pylint: disable=import-outside-toplevel

        return size(self.tree)

    @property
    def children(self) -> list:
        """Get access to the ast roots children.
        Is none if there is no root.
        """
        return self.tree.children if self.tree is not None else None
