from __future__ import annotations

from typing import Optional

from .parent import Parent
from .position import Position


class Root(Parent):
    """Root (Parent) represents a document.

    Root can be used as the root of a tree, or as a value
    of the content field on a 'template' Element, never as a child.
    """

    def __init__(
        self,
        position: Optional[Position] = None,
        children: Optional[list] = None,
    ):
        super().__init__(position, children)
        self.parent = None

    def __eq__(self, obj) -> bool:
        return bool(
            obj is not None
            and isinstance(obj, Root)
            and len(self.children) == len(obj.children)
            and all(child == obj_child for child, obj_child in zip(self.children, obj.children))
        )

    def __repr__(self) -> str:
        return f"root [{len(self.children)}]"
