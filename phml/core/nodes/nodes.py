from __future__ import annotations

from functools import cached_property, lru_cache
from typing import Optional, overload

__all__ = [
    "Element",
    "Root",
    "Node",
    "DocType",
    "Parent",
    "PI",
    "Comment",
    "Literal",
    "Point",
    "Position",
    "Text",
    "NODE"
]

def leading_spaces(content: str | list[str]) -> int:
    """Get the leading offset of the first line of the string."""
    content = content.split("\n") if isinstance(content, str) else content
    return len(content[0]) - len(content[0].lstrip())

def strip_blank_lines(data_lines: list[str]) -> list[str]:
    """Strip the blank lines at the start and end of a list."""
    data_lines = [line.replace("\r\n", "\n") for line in data_lines]
    # remove leading blank lines
    for idx in range(0, len(data_lines)):  # pylint: disable=consider-using-enumerate
        if data_lines[idx].strip() != "":
            data_lines = data_lines[idx:]
            break
        if idx == len(data_lines) - 1:
            data_lines = []
            break

    # Remove trailing blank lines
    if len(data_lines) > 0:
        for idx in range(len(data_lines) - 1, -1, -1):
            if data_lines[idx].replace("\n", " ").strip() != "":
                data_lines = data_lines[: idx + 1]
                break

    return data_lines

def normalize_indent(content: str, indent: int = 0) -> str:
    """Normalize the indent between all lines.

    Args:
        content (str): The content to normalize the indent for
        indent (bool): The amount of offset to add to each line after normalization.

    Returns:
        str: The normalized string
    """

    content = strip_blank_lines(str(content).split("\n"))
    offset = len(content[0]) - len(content[0].lstrip())
    lines = []
    for line in content:
        if len(line) > 0 and leading_spaces(line) >= offset:
            lines.append(" " * indent + line[offset:])
        else:
            lines.append(line)
    return "\n".join(lines)

class Point:
    """Represents one place in a source file.

    The line field (1-indexed integer) represents a line in a source file. The column field
    (1-indexed integer) represents a column in a source file. The offset field (0-indexed integer)
    represents a character in a source file.
    """

    def __init__(self, line: int, column: int, offset: Optional[int] = None):
        if line is None or line < 0:
            raise IndexError(f"Point.line must be >= 0 but was {line}")

        self.line = line

        if column is None or column < 0:
            raise IndexError(f"Point.column must be >= 0 but was {column}")

        self.column = column

        if offset is not None and offset < 0:
            raise IndexError(f"Point.offset must be >= 0 or None but was {line}")

        self.offset = offset

    def __eq__(self, obj) -> bool:
        return bool(
            obj is not None
            and isinstance(obj, self.__class__)
            and self.line == obj.line
            and self.column == obj.column
        )

    def __repr__(self) -> str:
        return f"point(line: {self.line}, column: {self.column}, offset: {self.offset})"

    def __str__(self) -> str:
        return f"{self.line}:{self.column}"

class Position:
    """Position represents the location of a node in a source file.

    The `start` field of `Position` represents the place of the first character
    of the parsed source region. The `end` field of Position represents the place
    of the first character after the parsed source region, whether it exists or not.
    The value of the `start` and `end` fields implement the `Point` interface.

    The `indent` field of `Position` represents the start column at each index
    (plus start line) in the source region, for elements that span multiple lines.

    If the syntactic unit represented by a node is not present in the source file at
    the time of parsing, the node is said to be `generated` and it must not have positional
    information.
    """

    @overload
    def __init__(
        self,
        start: tuple[int, int, int | None],
        end: tuple[int, int, int | None],
        indent: Optional[int] = None,
    ):
        """
        Args:
            start (tuple[int, int, int  |  None]): Tuple representing the line, column, and optional
            offset of the start point.
            end (tuple[int, int, int  |  None]): Tuple representing the line, column, and optional
            offset of the end point.
            indent (Optional[int], optional): The indent amount for the start of the position.
        """
        ...

    def __init__(self, start: Point, end: Point, indent: Optional[int] = None):
        """
        Args:
            start (Point): Starting point of the position.
            end (Point): End point of the position.
            indent (int | None): The indent amount for the start of the position.
        """

        self.start = (
            Point(start[0], start[1], start[2] if len(start) == 3 else None)
            if isinstance(start, tuple)
            else start
        )
        self.end = (
            Point(end[0], end[1], end[2] if len(end) == 3 else None)
            if isinstance(end, tuple)
            else end
        )

        if indent is not None and indent < 0:
            raise IndexError(f"Position.indent value must be >= 0 or None but was {indent}")

        self.indent = indent

    def __eq__(self, obj) -> bool:
        return bool(
            obj is not None
            and isinstance(obj, Position)
            and self.start == obj.start
            and self.end == obj.end
        )

    def as_dict(self) -> dict:
        """Convert the position object to a dict."""
        return {
            "start": {
                "line": self.start.line,
                "column": self.start.column,
                "offset": self.start.offset,
            },
            "end": {"line": self.end.line, "column": self.end.column, "offset": self.end.offset},
            "indent": self.indent,
        }

    def __repr__(self) -> str:
        indent = f" ~ {self.indent}" if self.indent is not None else ""
        return f"<{self.start}-{self.end}{indent}>"

    def __str__(self) -> str:
        return repr(self)

class Node:  # pylint: disable=too-few-public-methods
    """All node values can be expressed in JSON as: string, number,
    object, array, true, false, or null. This means that the syntax tree should
    be able to be converted to and from JSON and produce the same tree.
    For example, in JavaScript, a tree can be passed through JSON.parse(JSON.phml(tree))
    and result in the same tree.
    """

    position: Position
    """The location of a node in a source document.
    The value of the position field implements the Position interface.
    The position field must not be present if a node is generated.
    """

    def __init__(
        self,
        position: Optional[Position] = None,
    ):
        self.position = position

    @property
    def type(self) -> str:
        """Non-empty string representing the variant of a node.
        This field can be used to determine the type a node implements."""
        return self.__class__.__name__.lower()

class Parent(Node):  # pylint: disable=too-few-public-methods
    """Parent (UnistParent) represents a node in hast containing other nodes (said to be children).

    Its content is limited to only other hast content.
    """

    def __init__(self, position: Optional[Position] = None, children: Optional[list] = None):
        super().__init__(position)

        if children is not None:
            for child in children:
                if hasattr(child, "type") and child.type in [
                    "element",
                    "text",
                    "doctype",
                    "root",
                    "comment",
                ]:
                    child.parent = self

        self.children: list[Element | DocType | Comment | Text] = children or []

    def append(self, node: NODE):
        """Add a node to the nested children of the current parent node."""
        node.parent = self
        self.children.append(node)
        
    def extend(self, nodes: list[NODE]):
        """Add a node to the nested children of the current parent node."""
        for node in nodes:
            self.append(node)

    def insert(self, index: int, node: NODE):
        """Insert a node into a specific position in the current parent node's children."""
        node.parent = self
        self.children.insert(index, node)

    def remove(self, node: NODE):
        """Remove a specific node from the current parent node's children."""
        self.children.remove(node)
    
class Root(Parent):
    """Root (Parent) represents a document.

    Root can be used as the root of a tree, or as a value
    of the content field on a 'template' Element, never as a child.
    """

    def __init__(
        self,
        position: Optional[Position] = None,
        children: Optional[list] = None,
    ):
        super().__init__(position, children)
        self.parent = None

    def __eq__(self, obj) -> bool:
        return bool(
            obj is not None
            and isinstance(obj, Root)
            and len(self.children) == len(obj.children)
            and all(child == obj_child for child, obj_child in zip(self.children, obj.children))
        )

    def __repr__(self) -> str:
        return f"root [{len(self.children)}]"

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
        properties: Optional[dict[str, str]] = None,
        parent: Optional[Element | Root] = None,
        startend: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.properties = properties or {}
        self.tag = tag
        self.startend = startend
        self.parent = parent
        self.context = {}

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
        return f"</{self.tag}>" if not self.startend else ""

    def __repr__(self) -> str:
        out = f"{self.type}(tag: {self.tag}, properties: {self.properties}, \
startend: {self.startend}, children: {len(self.children)})"
        return out

class PI(Node):
    """A processing instruction node. Mainly used for XML."""

    def __init__(self, tag: str, properties: dict, position: Optional[Position] = None) -> None:
        super().__init__(position)
        self.tag = tag
        self.properties = properties

    def stringify(self, indent: int = 0):  # pylint: disable=unused-argument
        """Construct the string representation of the processing instruction node."""
        attributes = " ".join(f'{key}="{value}"' for key, value in self.properties.items())
        return f"<?{self.tag} {attributes}?>"

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

class Literal(Node):
    """Literal (UnistLiteral) represents a node in hast containing a value."""

    position: Position
    """The location of a node in a source document.
    The value of the position field implements the Position interface.
    The position field must not be present if a node is generated.
    """

    value: str
    """The Literal nodes value. All literal values must be strings"""

    def __init__(
        self,
        value: str = "",
        parent: Optional[Element | Root] = None,
        position: Optional[Position] = None,
    ):
        super().__init__(position)
        self.value = str(value)
        self.parent = parent

    def __eq__(self, obj) -> bool:
        return bool(obj is not None and self.type == obj.type and self.value == obj.value)

    def normalized(self, indent: int = 0) -> str:
        """Get the normalized indented value with leading and trailing blank lines stripped."""
        return normalize_indent(self.value, indent)
    
    def stringify(self, indent: int) -> str:
        return self.normalized(indent)

    def get_ancestry(self) -> list[str]:
        """Get the ancestry of the literal node.

        Used to validate whether there is a `pre` element in the ancestry.
        """

        def get_parent(parent) -> list[str]:
            result = []

            if parent is not None and hasattr(parent, "tag"):
                result.append(parent.tag)

            if parent.parent is not None:
                result.extend(get_parent(parent.parent))

            return result

        return get_parent(self.parent)

class Text(Literal):
    """Text (Literal) represents a Text ([DOM]).

    Example:

    ```html
    <span>Foxtrot</span>
    ```

    Yields:

    ```javascript
    {
        type: 'element',
        tagName: 'span',
        properties: {},
        children: [{type: 'text', value: 'Foxtrot'}]
    }
    ```
    """

    @cached_property
    def num_lines(self) -> int:
        """Determine the number of lines the text has."""
        return len([line for line in str(self.value).split("\n") if line.strip() != ""])

    def stringify(self, indent: int = 0) -> str:
        """Build indented html string of html text.

        Returns:
            str: Built html of text
        """
        if self.parent is None or not any(
            tag in self.get_ancestry() for tag in ["pre", "python"]
        ):
            from phml.utilities.transform import normalize_indent # pylint: disable=import-outside-toplevel
            return normalize_indent(self.value, indent)
        return self.value

    def __repr__(self) -> str:
        return f"literal.text('{self.value}')"

class Comment(Literal):
    """Comment (Literal) represents a Comment ([DOM]).

    Example:
    ```html
    <!--Charlie-->
    ```
    """

    def stringify(self, indent: int = 0) -> str:
        """Build indented html string of html comment.

        Returns:
            str: Built html of comment
        """
        lines = [line for line in self.value.split("\n") if line.strip() != ""]
        if len(lines) > 1:
            start = f"{' ' * indent}<!--{lines[0].rstrip()}"
            end = f"{' ' * indent}{lines[-1].lstrip()}-->"
            for i in range(1, len(lines) - 1):
                lines[i] = (' ' * indent) + lines[i].strip()
            lines = [start, *lines[1:-1], end]
            return "\n".join(lines)
        return ' ' * indent + f"<!--{self.value}-->"

    def __repr__(self) -> str:
        return f"literal.comment(value: {self.value})"

NODE = Root | Element | Text | Comment | DocType | Parent | Node | Literal