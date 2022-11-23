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

    @cached_property
    def num_lines(self) -> int:
        """Determine the number of lines the text has."""
        return len([line for line in self.value.split("\n") if line.strip() != ""])

    def stringify(self, indent: int = 0) -> str:
        """Build indented html string of html text.

        Returns:
            str: Built html of text
        """
        if not any(tag in self.get_ancestry() for tag in ["pre", "python"]):
            lines = [line.lstrip() for line in self.value.split("\n") if line.strip() != ""]
            for line in lines:
                line = ' ' * indent + line
            return "\n".join(lines)
        return self.value

    def __repr__(self) -> str:
        return "literal.text()"
