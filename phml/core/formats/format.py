from typing import Optional

from phml.core.nodes import AST, NODE


class Format:
    """Base class for built-in file formats. Each sub class contains a `parse` and
    `compile` method. The parse method should take a string or dict and return
    """

    extension: str | list[str] = "txt"
    """The extension or extensions for the file format. When writing to a file and
    extensions is a list then the first extensions in the list is used for the file
    extension.
    """

    @classmethod
    def suffix(cls) -> str:
        """The prefered extension/suffix for the file format."""

        if isinstance(cls.extension, list):
            return f".{cls.extension[0]}"
        return f".{cls.extension}"

    @classmethod
    def is_format(cls, _extension: str) -> bool:
        """Determine if an extension is of the current format."""

        if isinstance(cls.extension, list):
            return _extension.lstrip(".") in cls.extension
        return _extension.lstrip(".") == cls.extension

    @classmethod
    def parse(cls, data: ..., auto_close: bool = True) -> str:
        """Parse the given data into a phml.core.nodes.AST."""
        raise Exception("Base class Format's parse method should never be called")

    @classmethod
    def compile(
        cls,
        ast: AST,
        components: Optional[dict[str, dict[str, list | NODE]]] = None,
        **kwargs,
    ) -> AST:
        """Compile and process the given ast and return the resulting ast."""
        raise Exception(f"{cls.__class__.__name__} \
does not support compiling and returning a phml ast.")

    @classmethod
    def render(
        cls,
        ast: AST,
        components: Optional[dict[str, dict[str, list | NODE]]] = None,
        indent: int = 0,
        **kwargs,
    ) -> str:
        """Compile the given phml.core.nodes.AST into string of a given format."""
        raise Exception("Base class Format's render method should never be called")
