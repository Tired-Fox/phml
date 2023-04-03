from typing import Any, Callable, overload

from phml.nodes import Element, Parent, MISSING
from phml.utilities.validate.check import Test


class Index:
    """Uses the given key or key generator and creates a mutable dict of key value pairs
    that can be easily indexed.

    Nodes that don't match the condition or don't have a valid key are not indexed.
    """

    indexed_tree: dict[Any, list[Element]]
    """The indexed collection of elements"""

    def __init__(
        self,
        start: Parent,
        key: str | Callable[[Element], str],
        condition: Test | None = None
    ):
        """
        Args:
            `key` (str | Callable): Str represents the attribute to use as an index. Callable
            represents a function to call on each element to generate a key. The returned key
            must be able to be converted to a string. If none then element is skipped.
            `start` (Parent): The root or node to start at while indexing
            `test` (Test): The test to apply to each node. Only valid/passing nodes
            will be indexed
        """
        from phml.utilities import check, walk  # pylint: disable=import-outside-toplevel
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

    def __contains__(self, _key: str) -> bool:
        return _key in self.indexed_tree

    def __str__(self):
        return str(self.indexed_tree)

    def items(self): # pragma: no cover
        """Get the key value pairs of all indexes."""
        return self.indexed_tree.items()

    def values(self): # pragma: no cover
        """Get all the values in the collection."""
        return self.indexed_tree.values()

    def keys(self): # pragma: no cover
        """Get all the keys in the collection."""
        return self.indexed_tree.keys()

    def add(self, node: Element):
        """Adds element to indexed collection if not already there."""

        key = node.get(self.key, "") if isinstance(self.key, str) else self.key(node)
        if key not in self.indexed_tree:
            self.indexed_tree[key] = [node]

        if node not in self.indexed_tree[key]:
            self.indexed_tree[key].append(node)

    def remove(self, node: Element):
        """Removes element from indexed collection if there."""

        key = self.key if isinstance(self.key, str) else self.key(node)
        if key in self.indexed_tree and node in self.indexed_tree[key]:
            self.indexed_tree[key].remove(node)
            if len(self.indexed_tree[key]) == 0:
                self.indexed_tree.pop(key, None)

    def __getitem__(self, key: Any) -> list[Element]:
        return self.indexed_tree[key]

    @overload
    def get(self, _key: str, _default: Any = MISSING) -> list[Element] | Any:
        ...

    @overload
    def get(self, _key: str) -> list[Element] | None:
        ...

    def get(self, _key: str, _default: Any = MISSING) -> list[Element] | None: # pragma: no cover
        """Get a specific index from the indexed tree."""
        if _default != MISSING:
            return self.indexed_tree.get(_key, _default)
        return self.indexed_tree.get(_key, None)

    # Built in key functions

    @staticmethod
    def key_by_tag(node: Element) -> str:
        """Builds the key from an elements tag. If the node is not an element
        then the node's type is returned."""

        return node.tag

