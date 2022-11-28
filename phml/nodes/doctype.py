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
        lang: Optional[str] = None,
        parent: Optional[Element | Root] = None,
        position: Optional[Position] = None,
    ):
        super().__init__(position)
        self.parent = parent
        self.lang = lang

    def __eq__(self, obj) -> bool:
        if hasattr(obj, "type") and obj.type == self.type:
            if self.lang == obj.lang:
                return True
        # print(f"{self.__class__} != {obj.__class__}: {type(self).__name__} can not be equated to {type(obj).__name__}")
        return False

    def stringify(self, indent: int = 0) -> str:
        """Build indented html string of html doctype element.

        Returns:
            str: Built html of doctype element
        """
        return f"<!DOCTYPE {self.lang or 'html'}>"

    def __repr__(self) -> str:
        return f"node.doctype({self.lang or 'html'})"
