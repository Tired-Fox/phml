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

    def as_dict(self) -> dict:
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

    def __eq__(self, obj) -> bool:
        if isinstance(obj, Position):
            if self.start == obj.start:
                if self.end == obj.end:
                    return True
                else:
                    # print(f"{self.end} != {obj.end}: end values are not equal")
                    return False
            else:
                # print(f"{self.start} != {obj.start}: start values are not equal")
                return False
        # print(
        # f"{type(self).__name__} != {type(obj).__name__}: {type(self).__name__} can not be equated to {type(obj).__name__}"
        # )
        return False

    def __repr__(self) -> str:
        indent = f" ~ {self.indent}" if self.indent is not None else ""
        return f"<{self.start}-{self.end}{indent}>"

    def __str__(self) -> str:
        return repr(self)
