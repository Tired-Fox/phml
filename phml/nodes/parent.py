# pylint: disable=missing-module-docstring
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .node import Node

if TYPE_CHECKING:
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
                child.parent = self

        self.children: list[Element | DocType | Comment | Text] = children or []
