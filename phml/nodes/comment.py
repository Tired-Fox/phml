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
        return ' ' * indent + f"<!--{self.value}-->"

    def __repr__(self) -> str:
        return f"literal.comment(value: {self.value})"
