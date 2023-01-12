from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .node import Node

if TYPE_CHECKING:
    from . import All_Nodes
    from .comment import Comment
    from .doctype import DocType
    from .element import Element
    from .position import Position
    from .text import Text


class Parent(Node):  # pylint: disable=too-few-public-methods
    """Parent (UnistParent) represents a node in hast containing other nodes (said to be children).

    Its content is limited to only other hast content.
    """

    def __init__(self, position: Optional[Position] = None, children: Optional[list] = None):
        super().__init__(position)

        if children is not None:
            for child in children:
                if hasattr(child, "type") and child.type in [
                    "element",
                    "text",
                    "doctype",
                    "root",
                    "comment",
                ]:
                    child.parent = self

        self.children: list[Element | DocType | Comment | Text] = children or []

    def append(self, node: All_Nodes):
        """Add a node to the nested children of the current parent node."""
        node.parent = self
        self.children.append(node)
        
    def extend(self, nodes: list[All_Nodes]):
        """Add a node to the nested children of the current parent node."""
        for node in nodes:
            self.append(node)

    def insert(self, index: int, node: All_Nodes):
        """Insert a node into a specific position in the current parent node's children."""
        node.parent = self
        self.children.insert(index, node)

    def remove(self, node: All_Nodes):
        """Remove a specific node from the current parent node's children."""
        self.children.remove(node)
