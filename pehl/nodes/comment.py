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
        yield f"{' '*depth}{prefix} {self.type.upper()}"
        
    def pehl(self, indent: int = 0) -> str:
        """Build indented html string of html comment.

        Returns:
            str: Built html of comment
        """
        return ' '*indent + str(self)
        
    def __str__(self) -> str:
        return f"<!-- {self.value} -->"
