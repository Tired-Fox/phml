from typing import Iterator

from .literal import Literal


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
        lines = [line.lstrip() for line in self.value.split("\n") if line.strip() != ""]
        if len(lines) > 1:
            start = f"{' ' * indent}<!--{lines[0]}"
            end = f"{' ' * indent}{lines[-1]}-->"
            for i in range(1, len(lines) - 1):
                lines[i] = (' ' * indent) + lines[i].strip()
            lines = [start, *lines[1:-1], end]
            return "\n".join(lines)
        return ' ' * indent + f"<!--{self.value}-->"

    def __repr__(self) -> str:
        return f"literal.comment(value: {self.value})"
