from __future__ import annotations

from typing import TYPE_CHECKING
from .parent import Parent

if TYPE_CHECKING:
    from .position import Position
    from .element import Element
    from .doctype import DocType
    from .comment import Comment
    from .text import Text


class Root(Parent):
    """Root (Parent) represents a document.

    Root can be used as the root of a tree, or as a value
    of the content field on a 'template' Element, never as a child.
    """

    def __init__(
        self,
        position: Position,
        children: list[Element | DocType | Comment | Text],
    ):  # pylint: disable=useless-parent-delegation
        super().__init__(position, children)
