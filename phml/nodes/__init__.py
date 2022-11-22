"""phml.nodes

All things related to phml node data objects.
"""

from .AST import AST
from .node import Node
from .root import Root
from .doctype import DocType

from .parent import Parent
from .element import Element

from .literal import Literal
from .comment import Comment
from .text import Text

from .position import Position
from .point import Point

from .types import Properties, PropertyName, PropertyValue

All_Nodes = Root | Element | Text | Comment | DocType | Parent | Node | Literal

__all__ = [
    "AST",
    "Node",
    "Root",
    "DocType",
    "Parent",
    "Element",
    "Literal",
    "Comment",
    "Text",
    "Position",
    "Point",
    "Properties",
    "PropertyName",
    "PropertyValue",
    "All_Nodes"
]