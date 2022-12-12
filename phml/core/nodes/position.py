from __future__ import annotations

from typing import Optional, overload

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
