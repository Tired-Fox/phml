# pylint: disable=missing-module-docstring
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .point import Point


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

    def __init__(self, start: Point, end: Point, indent: Optional[int] = None):
        self.start = start
        self.end = end

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

    def __repr__(self) -> str:
        indent = f" ~ {self.indent}" if self.indent is not None else ""
        return f"<{self.start}-{self.end}{indent}>"

    def __str__(self) -> str:
        return repr(self)
