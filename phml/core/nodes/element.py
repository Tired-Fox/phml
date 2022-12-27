from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .parent import Parent

if TYPE_CHECKING:
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
        properties: Optional[Properties] = None,
        parent: Optional[Element | Root] = None,
        startend: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.properties = properties or {}
        self.tag = tag
        self.startend = startend
        self.parent = parent
        self.locals = {}

    def __getitem__(self, index: str) -> str:
        return self.properties[index]

    def __setitem__(self, index: str, value: str):
        if not isinstance(index, str) or not isinstance(value, (str, bool)):
            raise TypeError("Index must be a str and value must be either str or bool.")

        self.properties[index] = value

    def __delitem__(self, index: str):
        if index in self.properties:
            self.properties.pop(index, None)

    def __eq__(self, obj) -> bool:
        return bool(
            obj is not None
            and isinstance(obj, Element)
            and self.tag == obj.tag
            and self.startend == obj.startend
            and self.properties == obj.properties
            and len(self.children) == len(obj.children)
            and all(child == obj_child for child, obj_child in zip(self.children, obj.children))
        )

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
            if isinstance(self[prop], bool) or self[prop] in ["yes", "no"]:
                if self[prop] == "yes" or self[prop]:
                    attributes.append(prop)
            else:
                attributes.append(f'{prop}="{self[prop]}"')
        if len(attributes) > 0:
            attributes = " " + " ".join(attributes)
        else:
            attributes = ""

        closing = f"{'/' if self.startend else ''}>"

        if closing == "/>" and attributes != "":
            return opening + attributes + " " + closing
        return opening + attributes + closing

    def end_tag(self) -> str:
        """Build the elements end tag.

        Returns:
            str: Built element end tag.
        """
        return f"</{self.tag}>" if not self.startend else None

    def __repr__(self) -> str:
        out = f"{self.type}(tag: {self.tag}, properties: {self.properties}, \
startend: {self.startend}, children: {len(self.children)})"
        return out
