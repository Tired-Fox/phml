"""phml.nodes

All things related to phml node data objects.
"""

from .AST import AST
from .comment import Comment
from .doctype import DocType
from .element import Element
from .literal import Literal
from .node import Node
from .parent import Parent
from .point import Point
from .position import Position
from .processing_instruction import PI
from .root import Root
from .text import Text
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
    "All_Nodes",
]
