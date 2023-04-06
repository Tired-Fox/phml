from __future__ import annotations
from dataclasses import dataclass

from types import NoneType
from typing import Any, Iterator, NoReturn, TypeAlias, overload

from saimll import SAIML

Attribute: TypeAlias = str | bool


class Missing:
    pass


MISSING = Missing()


def p_code(value) -> str:  # pragma: no cover
    """Get python code representation of phml nodes."""
    if value is None:
        return "None"
    return value.__p_code__()


@dataclass
class LiteralType:
    Text = "text"
    Comment = "comment"

    @staticmethod
    def From(type: str) -> str:
        types = ["text", "comment"]
        if type in types:
            return type
        raise ValueError(f"Expected on of {', '.join(types)}")


@dataclass
class NodeType:
    AST = "ast"
    ELEMENT = "element"
    LITERAL = "literal"


class Point:
    """Represents one place in a source file.

    The line field (1-indexed integer) represents a line in a source file. The column field
    (1-indexed integer) represents a column in a source file. The offset field (0-indexed integer)
    represents a character in a source file.
    """

    def __init__(self, line: int, column: int) -> None:
        if line is None or line < 0:
            raise IndexError(f"Point.line must be >= 0 but was {line}")

        self.line = line

        if column is None or column < 0:
            raise IndexError(f"Point.column must be >= 0 but was {column}")

        self.column = column

    def __eq__(self, _o) -> bool:
        return (
            isinstance(_o, self.__class__)
            and _o.line == self.line
            and _o.column == self.column
        )

    @staticmethod
    def from_dict(data: dict) -> Point:
        return Point(data["line"], data["column"])

    def __p_code__(self) -> str:
        return f"Point({self.line}, {self.column})"

    def __repr__(self) -> str:
        return f"{self.line}:{self.column}"

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
        start: Point,
        end: Point,
    ) -> None:
        """
        Args:
            start (tuple[int, int, int  |  None]): Tuple representing the line, column, and optional
            offset of the start point.
            end (tuple[int, int, int  |  None]): Tuple representing the line, column, and optional
            offset of the end point.
            indent (Optional[int], optional): The indent amount for the start of the position.
        """
        ...

    @overload
    def __init__(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> None:
        """
        Args:
            start (tuple[int, int, int  |  None]): Tuple representing the line, column, and optional
            offset of the start point.
            end (tuple[int, int, int  |  None]): Tuple representing the line, column, and optional
            offset of the end point.
            indent (Optional[int], optional): The indent amount for the start of the position.
        """
        ...

    def __init__(self, start: Point | tuple[int, int], end: Point | tuple[int, int]):
        """
        Args:
            start (Point): Starting point of the position.
            end (Point): End point of the position.
            indent (int | None): The indent amount for the start of the position.
        """

        self.start = Point(start[0], start[1]) if isinstance(start, tuple) else start
        self.end = Point(end[0], end[1]) if isinstance(end, tuple) else end

    def __p_code__(self) -> str:
        return f"Position({p_code(self.start)}, {p_code(self.end)})"

    def __eq__(self, _o):
        return (
            isinstance(_o, Position) and _o.start == self.start and _o.end == self.end
        )

    @staticmethod
    def from_pos(pos: Position) -> Position:
        """Create a new position from another position object."""
        return Position(
            (pos.start.line, pos.start.column),
            (pos.end.line, pos.end.column),
        )

    @staticmethod
    def from_dict(data: dict) -> Position | None:
        if data is None:
            return None
        return Position(Point.from_dict(data["start"]), Point.from_dict(data["end"]))

    def as_dict(self) -> dict:
        """Convert the position object to a dict."""
        return {
            "start": {
                "line": self.start.line,
                "column": self.start.column,
            },
            "end": {
                "line": self.end.line,
                "column": self.end.column,
            },
        }

    def __repr__(self) -> str:
        # indent = f" ~ {self.indent}" if self.indent is not None else ""
        return f"<{self.start!r}-{self.end!r}>"

    def __str__(self) -> str:
        return f"\x1b[38;5;8m<\x1b[39m{self.start}\x1b[38;5;8m-\x1b[39m{self.end}\x1b[38;5;8m>\x1b[39m"


class Node:
    """Base phml node. Defines a type and basic interactions."""

    def __init__(
        self,
        _type: NodeType,
        position: Position | None = None,
        parent: Parent | None = None,
        in_pre: bool = False,
    ) -> None:
        self._position = position
        self.parent = parent
        self._type = _type
        self.in_pre = in_pre

        def __p_code__(self) -> str:
            in_pre = f", in_pre={self.in_pre}" if self.in_pre else ""
            return f"Node({self.type!r}, position={p_code(self.position)}{in_pre})"

    def __eq__(self, _o):
        return (
            isinstance(_o, self.__class__)
            and self.type == _o.type
            and self.in_pre == _o.in_pre
        )

    def as_dict(self) -> dict:
        return {
            "type": str(self._type),
        }

    @staticmethod
    def from_dict(data: dict, in_pre: bool = False):
        if data["type"] == NodeType.AST:
            ast = AST(
                children=[] if data["children"] is not None else None,
            )
            if data["children"] is not None:
                for child in data["children"]:
                    ast.append(Node.from_dict(child, in_pre))
            return ast
        elif data["type"] == NodeType.ELEMENT:
            return Element.from_dict(data)
        elif data["type"] == NodeType.LITERAL:
            return Literal(
                LiteralType.From(data["name"]),
                data["content"],
            )
        raise ValueError(
            f"Phml ast dicts must have nodes with the following types: {NodeType.AST}, {NodeType.ELEMENT}, {NodeType.LITERAL}",
        )

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

    def pos_as_str(self, color: bool = False) -> str:  # pragma: no cover
        """Return the position formatted as a string."""

        position = ""
        if self.position is not None:
            if color:
                start = self.position.start
                end = self.position.end
                position = SAIML.parse(
                    f"<[@F244]{start.line}[@F]-[@F244]{start.column}[@F]"
                    f":[@F244]{end.line}[@F]-[@F244]{end.column}[@F]>",
                )
            else:
                start = self.position.start
                end = self.position.end
                position = f"<{start.line}-{start.column}:{end.line}-{end.column}>"
        return position

    def __repr__(self) -> str:
        return f"{self.type}()"

    def __format__(self, indent: int = 0, color: bool = False, text: bool = False):
        if color:
            return (
                SAIML.parse(f"{' '*indent}[@Fred]{self.type}[@F]")
                + f" {self.pos_as_str(True)}"
            )
        return f"{' '*indent}{self.type} {self.pos_as_str()}"

    def __str__(self) -> str:
        return self.__format__()


class Parent(Node):
    def __init__(
        self,
        _type: NodeType,
        children: list[Node] | None,
        position: Position | None = None,
        parent: Parent | None = None,
        in_pre: bool = False,
    ) -> None:
        super().__init__(_type, position, parent, in_pre)
        self.children = [] if children is not None else None

        if children is not None:
            self.extend(children)

    def __p_code__(self) -> str:
        children = (
            "None"
            if self.children is None
            else f"[{', '.join([p_code(child) for child in self])}]"
        )
        in_pre = f", in_pre={self.in_pre}" if self.in_pre else ""
        return f"Parent({self.type!r}, position={p_code(self.position)}{in_pre}, children={children})"

    def __iter__(self) -> Iterator[Parent | Literal]:
        if self.children is not None:
            yield from self.children

    @overload
    def __setitem__(self, key: int, value: Node) -> NoReturn:
        ...

    @overload
    def __setitem__(self, key: slice, value: list) -> NoReturn:
        ...

    def __setitem__(self, key: int | slice, value: Node | list):
        if self.children is not None:
            if isinstance(key, int):
                if not isinstance(value, Node):
                    raise ValueError(
                        "Can not assign value that is not phml.Node to children",
                    )
                value.parent = self
                self.children[key] = value
            else:
                if not isinstance(value, list):
                    raise ValueError(
                        "Can not assign value that is not list[phml.Node] to slice of children",
                    )
                for v in value:
                    v.parent = self
                self.children[key] = value
        else:
            raise ValueError("Invalid value type. Expected phml Node")

    @overload
    def __getitem__(self, _k: int) -> Parent | Literal:
        ...

    @overload
    def __getitem__(self, _k: slice) -> list[Parent | Literal]:
        ...

    def __getitem__(
        self,
        key: int | slice,
    ) -> Parent | Literal | list[Parent | Literal]:
        if self.children is not None:
            return self.children[key]
        raise ValueError("A self closing element can not be indexed")

    @overload
    def __delitem__(self, key: int) -> NoReturn:
        ...

    @overload
    def __delitem__(self, key: slice) -> NoReturn:
        ...

    def __delitem__(self, key: int | slice):
        if self.children is not None:
            del self.children[key]
        else:
            raise ValueError("Can not use del for a self closing elements children")

    def pop(self, idx: int = 0) -> Node:
        """Pop a node from the children. Defaults to index 0"""
        if self.children is not None:
            return self.children.pop(idx)
        raise ValueError("A self closing element can not pop a child node")

    def index(self, node: Node) -> int:
        """Get the index of a node in the childre."""
        if self.children is not None:
            return self.children.index(node)
        raise ValueError("A self closing element can not be indexed")

    def append(self, node: Node):
        """Append a child node to the end of the children."""
        if self.children is not None:
            node.parent = self
            self.children.append(node)
        else:
            raise ValueError(
                "A child node can not be appended to a self closing element",
            )

    def extend(self, nodes: list):
        """Extend the children with a list of nodes."""
        if self.children is not None:
            for child in nodes:
                child.parent = self
            self.children.extend(nodes)
        else:
            raise ValueError(
                "A self closing element can not have it's children extended",
            )

    def insert(self, index: int, nodes: Node | list):
        """Insert a child node or nodes into a specific index of the children."""
        if self.children is not None:
            if isinstance(nodes, list):
                for n in nodes:
                    n.parent = self
                self.children[index:index] = nodes
            else:
                self.children.insert(index, nodes)
        else:
            raise ValueError(
                "A child node can not be inserted into a self closing element",
            )

    def remove(self, node: Node):
        """Remove a child node from the children."""
        if self.children is None:
            raise ValueError(
                "A child node can not be removed from a self closing element.",
            )
        self.children.remove(node)

    def len_as_str(self, color: bool = False) -> str:  # pragma: no cover
        if color:
            return SAIML.parse(
                f"[@F66]{len(self) if self.children is not None else '/'}[@F]",
            )
        return f"{len(self) if self.children is not None else '/'}"

    def __len__(self) -> int:
        return len(self.children) if self.children is not None else 0

    def __repr__(self) -> str:
        return f"{self.type}(cldrn={self.len_as_str()})"

    def __format__(self, indent: int = 0, color: bool = False, text: bool = False):
        output = [f"{' '*indent}{self.type} [{self.len_as_str()}]{self.pos_as_str()}"]
        if color:
            output[0] = (
                SAIML.parse(f"{' '*indent}[@Fred]{self.type}[@F]")
                + f" [{self.len_as_str(True)}]"
                + f" {self.pos_as_str(True)}"
            )
        for child in self.children or []:
            output.extend(child.__format__(indent=indent + 2, color=color, text=text))
        return output

    def __str__(self) -> str:
        return "\n".join(self.__format__())

    def as_dict(self) -> dict:
        return {
            "children": [child.as_dict() for child in self.children]
            if self.children is not None
            else None,
            **super().as_dict(),
        }


class AST(Parent):
    def __init__(
        self,
        children: list[Node] | None = None,
        position: Position | None = None,
        in_pre: bool = False,
    ) -> None:
        super().__init__(NodeType.AST, children or [], position, None, in_pre)

    def __eq__(self, _o):
        return isinstance(_o, AST) and (
            (_o.children is None and self.children is None)
            or (len(_o) == len(self) and all(c1 == c2 for c1, c2 in zip(_o, self)))
        )

    def __p_code__(self) -> str:
        children = (
            "None"
            if self.children is None
            else f"[{', '.join([p_code(child) for child in self])}]"
        )
        in_pre = f", in_pre={self.in_pre}" if self.in_pre else ""
        return f"AST(position={p_code(self.position)}, children={children}{in_pre})"


class Element(Parent):
    def __init__(
        self,
        tag: str,
        attributes: dict[str, Attribute] | None = None,
        children: list[Node] | None = None,
        position: Position | None = None,
        parent: Parent | None = None,
        in_pre: bool = False,
    ) -> None:
        super().__init__(NodeType.ELEMENT, children, position, parent, in_pre)
        self.tag = tag
        self.attributes = attributes or {}
        self.context = {}

    def __p_code__(self) -> str:
        children = (
            "None"
            if self.children is None
            else f"[{', '.join([p_code(child) for child in self])}]"
        )
        in_pre = f", in_pre={self.in_pre}" if self.in_pre else ""
        return f"Element({self.tag!r}, position={p_code(self.position)}, attributes={self.attributes}, children={children}{in_pre})"

    def __eq__(self, _o) -> bool:
        return (
            isinstance(_o, Element)
            and _o.attributes == self.attributes
            and (
                (_o.children is None and self.children is None)
                or (len(_o) == len(self) and all(c1 == c2 for c1, c2 in zip(_o, self)))
            )
        )

    def as_dict(self) -> dict:
        return {"tag": self.tag, "attributes": self.attributes, **super().as_dict()}

    @staticmethod
    def from_dict(data: dict, in_pre: bool = False) -> Element:
        element = Element(
            data["tag"],
            attributes=data["attributes"],
            children=[] if data["children"] is not None else None,
        )
        if data["children"] is not None:
            element.children = [
                Node.from_dict(child, in_pre or data["tag"] == "pre")
                for child in data["children"]
            ]
        return element

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

    def __hash__(self) -> int:
        return (
            hash(self.tag)
            + sum(hash(attr) for attr in self.attributes.values())
            + hash(len(self))
        )

    def __contains__(self, _k: str) -> bool:
        return _k in self.attributes

    @overload
    def __getitem__(self, _k: int) -> Parent | Literal:
        ...

    @overload
    def __getitem__(self, _k: str) -> Attribute:
        ...

    @overload
    def __getitem__(self, _k: slice) -> list[Parent | Literal]:
        ...

    def __getitem__(
        self,
        _k: str | int | slice,
    ) -> Attribute | Parent | Literal | list[Parent | Literal]:
        if isinstance(_k, str):
            return self.attributes[_k]

        if self.children is not None:
            return self.children[_k]

        raise ValueError("A self closing element can not have it's children indexed")

    @overload
    def __setitem__(self, key: int, value: Node) -> NoReturn:
        ...

    @overload
    def __setitem__(self, key: slice, value: list) -> NoReturn:
        ...

    @overload
    def __setitem__(self, key: str, value: Attribute) -> NoReturn:
        ...

    def __setitem__(self, key: str | int | slice, value: Attribute | Node | list):
        if isinstance(key, str) and isinstance(value, Attribute):
            self.attributes[key] = value
        elif isinstance(key, int) and isinstance(value, Node):
            self.insert(key, value)
        elif isinstance(key, slice) and isinstance(value, list):
            if self.children is None:
                raise ValueError(
                    "A self closing element can not have a subset of it's children assigned to",
                )
            self.children[key.start : key.stop] = value
        else:
            raise ValueError(
                "Invalid value type. Expected <key:str> -> <value:Attribute> or <key:int> -> <value:Node>",
            )

    @overload
    def __delitem__(self, key: int) -> NoReturn:
        ...

    @overload
    def __delitem__(self, key: slice) -> NoReturn:
        ...

    @overload
    def __delitem__(self, key: str) -> NoReturn:
        ...

    def __delitem__(self, key: str | int | slice):
        if isinstance(key, str):
            del self.attributes[key]
        elif self.children is not None:
            del self.children[key]
        else:
            raise ValueError("Can not use del for a self closing elements children")

    @overload
    def pop(self, idx: int = 0) -> Node:
        ...

    @overload
    def pop(self, idx: str, _default: Any = MISSING) -> Attribute:
        ...

    def pop(self, idx: str | int = 0, _default: Any = MISSING) -> Attribute | Node:
        """Pop a specific attribute from the elements attributes. A default value
        can be provided for when the value is not found, otherwise an error is thrown.
        """
        if isinstance(idx, str):
            if _default != MISSING:
                return self.attributes.pop(idx, _default)
            return self.attributes.pop(idx)
        if self.children is not None:
            return self.children.pop(idx)

        raise ValueError("A self closing element can not pop a child node")

    def get(self, key: str, _default: Any = MISSING) -> Attribute:
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
        if not isinstance(_default, (Attribute, NoneType)) and _default != MISSING:
            raise TypeError("_default value must be str, bool, or MISSING")

        if key in self:
            return self[key]
        if _default != MISSING:
            return _default
        raise ValueError(f"Attribute {key!r} not found")

    def attrs_as_str(self, indent: int, color: bool = False) -> str:  # pragma: no cover
        """Return a str representation of the attributes"""
        if color:
            attrs = (
                (
                    f"\n{' '*(indent)}▸ "
                    + f"\n{' '*(indent)}▸ ".join(
                        str(key)
                        + ": "
                        + (
                            f"\x1b[32m{value!r}\x1b[39m"
                            if isinstance(value, str)
                            else f"\x1b[35m{value}\x1b[39m"
                        )
                        for key, value in self.attributes.items()
                    )
                )
                if len(self.attributes) > 0
                else ""
            )
        else:
            attrs = (
                (
                    f"\n{' '*(indent)}▸ "
                    + f"\n{' '*(indent)}▸ ".join(
                        f"{key}: {value!r}" for key, value in self.attributes.items()
                    )
                )
                if len(self.attributes) > 0
                else ""
            )

        return attrs

    def __repr__(self) -> str:
        return f"{self.type}.{self.tag}(cldrn={self.len_as_str()}, attrs={self.attributes})"

    def __format__(
        self,
        indent: int = 0,
        color: bool = False,
        text: bool = False,
    ) -> list[str]:  # pragma: no cover
        output: list[str] = []
        if color:
            output.append(
                f"{' '*indent}"
                + SAIML.parse(f"[@Fred]{self.type}[@F]" + f".[@Fblue]{self.tag}[@F]")
                + f" [{self.len_as_str(True)}]"
                + f" {self.pos_as_str(True)}"
                + f"{self.attrs_as_str(indent+2, True)}",
            )
        else:
            output.append(
                f"{' '*indent}{self.type}.{self.tag}"
                + f" [{self.len_as_str()}]{self.pos_as_str()}{self.attrs_as_str(indent+2)}",
            )

        for child in self.children or []:
            output.extend(child.__format__(indent=indent + 2, color=color, text=text))
        return output

    def __str__(self) -> str:
        return "\n".join(self.__format__())


class Literal(Node):
    def __init__(
        self,
        name: str,
        content: str,
        parent: Parent | None = None,
        position: Position | None = None,
        in_pre: bool = False,
    ) -> None:
        super().__init__(NodeType.LITERAL, position, parent, in_pre)
        self.name = name
        self.content = content

    def __hash__(self) -> int:
        return hash(self.content) + hash(str(self.name))

    def __p_code__(self) -> str:
        in_pre = ", in_pre=True" if self.in_pre else ""
        return f"Literal({str(self.name)!r}, {self.content!r}{in_pre})"

    def __eq__(self, _o) -> bool:
        return (
            isinstance(_o, Literal)
            and _o.type == self.type
            and self.name == _o.name
            and self.content == _o.content
        )

    def as_dict(self) -> dict:
        return {"name": str(self.name), "content": self.content, **super().as_dict()}

    @staticmethod
    def is_text(node: Node) -> bool:
        """Check if a node is a literal and a text node."""
        return isinstance(node, Literal) and node.name == LiteralType.Text

    @staticmethod
    def is_comment(node: Node) -> bool:
        """Check if a node is a literal and a comment."""
        return isinstance(node, Literal) and node.name == LiteralType.Comment

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.type}.{self.name}(len={len(self.content)})"

    def __format__(
        self,
        indent: int = 0,
        color: bool = False,
        text: bool = False,
    ):  # pragma: no cover
        from .helpers import normalize_indent

        content = ""
        if text:
            offset = " " * (indent + 2)
            content = (
                f'{offset}"""\n{normalize_indent(self.content, indent+4)}\n{offset}"""'
            )
        if color:
            return [
                SAIML.parse(
                    f"{' '*indent}[@Fred]{self.type}[@F].[@Fblue]{self.name}[@F]"
                    + (f"\n[@Fgreen]{content}[@F]" if text else ""),
                ),
            ]
        return [
            f"{' '*indent}{self.type}.{self.name}" + (f"\n{content}" if text else ""),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.__format__()[0]


def inspect(
    node: Node,
    color: bool = False,
    text: bool = False,
) -> str:  # pragma: no cover
    """Inspected a given node recursively.

    Args:
        node (Node): Any type of node to inspect.
        color (bool): Whether to return a string with ansi encoding. Default False.
        text (bool): Whether to include the text from comment and text nodes. Default False.

    Return:
        A formatted multiline string representation of the node and it's children.
    """
    return "\n".join(node.__format__(color=color, text=text))
