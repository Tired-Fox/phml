from __future__ import annotations
from functools import cached_property

from typing import TYPE_CHECKING, Iterator, Optional
from .nodes import (
    Root,
    Element,
)  # , Node, DocType, Parent, Literal, Comment, Text, Position, Point, Properties, PropertyName, PropertyValue

from .utils import Test, test

if TYPE_CHECKING:
    from phml import All_Nodes


class AST:
    """PHML ast.

    Contains utility functions that can manipulate the ast.
    """

    def __init__(self, tree: Root | Element):
        self.tree = tree

    def __iter__(self) -> Iterator:
        return self.walk()

    @cached_property
    def size(self) -> int:
        """Get the number of nodes in the ast tree."""
        size = 0
        for _ in self.walk():
            size += 1
        return size

    def inspect(self) -> str:
        """Return an inspected tree view of the ast."""
        return self.tree.inspect()

    def walk(self) -> Iterator:
        """Recursively traverse the tree as an iterator.
        Left to right depth first.
        """

        def get_children(parent: All_Nodes) -> Iterator:
            yield parent
            if isinstance(parent, Root) or isinstance(parent, Element):
                for child in parent.children:
                    yield from get_children(child)

        for child in self.visit_children(self.tree):
            yield from get_children(child)

    def visit_children(self, parent: Root | Element) -> Iterator:
        """Traverse the children as an iterator."""
        for child in parent.children:
            yield child

    def visit_all_after(self, start: All_Nodes) -> Iterator:
        """Recursively traverse the tree starting at given node."""

        def get_children(parent: All_Nodes) -> Iterator:
            yield parent
            if isinstance(parent, Root) or isinstance(parent, Element):
                for child in parent.children:
                    yield from get_children(child)

        if start is self.tree:
            yield from self.walk()
        else:
            parent = start.parent
            for child in self.visit_children(parent):
                if child is not start:
                    yield from get_children(child)

    def find(self, condition: Test) -> Optional[All_Nodes]:
        """Walk the tree and return the desired node.

        Returns the first node that matches the condition.

        Args:
            condition (Test): Condition to check against each node.

        Returns:
            Optional[All_Nodes]: Returns the found node or None if not found.
        """

        for node in self.walk():
            if test(node, condition):
                return node

        return None

    def find_after(
        self,
        node: All_Nodes,
        condition: Optional[Test] = None,
    ) -> Optional[All_Nodes]:
        """Get the first sibling node.

        Args:
            node (All_Nodes): Node to get sibling from.
            condition (Test): Condition to check against each node.

        Returns:
            Optional[All_Nodes]: Returns the first sibling or None if there
            are no siblings.
        """

        idx = node.parent.children.index(node)
        if len(node.parent.children) - 1 > idx:
            for el in node.parent.children[idx + 1 :]:
                if condition is not None:
                    return el if test(node, condition) else None
                return el
        return None

    def find_all_after(
        self,
        node: All_Nodes,
        condition: Optional[Test] = None,
    ) -> Optional[All_Nodes]:
        """Get the all sibling nodes.

        Args:
            node (All_Nodes): Node to get siblings from.
            condition (Test): Condition to check against each node.

        Returns:
            Optional[All_Nodes]: Returns the all siblings that match the
            condition or an empty list if none were found.
        """

        idx = node.parent.children.index(node)

        matches = []

        if len(node.parent.children) - 1 > idx:
            for el in node.parent.children[idx + 1 :]:
                if condition is not None:
                    if test(node, condition):
                        matches.append(el)
                matches.append(el)
        return matches

    def depth(self, el: All_Nodes) -> int:
        """Get the depth in the tree for a given node.

        -1 means that you passed in the tree itself and you are at the
        ast's root.
        """
        depth = -1
        while el.parent is not None:
            depth += 1
            el = el.parent

        return depth

    def to_phml(self) -> str:
        """Get the ast as a phml string."""
        return self.tree.phml()

    def to_json(self) -> str:
        """Get the ast as a json string."""
        return self.tree.json()

    def to_html(self) -> str:
        """Get the ast as a rendered html string."""
        return ""
