from typing import Optional, Iterator
from .node import Node
from .root import Root
from .element import Element
from .position import Position


class DocType(Node):
    """Doctype (Node) represents a DocumentType ([DOM]).

    Example:

    ```html
    <!doctype html>
    ```

    Yields:

    ```javascript
    {type: 'doctype'}
    ```
    """

    def __init__(
        self,
        parent: Optional[Element | Root] = None,
        position: Optional[Position] = None,
    ):
        super().__init__(position)
        self.parent = parent

    def __eq__(self, obj) -> bool:
        if hasattr(obj, "type") and obj.type == self.type:
            return True
        
        # print(f"{self.__class__} != {obj.__class__}: {type(self).__name__} can not be equated to {type(obj).__name__}")
        return False

    def as_dict(self) -> dict:
        """Convert root node to a dict."""

        return {"type": self.type, "value": "html"}

    def tree(self, depth: int = 0, prefix: str = "└") -> Iterator[str]:
        """Yields the tree representation of the node."""
        yield f"{' '*depth}{prefix} {self.type.upper()}  {self.position}"

    def inspect(self) -> str:
        """Return an inspected tree view of the node."""
        return "\n".join(self.tree())

    def html(self, indent: int = 4) -> str:
        """Convert doctype node to an html string."""
        return ""

    def json(self, indent: int = 2) -> str:
        """Convert doctype node to a json string."""
        from json import dumps  # pylint: disable=import-outside-toplevel

        return dumps(self.as_dict(), indent=indent)

    def phml(self, indent: int = 0) -> str:
        """Build indented html string of html doctype element.

        Returns:
            str: Built html of doctype element
        """
        return ' ' * indent + "<!DOCTYPE html>"

    def __str__(self) -> str:
        return "node.doctype()"
