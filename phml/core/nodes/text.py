from functools import cached_property

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
        if self.parent is None or not any(
            tag in self.get_ancestry() for tag in ["pre", "python"]
        ):
            from phml.utilities.transform import normalize_indent # pylint: disable=import-outside-toplevel
            return normalize_indent(self.value, indent)
        return self.value

    def __repr__(self) -> str:
        return f"literal.text('{self.value}')"
