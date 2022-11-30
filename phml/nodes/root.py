from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional

from .parent import Parent

if TYPE_CHECKING:
    from .comment import Comment
    from .doctype import DocType
    from .element import Element
    from .position import Position
    from .text import Text


class Root(Parent):
    """Root (Parent) represents a document.

    Root can be used as the root of a tree, or as a value
    of the content field on a 'template' Element, never as a child.
    """

    def __init__(
        self,
        position: Optional[Position] = None,
        children: Optional[list] = None,
    ):  # pylint: disable=useless-parent-delegation
        super().__init__(position, children)
        self.parent = None

    def __eq__(self, obj) -> bool:
        if obj is None:
            return False

        if hasattr(obj, "type") and self.type == obj.type:
            for c, oc in zip(self.children, obj.children):
                if c != oc:
                    return False
            return True
        else:
            return False

    def stringify(self) -> str:
        """Build indented html string of documents elements and their children.

        Returns:
            str: Built html of document
        """
        out = []
        out.extend([child.stringify() for child in self.children])
        return "\n".join(out)

    def __repr__(self) -> str:
        return f"root [{len(self.children)}]"
