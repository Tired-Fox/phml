from __future__ import annotations

from enum import StrEnum, unique
from json import dumps
from typing import Iterator
from v2.types import Attribute, Position


@unique
class NodeType(StrEnum):
    AST = "ast"
    ELEMENT = "element"
    LITERAL = "literal"


def position(start_line: int, start_col: int, end_line: int, end_col: int) -> Position:
    return ((start_line, start_col), (end_line, end_col))


class Node:
    """Base phml node. Defines a type and basic interactions."""

    def __init__(
        self,
        _type: NodeType,
        position: Position | None = None,
        parent: Node | None = None,
    ):
        self._position = position
        self.parent = parent
        self._type = _type

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

    def pos_as_str(self) -> str:
        """Return the position formatted as a string."""

        position = ""
        if self.position is not None:
            position = "<{}:{}-{}:{}>".format(*self.position[0], *self.position[1])
        return position

    def __repr__(self) -> str:
        return f"{self.type}()"

    def __str__(self) -> str:
        return f"{self.type} {self.pos_as_str()}"


class Parent(Node):
    def __init__(
        self,
        _type: NodeType,
        children: list[Node] | None,
        position: Position | None = None,
        parent: Node | None = None,
    ):
        super().__init__(_type, position, parent)
        self.children = [] if children is not None else None

        if children is not None:
            self.extend(children)

    def __iter__(self) -> Iterator[Node]:
        if self.children is not None:
            for child in self.children:
                yield child
        else:
            raise ValueError("A self closing element can not be iterated")

    def __getitem__(self, key: int) -> Node:
        if self.children is not None:
            return self.children[key]
        raise ValueError("A self closing element can not be indexed")

    def append(self, node: Node):
        """Append a node to the end of the children."""
        if self.children is not None:
            node.parent = self
            self.children.append(node)
        else:
            raise ValueError("A node can not be appended to a self closing element")

    def extend(self, nodes: list[Node]):
        """Extend the children with a list of nodes."""
        if self.children is not None:
            for i, _ in enumerate(nodes):
                nodes[i].parent = self
            self.children.extend(nodes)
        else:
            raise ValueError("A self closing element can not have it's children extended")

    def insert(self, index: int, node: Node):
        """Insert a node into a specific index of the children."""
        if self.children is not None:
            self.children.insert(index, node)
        else:
            raise ValueError("A node can not be inserted into a self closing element")

    def len_as_str(self) -> str:
        return f"{len(self) if self.children is not None else '/'}"

    def __len__(self) -> int:
        return len(self.children) if self.children is not None else 0

    def __repr__(self) -> str:
        pos = self.pos_as_str()
        pos = " " + pos if pos != "" else ""
        return f"{self.type}(cldrn={self.len_as_str()})"

    def __str__(self) -> str:
        pos = self.pos_as_str()
        pos = " " + pos if pos != "" else ""
        return f"{self.type} [{self.len_as_str()}]{pos}"


class AST(Parent):
    def __init__(self, children: list[Node] | None = None, position: Position | None = None):
        super().__init__(NodeType.AST, children or [], position, None)


class Element(Parent):
    def __init__(
        self,
        tag: str,
        attributes: dict[str, Attribute],
        children: list[Node] | None = None,
        position: Position | None = None,
        parent: Node | None = None,
    ):
        super().__init__(NodeType.ELEMENT, children, position, parent)
        self.tag = tag
        self.attributes = attributes
        self.parent = parent
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

    def __getitem__(self, _k: str | int) -> Attribute:
        if isinstance(_k, str):
            return self.attributes[_k]

        if self.children is not None:
            return self.children[_k]

        raise ValueError("A self closing element can not have it's children indexed")

    def get(self, key: str, _default: Attribute | None = None) -> Attribute | None:
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

    def attrs_as_str(self) -> str:
        """Return a str representation of the attributes"""
        attrs = [f"{key}: {value!r}" for key, value in self.attributes.items()]
        return " ▸ " + "\n ▸ ".join(attrs)

    def __repr__(self) -> str:
        return f"{self.type}.{self.tag}(cldrn={self.len_as_str()}, attrs={self.attributes})"

    def __str__(self) -> str:
        pos = self.pos_as_str()
        pos = " " + pos if pos != "" else ""
        attrs = "\n  ".join(self.attrs_as_str().split("\n"))
        return f"{self.type}.{self.tag} [{self.len_as_str()}]{pos}\n  {attrs}"


class Literal(Node):
    def __init__(
        self,
        name: str,
        content: str,
        parent: Node | None = None,
        position: Position | None = None,
    ):
        super().__init__(NodeType.LITERAL, position, parent)
        self.name = name
        self.content = content

    def __repr__(self) -> str:
        return f"{self.type}.{self.name}(len={len(self.content)})"

    def __str__(self) -> str:
        return f"{self.type}.{self.name}"

    # TODO: methods to normalize content indent and strip blank lines


if __name__ == "__main__":
    ast = AST([], position(0, 0, 0, 0))
    ast.append(Element("meta", {"size": "100"}, [], position=position(10, 0, 10, 34)))

    print(ast)
