from typing import Optional
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
        value: str,
        position: Optional[Position] = None,
    ):
        super().__init__(position)
        self.value = value

    def as_dict(self) -> dict:
        """Convert literal node to a dict."""

        return {
            "type": self.type,
            "value": self.value
        }

    def html(self, indent: int = 4) -> str:
        """Convert literal node to an html string."""
        return ""

    def json(self, indent: int = 2) -> str:
        """Convert literal node to a json string."""
        from json import dumps #pylint: disable=import-outside-toplevel

        return dumps(self.as_dict(), indent=indent)
