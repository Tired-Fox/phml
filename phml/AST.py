from __future__ import annotations
from functools import cached_property
from typing import Iterator

from phml.nodes import (
    Root,
    Element,
)  # , Node, DocType, Parent, Literal, Comment, Text, Position, Point, Properties, PropertyName, PropertyValue

from phml.utils.transform import walk, size

__all__ = ["AST"]


class AST:
    """PHML ast.

    Contains utility functions that can manipulate the ast.
    """

    def __init__(self, tree: Root | Element):
        self.tree = tree

    def __iter__(self) -> Iterator:
        return walk(self.tree)

    def __eq__(self, obj) -> bool:
        if isinstance(obj, self.__class__):
            if self.tree == obj.tree:
                return True

        return False

    @cached_property
    def size(self) -> int:
        """Get the number of nodes in the ast tree."""

        size(self.tree)

    def inspect(self) -> str:
        """Return the full tree's inspect data."""
        return self.tree.inspect()
