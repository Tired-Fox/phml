# pylint: disable=missing-module-docstring
from typing import Optional

from .element import Element
from .node import Node
from .position import Position
from .root import Root


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
        lang: Optional[str] = None,
        parent: Optional[Element | Root] = None,
        position: Optional[Position] = None,
    ):
        super().__init__(position)
        self.parent = parent
        self.lang = lang or 'html'

    def __eq__(self, obj) -> bool:
        if obj is None:
            return False

        if hasattr(obj, "type") and obj.type == self.type:
            if self.lang == obj.lang:
                return True
        return False

    def stringify(self, indent: int = 0) -> str:  # pylint: disable=unused-argument
        """Build indented html string of html doctype element.

        Returns:
            str: Built html of doctype element
        """
        return f"<!DOCTYPE {self.lang or 'html'}>"

    def __repr__(self) -> str:
        return f"node.doctype({self.lang or 'html'})"
