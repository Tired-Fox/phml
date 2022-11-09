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
        yield f"{' '*depth}{prefix} {self.type.upper()}"
    
    def pehl(self, indent: int = 0) -> str:
        """Build indented html string of html doctype element.

        Returns:
            str: Built html of doctype element
        """
        return ' '*indent + str(self)
    
    def __str__(self) -> str:
        return f"<!DOCTYPE html>"
