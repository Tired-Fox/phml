from typing import Iterator
from .literal import Literal


class Comment(Literal):
    """Comment (Literal) represents a Comment ([DOM]).

    Example:
    ```html
    <!--Charlie-->
    ```
    """

    def tree(self, depth: int = 0, prefix: str = "└") -> Iterator[str]:
        yield f"{' '*depth}{prefix} {self.type.upper()}  {self.position}"

    def inspect(self) -> str:
        """Return an inspected tree view of the node."""
        return "\n".join(self.tree())

    def phml(self, indent: int = 0) -> str:
        """Build indented html string of html comment.

        Returns:
            str: Built html of comment
        """
        return ' ' * indent + f"<!-- {self.value} -->"

    def __str__(self) -> str:
        return f"literal.comment(value: {self.value})"
