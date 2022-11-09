from typing import Optional


class Point:
    """Represents one place in a source file.

    The line field (1-indexed integer) represents a line in a source file. The column field (1-indexed integer) represents a column in a source file. The offset field (0-indexed integer) represents a character in a source file.
    """

    def __init__(self, line: int, column: int, offset: Optional[int]):
        if line < 1:
            raise IndexError(f"Point.line must be >= 1 but was {line}")

        self.line = line

        if column < 1:
            raise IndexError(f"Point.column must be >= 1 but was {column}")

        self.column = column

        if offset is not None and offset < 1:
            raise IndexError(f"Point.offset must be >= 0 or None but was {line}")

        self.offset = offset
