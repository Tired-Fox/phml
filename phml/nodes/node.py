from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .position import Position


class Node:
    """All node values can be expressed in JSON as: string, number,
    object, array, true, false, or null. This means that the syntax tree should
    be able to be converted to and from JSON and produce the same tree.
    For example, in JavaScript, a tree can be passed through JSON.parse(JSON.phml(tree))
    and result in the same tree.
    """

    position: Position
    """The location of a node in a source document.
    The value of the position field implements the Position interface.
    The position field must not be present if a node is generated.
    """

    def __init__(
        self,
        position: Optional[Position] = None,
    ):
        self.position = position

    @property
    def type(self) -> str:
        """Non-empty string representing the variant of a node.
        This field can be used to determine the type a node implements."""
        return self.__class__.__name__.lower()
