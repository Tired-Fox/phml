from typing import Optional

from phml.core.nodes import AST, All_Nodes

from .compile import ASTRenderer
from .format import Format
from .parse import parse_hypertest_markup


def parse_markup(data: str, class_name: str, auto_close: bool = True) -> AST:
    """Parse a string as a markup document."""
    return parse_hypertest_markup(data, class_name, auto_close)


class PHMLFormat(Format):
    """Logic for parsing and compiling html files."""

    extension: str = "phml"

    @classmethod
    def parse(cls, data: str, auto_close: bool = True) -> str:
        return parse_markup(data, cls.__name__, auto_close)

    @classmethod
    def compile(
        cls,
        ast: AST,
        components: Optional[dict[str, dict[str, list | All_Nodes]]] = None,
        **kwargs,
    ) -> AST:
        """Compile and process the given ast and return the resulting ast."""
        return ast

    @classmethod
    def render(
        cls,
        ast: AST,
        components: Optional[dict[str, dict[str, list | All_Nodes]]] = None,
        indent: int = 4,
        **kwargs,
    ) -> str:
        indent = indent or 4

        return ASTRenderer(ast, indent).compile()
