# pylint: disable=missing-module-docstring
from typing import Optional

from .element import Element
from .node import Node
from .position import Position
from .root import Root


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
        value: str = "",
        parent: Optional[Element | Root] = None,
        position: Optional[Position] = None,
    ):
        super().__init__(position)
        self.value = value
        self.parent = parent

    def __eq__(self, obj) -> bool:
        return bool(obj is not None and self.type == obj.type and self.value == obj.value)

    def __repr__(self) -> str:
        return f"{self.type}(value:{len(self.value)})"

    def get_ancestry(self) -> list[str]:
        """Get the ancestry of the literal node.

        Used to validate whether there is a `pre` element in the ancestry.
        """

        def get_parent(parent) -> list[str]:
            result = []

            if parent is not None and hasattr(parent, "tag"):
                result.append(parent.tag)

            if parent.parent is not None:
                result.extend(get_parent(parent.parent))

            return result

        return get_parent(self.parent)
