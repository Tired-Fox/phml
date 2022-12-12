from typing import Callable, Optional

from phml.core.nodes import AST, Element, Root
from phml.utilities.validate.check import Test


class Index:
    """Uses the given key or key generator and creates a mutable dict of key value pairs
    that can be easily indexed.

    Nodes that don't match the condition or don't have a valid key are not indexed.
    """

    indexed_tree: dict[str, list[Element]]
    """The indexed collection of elements"""

    def __init__(
        self, key: str | Callable, start: AST | Root | Element, condition: Optional[Test] = None
    ):
        """
        Args:
            `key` (str | Callable): Str represents the property to use as an index. Callable
            represents a function to call on each element to generate a key. The returned key
            must be able to be converted to a string. If none then element is skipped.
            `start` (AST | Root | Element): The root or node to start at while indexing
            `test` (Test): The test to apply to each node. Only valid/passing nodes
            will be indexed
        """
        from phml import check, walk  # pylint: disable=import-outside-toplevel

        if isinstance(start, AST):
            start = start.tree

        self.indexed_tree = {}
        self.key = key

        for node in walk(start):
            if isinstance(node, Element):
                if condition is not None:
                    if check(node, condition):
                        self.add(node)
                else:
                    self.add(node)

    def __iter__(self):
        return iter(self.indexed_tree)

    def items(self) -> tuple[str, list]:
        """Get the key value pairs of all indexes."""
        return self.indexed_tree.items()

    def values(self) -> list[list]:
        """Get all the values in the collection."""
        return self.indexed_tree.values()

    def keys(self) -> list[str]:
        """Get all the keys in the collection."""
        return self.indexed_tree.keys()

    def add(self, node: Element):
        """Adds element to indexed collection if not already there."""

        key = node[self.key] if isinstance(self.key, str) else self.key(node)
        if key not in self.indexed_tree:
            self.indexed_tree[key] = [node]

        if node not in self.indexed_tree[key]:
            self.indexed_tree[key].append(node)

    def remove(self, node: Element):
        """Removes element from indexed collection if there."""

        key = node[self.key] if isinstance(self.key, str) else self.key(node)
        if key in self.indexed_tree and node in self.indexed_tree[key]:
            self.indexed_tree[key].remove(node)
            if len(self.indexed_tree[key]) == 0:
                self.indexed_tree.pop(key, None)

    def get(self, _key: str) -> Optional[list[Element]]:
        """Get a specific index from the indexed tree."""
        return self.indexed_tree.get(_key)

    # Built in key functions

    @classmethod
    def key_by_tag(cls, node: Element) -> str:
        """Builds the key from an elements tag. If the node is not an element
        then the node's type is returned."""

        return node.tag
