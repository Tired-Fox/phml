from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional
from .parent import Parent

if TYPE_CHECKING:
    from .position import Position
    from .root import Root
    from .types import Properties
    from .comment import Comment
    from .text import Text


class Element(Parent):
    """Element (Parent) represents an Element ([DOM]).

    A tagName field must be present. It represents the element’s local name ([DOM]).

    The properties field represents information associated with the element. The value of the properties field implements the Properties interface.

    If the tagName field is 'template', a content field can be present. The value of the content field implements the Root interface.

    If the tagName field is 'template', the element must be a leaf.

    If the tagName field is 'noscript', its children should be represented as if scripting is disabled ([HTML]).


    For example, the following HTML:

    ```html
    <a href="https://alpha.com" class="bravo" download></a>
    ```

    Yields:

    ```javascript
    {
        type: 'element',
        tagName: 'a',
        properties: {
            href: 'https://alpha.com',
            className: ['bravo'],
            download: true
        },
        children: []
    }
    ```
    """

    def __init__(
        self,
        tag: str,
        properties: Optional[Properties],
        parent: Element | Root,
        content: Optional[Root] = None,
        openclose: bool = False
    ):
        super().__init__()
        self.content = content
        self.properties = properties
        self.tag = tag
        self.openclose = openclose
        self.parent = parent

    def tree(self, depth: int = 0, prefix: str = "└") -> str:
        yield f"{' '*depth}{prefix} {self.tag.upper()}"
        
        depth = 2 if depth == 0 else depth
        for i, child in enumerate(self.children):            
            prefix = f"{' '*(depth)}"
            if len(self.children) > 1:
                if i == len(self.children) - 1:
                    sep = f"└"
                else:
                    sep = f"├"
                    prefix = f"{' '*(depth)}│"
            else:
                sep = f"└"
            for i, line in enumerate(child.tree(2, sep)):
                if i == 0:
                    yield line
                else:
                    yield prefix + line

    def __repr__(self) -> str:
        out = f"{self.type}(tag: {self.tag}, properties: {self.properties}, children: "
        for child in self.children:
            out += repr(child) + "\n"
        out += ")"
        return out