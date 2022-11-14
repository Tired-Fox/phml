from __future__ import annotations
from functools import cached_property
from typing import Iterator
from phml import VPElement, get_vp_result, process_vp_blocks

from .nodes import (
    Root,
    Element,
)  # , Node, DocType, Parent, Literal, Comment, Text, Position, Point, Properties, PropertyName, PropertyValue

from .utils.transform import walk, size


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

    def to_phml(self) -> str:
        """Get the ast as a phml string."""
        return self.tree.phml()

    def to_json(self) -> str:
        """Get the ast as a json string."""
        return self.tree.json()

    def to_html(self) -> str:
        """Get the ast as a rendered html string."""
        return self.tree.html()
        # 1. Search each scope for python element and add it to outer scope
        # 2. Search each scope for conditions and process conditions
        # 3. Search each scope for for-loop conditions and execute them
        # 4. Take the final manipulated tree and print out
