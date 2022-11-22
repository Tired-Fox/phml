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
        if obj.type == self.type:
            if self.tag != obj.tag:
                # print(f"{self.tag} != {obj.tag}: Tag values are not equal")
                return False
            if self.position != obj.position:
                # print(f"{self.position} != {obj.position}: Position values are not equal")
                return False
            if self.startend != obj.startend:
                # print(f"{self.openclose} != {obj.openclose}: openclose values are not equal")
                return False
            if self.properties != obj.properties:
                # print(f"{self.properties} != {obj.properties}: Properties values are not equal")
                return False
            for c, oc in zip(self.children, obj.children):
                if c != oc:
                    # print(f"{c} != {oc}: Children values are not equal")
                    return False
            return True
        else:
            # print(f"{self.type} != {obj.type}: {type(self).__name__} can not be equated to {type(obj).__name__}")
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
            if self.properties[prop].lower() in ['yes', 'no']:
                if self.properties[prop].lower() == 'yes':
                    attributes.append(prop)
                else:
                    attributes.append(f'{prop}="no"')
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
        return f"</{self.tag}>"

    def tree(self, depth: int = 0, prefix: str = "") -> str:
        """Yields the tree representation of the node."""
        yield f"{' '*depth}{prefix} {self.tag.upper()} [{len(self.children)}]  {self.position}"

        depth = 2 if depth == 0 else depth
        for i, child in enumerate(self.children):
            prefix = ' ' * depth
            if len(self.children) > 1:
                if i == len(self.children) - 1:
                    sep = "└"
                else:
                    sep = "├"
                    prefix = f"{' '*(depth)}│"
            else:
                sep = "└"
            for i, line in enumerate(child.tree(2, sep)):
                if i == 0:
                    yield line
                else:
                    yield prefix + line

    def inspect(self) -> str:
        """Return an inspected tree view of the node."""
        return "\n".join(self.tree())

    def __repr__(self) -> str:
        out = f"{self.type}(tag: {self.tag}, properties: {self.properties}, children: {len(self.children)}), properties: {self.properties})"
        return out
