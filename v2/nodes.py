from __future__ import annotations

from enum import StrEnum, unique
from json import dumps
from typing import Iterator, overload
from type import Attribute
from saimll import SAIML


@unique
class LiteralType(StrEnum):
    Text = "text"
    Comment = "comment"

@unique
class NodeType(StrEnum):
    AST = "ast"
    ELEMENT = "element"
    LITERAL = "literal"

class Point:
    """Represents one place in a source file.

    The line field (1-indexed integer) represents a line in a source file. The column field
    (1-indexed integer) represents a column in a source file. The offset field (0-indexed integer)
    represents a character in a source file.
    """

    def __init__(self, line: int, column: int, offset: int | None = None):
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
        return f"\x1b[38;5;244m{self.line}:{self.column}\x1b[39m"


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
        indent: int | None = None,
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

    def __init__(self, start: Point, end: Point, indent: int | None = None):
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
            raise IndexError(
                f"Position.indent value must be >= 0 or None but was {indent}"
            )

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
            "end": {
                "line": self.end.line,
                "column": self.end.column,
                "offset": self.end.offset,
            },
            "indent": self.indent,
        }

    def __repr__(self) -> str:
        indent = f" ~ {self.indent}" if self.indent is not None else ""
        return f"\x1b[38;5;8m<\x1b[39m{self.start}\x1b[38;5;8m-\x1b[39m{self.end}{indent}\x1b[38;5;8m>\x1b[39m"

    def __str__(self) -> str:
        return repr(self)
    
class Node:
    """Base phml node. Defines a type and basic interactions."""

    def __init__(
        self,
        _type: NodeType,
        position: Position | None = None,
        parent: Parent | None = None,
        in_pre: bool = False,
    ):
        self._position = position
        self.parent = parent
        self._type = _type
        self.in_pre = in_pre

    @property
    def position(self) -> Position | None:
        """The position of the node in the parsed phml text.
        Is `None` if the node was generated.
        """
        return self._position

    @property
    def type(self) -> str:
        """The node type. Either root, element, or litera."""
        return self._type

    @type.setter
    def type(self, new_type: str):
        self._type = new_type

    def pos_as_str(self, color: bool = False) -> str:
        """Return the position formatted as a string."""

        position = ""
        if self.position is not None:
            if color:
                start = self.position.start
                end = self.position.end
                position = SAIML.parse(
                    f"<[@F244]{start.line}[@F]-[@F244]{start.column}[@F]"
                    f":[@F244]{end.line}[@F]-[@F244]{end.column}[@F]>"
                )
            else:
                start = self.position.start
                end = self.position.end
                position = f"<{start.line}-{start.column}:{end.line}-{end.column}>"
        return position
    
    def pretty(self):
        return "\n".join(self.__pretty__(color=True))

    def __repr__(self) -> str:
        return f"{self.type}()"

    def __pretty__(self, indent: int = 0, color: bool = False):
        if color:
            return SAIML.parse(f"{' '*indent}[@Fred]{self.type}[@F]") + f" {self.pos_as_str(True)}"
        return f"{' '*indent}{self.type} {self.pos_as_str()}"


    def __str__(self) -> str:
        return self.__pretty__()


class Parent(Node):
    def __init__(
        self,
        _type: NodeType,
        children: list[Node] | None,
        position: Position | None = None,
        parent: Node | None = None,
        in_pre: bool = False
    ):
        super().__init__(_type, position, parent, in_pre)
        self.children = [] if children is not None else None

        if children is not None:
            self.extend(children)

    def __iter__(self) -> Iterator[Parent|Literal]:
        if self.children is not None:
            for child in self.children:
                yield child
        else:
            raise ValueError("A self closing element can not be iterated")

    def __getitem__(self, key: int) -> Parent | Literal:
        if self.children is not None:
            return self.children[key]
        raise ValueError("A self closing element can not be indexed")

    def append(self, node: Node):
        """Append a child node to the end of the children."""
        if self.children is not None:
            node.parent = self
            self.children.append(node)
        else:
            raise ValueError("A child node can not be appended to a self closing element")

    def extend(self, nodes: list[Node]):
        """Extend the children with a list of nodes."""
        if self.children is not None:
            for i, _ in enumerate(nodes):
                nodes[i].parent = self
            self.children.extend(nodes)
        else:
            raise ValueError("A self closing element can not have it's children extended")

    def insert(self, index: int, nodes: Node | list[Node]):
        """Insert a child node or nodes into a specific index of the children."""
        if self.children is not None:
            if isinstance(nodes, list):
                for n in nodes:
                    n.parent = self
                self.children[index:index] = nodes
            else:
                self.children.insert(index, nodes)
        else:
            raise ValueError("A child node can not be inserted into a self closing element")

    def remove(self, node: Node):
        """Remove a child node from the children."""
        if self.children is None:
            raise ValueError("A child node can not be removed from a self closing element.")
        if node not in self.children:
            raise ValueError("Node does not exist in children")
        self.children.remove(node)


    def len_as_str(self, color: bool = False) -> str:
        if color:
            return SAIML.parse(f"[@F66]{len(self) if self.children is not None else '/'}[@F]")
        return f"{len(self) if self.children is not None else '/'}"

    def __len__(self) -> int:
        return len(self.children) if self.children is not None else 0

    def __repr__(self) -> str:
        return f"{self.type}(cldrn={self.len_as_str()})"

    def __pretty__(self, indent: int = 0, color: bool = False):
        output = [f"{' '*indent}{self.type} [{self.len_as_str()}]{self.pos_as_str()}"]
        if color:
            output[0] = (
                SAIML.parse(f"{' '*indent}[@Fred]{self.type}[@F]")
                + f" [{self.len_as_str(True)}]"
                + f" {self.pos_as_str(True)}"
            )
        for child in self.children or []:
            output.extend(child.__pretty__(indent+2, color))
        return output


    def __str__(self) -> str:
        return "\n".join(self.__pretty__())


class AST(Parent):
    def __init__(
        self,
        children: list[Node] | None = None,
        position: Position | None = None,
        in_pre: bool = False,
    ):
        super().__init__(NodeType.AST, children or [], position, None, in_pre)


class Element(Parent):
    def __init__(
        self,
        tag: str,
        attributes: dict[str, Attribute] | None = None,
        children: list[Node] | None = None,
        position: Position | None = None,
        parent: Node | None = None,
        in_pre: bool = False,
    ):
        super().__init__(NodeType.ELEMENT, children, position, parent, in_pre)
        self.tag = tag
        self.attributes = attributes or {}
        self.context = {}

    @property
    def tag_path(self) -> list[str]:
        """Get the list of all the tags to the current element. Inclusive."""
        path = [self.tag]
        parent = self
        while isinstance(parent.parent, Element):
            path.append(parent.parent.tag)
            parent = parent.parent

        path.reverse()
        return path

    def __contains__(self, _k: str) -> bool:
        return _k in self.attributes

    @overload
    def __getitem__(self, _k: int) -> Parent | Literal:
        ...

    def __getitem__(self, _k: str) -> Attribute:
        if isinstance(_k, str):
            return self.attributes[_k]

        if self.children is not None:
            return self.children[_k]

        raise ValueError("A self closing element can not have it's children indexed")

    @overload
    def get(self, key: str) -> Attribute | None:
        ...

    def get(self, key: str, _default: Attribute | None = None) -> Attribute:
        """Get a specific element attribute. Returns `None` if not found
        unless `_default` is defined.

        Args:
            key (str): The name of the attribute to retrieve.
            _default (str|bool): The default value to return if the key
                isn't an attribute.

        Returns:
            str|bool|None: str or bool if the attribute exists or a default
                was provided, else None
        """
        if not isinstance(_default, Attribute) and _default is not None:
            raise TypeError("_default value must be str, bool, or None")

        if key in self:
            return self[key]
        return _default

    def attrs_as_str(self, indent: int, color: bool = False) -> str:
        """Return a str representation of the attributes"""
        if color:
            attrs = (
                f"\n{' '*(indent)}▸ "
                + f"\n{' '*(indent)}▸ ".join(
                    str(key)
                    + ": "
                    + (
                        f"\x1b[32m{value!r}\x1b[39m"
                        if isinstance(value, str) else
                        f"\x1b[35m{value}\x1b[39m"
                    )
                    for key,value in self.attributes.items()
                )
            ) if len(self.attributes) > 0 else ""
        else:
            attrs = (
                f"\n{' '*(indent)}▸ "
                + f"\n{' '*(indent)}▸ ".join(
                    f"{key}: {value!r}"
                    for key,value in self.attributes.items()
                )
            ) if len(self.attributes) > 0 else ""

        return attrs 

    def __repr__(self) -> str:
        return f"{self.type}.{self.tag}(cldrn={self.len_as_str()}, attrs={self.attributes})"

    def __pretty__(self, indent: int = 0, color: bool = False) -> list[str]:
        attrs = self.attrs_as_str(indent+2, color)
        output: list[str] = []
        if color:
            output.append( 
                f"{' '*indent}"
                + SAIML.parse(
                    f"[@Fred]{self.type}[@F]"
                    + f".[@Fblue]{self.tag}[@F]"
                )
                + f" [{self.len_as_str(True)}]"
                + f" {self.pos_as_str(True)}"
                + f"{self.attrs_as_str(indent+2, True)}"
            )
        else:
            output.append(
                f"{' '*indent}{self.type}.{self.tag}"
                + f" [{self.len_as_str()}]{self.pos_as_str()}{self.attrs_as_str(indent+2)}"
            )

        for child in self.children or []:
            output.extend(child.__pretty__(indent+2, color))
        return output

    def __str__(self) -> str:
        return "\n".join(self.__pretty__())


class Literal(Node):
    def __init__(
        self,
        name: str,
        content: str,
        parent: Node | None = None,
        position: Position | None = None,
        in_pre: bool = False,
    ):
        super().__init__(NodeType.LITERAL, position, parent, in_pre)
        self.name = name
        self.content = content

    def __repr__(self) -> str:
        return f"{self.type}.{self.name}(len={len(self.content)})"

    def __pretty__(self, indent: int = 0, color: bool = False):
        if color:
            return [SAIML.parse(f"{' '*indent}[@Fred]{self.type}[@F].[@Fblue]{self.name}[@F]")]
        return [f"{' '*indent}{self.type}.{self.name}"]

    def __str__(self) -> str:
        return self.__pretty__()[0]

    # TODO: methods to normalize content indent and strip blank lines

