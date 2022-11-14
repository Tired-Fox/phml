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
        tag: str,
        properties: Optional[Properties],
        parent: Optional[Element | Root] = None,
        openclose: bool = False,
        position: Optional[Position] = None,
        children: Optional[list] = None,
    ):
        super().__init__(position, children)
        self.properties = properties
        self.tag = tag
        self.openclose = openclose
        self.parent = parent

    def __eq__(self, obj) -> bool:
        if obj.type == self.type:
            if self.tag != obj.tag:
                # print(f"{self.tag} != {obj.tag}: Tag values are not equal")
                return False
            if self.position != obj.position:
                # print(f"{self.position} != {obj.position}: Position values are not equal")
                return False
            if self.openclose != obj.openclose:
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

        closing = f"{' /' if self.openclose else ''}>"

        return opening + attributes + closing

    def end_tag(self) -> str:
        """Build the elements end tag.

        Returns:
            str: Built element end tag.
        """
        return f"</{self.tag}>"

    def as_dict(self) -> dict:
        """Convert element node to dict."""
        return {
            "type": self.type,
            "tag": self.tag,
            "properties": self.properties,
            "startend": self.openclose,
            "children": [child.as_dict() for child in self.children]
        }

    def tree(self, depth: int = 0, prefix: str = "") -> str:
        """Yields the tree representation of the node."""
        yield f"{' '*depth}{prefix} {self.tag.upper()} [{len(self.children)}]  {self.position}"

        depth = 2 if depth == 0 else depth
        for i, child in enumerate(self.children):            
            prefix = f"{' '*(depth)}"
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

    def html(self, indent: int = 4) -> str:
        """Convert element node and all children to an html string."""
        if self.openclose:
            return " "*indent + self.start_tag()
        else:
            if self.position is not None and self.position.indent is not None:
                indent = self.position.indent * 4
                out = [" "*indent + self.start_tag()]
                out.extend([child.phml(indent + 4) for child in self.children])
                out.append(" "*indent + self.end_tag())
                return "\n".join(out)
            else:
                out = [" "*indent + self.start_tag()]
                out.extend([child.phml(indent + 4) for child in self.children])
                out.append(self.end_tag())
                return "".join(out)

    def json(self, indent: int = 2) -> str:
        """Convert element node and all children to a json string."""
        from json import dumps

        return dumps(self.as_dict(), indent=indent)

    def phml(self, indent: int = 0) -> str:
        """Build indented html string of element and it's children.

        Returns:
            str: Built html of element
        """
        
        if self.openclose:
            return " "*indent + self.start_tag()
        else:
            if self.position is not None and self.position.indent is not None:
                indent = self.position.indent * 4
                out = [" "*indent + self.start_tag()]
                out.extend([child.phml(indent + 4) for child in self.children])
                out.append(" "*indent + self.end_tag())
                return "\n".join(out)
            else:
                out = [" "*indent + self.start_tag()]
                out.extend([child.phml(indent + 4) for child in self.children])
                out.append(self.end_tag())
                return "".join(out)

    def __repr__(self) -> str:
        out = f"{self.type}(tag: {self.tag}, properties: {self.properties}, children: "
        for child in self.children:
            out += repr(child) + "\n"
        out += ")"
        return out

    def __str__(self) -> str:
        return f"{self.type}.{self.tag}(startend: {self.openclose}, children: {len(self.children)}, properties: {self.properties})"
