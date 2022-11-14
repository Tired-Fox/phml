from typing import Iterator
from .literal import Literal


class Text(Literal):
    """Text (Literal) represents a Text ([DOM]).

    Example:

    ```html
    <span>Foxtrot</span>
    ```

    Yields:

    ```javascript
    {
        type: 'element',
        tagName: 'span',
        properties: {},
        children: [{type: 'text', value: 'Foxtrot'}]
    }
    ```
    """

    def tree(self, depth: int = 0, prefix: str = "") -> Iterator[str]:
        yield f"{' '*depth}{prefix} {self.type.upper()}  {self.position}"

    def inspect(self) -> str:
        """Return an inspected tree view of the node."""
        return "\n".join(self.tree())

    def phml(self, indent: int = 0) -> str:
        """Build indented html string of html text.

        Returns:
            str: Built html of text
        """
        return self.value

    def __str__(self) -> str:
        return "literal.text()"
