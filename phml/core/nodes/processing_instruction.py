from typing import Optional
from .node import Node
from .position import Position


class PI(Node):
    """A processing instruction node. Mainly used for XML."""

    def __init__(self, tag: str, properties: dict, position: Optional[Position] = None) -> None:
        super().__init__(position)
        self.tag = tag
        self.properties = properties

    def __repr__(self) -> str:
        return "<%s %r at %#x>" % (  # pylint: disable=consider-using-f-string
            self.__class__.__name__,
            self.tag,
            id(self),
        )

    def stringify(self, indent: int = 0):
        """Construct the string representation of the processing instruction node."""
        attributes = " ".join(f'{key}="{value}"' for key, value in self.properties.items())
        return f"<?{self.tag} {attributes}?>"
