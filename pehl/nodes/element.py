from __future__ import annotations

from typing import TYPE_CHECKING, Optional
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
        position: Position,
        children: list[Element | Comment | Text],
        content: Optional[Root],
        properties: Optional[Properties],
        tag_name: str,
    ):
        super().__init__(position, children)
        self.content = content
        self.properties = properties
        self.tag_name = tag_name
