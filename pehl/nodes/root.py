from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional
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
        position: Optional[Position] = None,
    ):  # pylint: disable=useless-parent-delegation
        super().__init__(position)
        self.parent = None
        
    def tree(self) -> Iterator[str]:
        result = ["ROOT"]
        for i, child in enumerate(self.children):
            if len(self.children) > 1:
                if i == len(self.children) - 1:
                    sep = f"└"
                else:
                    sep = f"├"
            else:
                sep = f"└"
            for line in child.tree(0, sep):
                result.append(line)
        
        return "\n".join(result)
        
    def __str__(self) -> str:
        return "\n".join(self.tree())
