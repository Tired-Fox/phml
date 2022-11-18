from functools import cached_property
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

    @cached_property
    def num_lines(self) -> int:
        """Determine the number of lines the text has."""
        return len([line for line in self.value.split("\n") if line.strip() != ""])

    def phml(self, indent: int = 0) -> str:
        """Build indented html string of html text.

        Returns:
            str: Built html of text
        """
        if not any(tag in self.get_ancestry() for tag in ["pre", "python"]):
            lines = [line.strip() for line in self.value.split("\n") if line.strip() != ""]
            for line in lines:
                line = ' ' * indent + line
            return "\n".join(lines)
        return self.value

    def __str__(self) -> str:
        return "literal.text()"
