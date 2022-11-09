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
