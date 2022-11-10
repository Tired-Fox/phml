from typing import Iterator
from .node import Node


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

    def tree(self, depth: int = 0, prefix: str = "└") -> Iterator[str]:
        """Yields the tree representation of the node."""
        yield f"{' '*depth}{prefix} {self.type.upper()}"

    def as_dict(self) -> dict:
        """Convert root node to a dict."""

        return {
            "type": self.type,
            "value": "html"
        }

    def html(self, indent: int = 4) -> str:
        """Convert doctype node to an html string."""
        return ""

    def json(self, indent: int = 2) -> str:
        """Convert doctype node to a json string."""
        from json import dumps #pylint: disable=import-outside-toplevel

        return dumps(self.as_dict(), indent=indent)

    def phml(self, indent: int = 0) -> str:
        """Build indented html string of html doctype element.

        Returns:
            str: Built html of doctype element
        """
        return ' '*indent + str(self)

    def __str__(self) -> str:
        return "<!DOCTYPE html>"
