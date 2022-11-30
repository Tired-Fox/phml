from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .parent import Parent

if TYPE_CHECKING:
    from .position import Position
    from .root import Root
    from .types import Properties


class Element(Parent):
    """Element (Parent) represents an Element ([DOM]).

    A tagName field must be present. It represents the element's local name ([DOM]).

    The properties field represents information associated with the element.
    The value of the properties field implements the Properties interface.

    If the tagName field is 'template', a content field can be present. The value
    of the content field implements the Root interface.

    If the tagName field is 'template', the element must be a leaf.

    If the tagName field is 'noscript', its children should be represented as if
    scripting is disabled ([HTML]).


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
        tag: str = "element",
        properties: Optional[Properties] = {},
        parent: Optional[Element | Root] = None,
        startend: bool = False,
        position: Optional[Position] = None,
        children: Optional[list] = None,
    ):
        super().__init__(position, children)
        self.properties = properties
        self.tag = tag
        self.startend = startend
        self.parent = parent
        self.locals = {}

    def __eq__(self, obj) -> bool:
        if obj is None:
            return False

        if obj.type == self.type:
            if self.tag != obj.tag:
                return False
            if self.startend != obj.startend:
                return False
            if self.properties != obj.properties:
                return False

            for c, oc in zip(self.children, obj.children):
                if c != oc:
                    return False
            return True
        else:
            return False

    def start_tag(self) -> str:
        """Builds the open/start tag for the element.

        Note:
            It will return `/>` if the tag is self closing.

        Returns:
            str: Built element start tag.
        """
        opening = f"<{self.tag}"

        attributes = []
        for prop in self.properties:
            if isinstance(self.properties[prop], bool) or self.properties[prop] in ["yes", "no"]:
                if self.properties[prop] == "yes" or self.properties[prop]:
                    attributes.append(prop)
            else:
                attributes.append(f'{prop}="{self.properties[prop]}"')
        if len(attributes) > 0:
            attributes = " " + " ".join(attributes)
        else:
            attributes = ""

        closing = f"{' /' if self.startend else ''}>"

        return opening + attributes + closing

    def end_tag(self) -> str:
        """Build the elements end tag.

        Returns:
            str: Built element end tag.
        """
        return f"</{self.tag}>" if not self.startend else None

    def __repr__(self) -> str:
        out = f"{self.type}(tag: {self.tag}, properties: {self.properties}, children: {len(self.children)})"
        return out
