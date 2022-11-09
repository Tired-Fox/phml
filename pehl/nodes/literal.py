from typing import TYPE_CHECKING
from .node import Node
from .position import Position


class Literal(Node):
    """Literal (UnistLiteral) represents a node in hast containing a value."""

    position: Position
    """The location of a node in a source document.
    The value of the position field implements the Position interface.
    The position field must not be present if a node is generated.
    """

    value: str
    """The Literal nodes value. All literal values must be strings"""

    def __init__(
        self,
        position: Position,
        value: str,
    ):
        super().__init__(position)
        self.value = value
