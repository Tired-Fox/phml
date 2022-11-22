from __future__ import annotations
from functools import cached_property
from typing import Iterator

__all__ = ["AST"]


class AST:
    """PHML ast.

    Contains utility functions that can manipulate the ast.
    """

    def __init__(self, tree):
        if hasattr(tree, "type") and tree.type in ["root", "element"]:
            self.tree = tree
        else:
            raise TypeError("The given tree/root node for AST must be of type `Root` or `Element`")

    def __iter__(self) -> Iterator:
        from phml.utils import walk
        
        return walk(self.tree)

    def __eq__(self, obj) -> bool:
        if isinstance(obj, self.__class__):
            if self.tree == obj.tree:
                return True
        return False

    @cached_property
    def size(self) -> int:
        """Get the number of nodes in the ast tree."""
        from phml.utils import size
        
        return size(self.tree)

    def inspect(self) -> str:
        """Return the full tree's inspect data."""
        return self.tree.inspect()
