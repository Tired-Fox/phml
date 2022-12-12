from typing import Optional

from phml.core.nodes import All_Nodes, AST

from .format import Format
from .compile import ToML
from .parse import HypertextMarkupParser


class PHMLFormat(Format):
    """Logic for parsing and compiling html files."""

    extension: str = "phml"

    @classmethod
    def parse(cls, data: ...) -> str:
        phml_parser = HypertextMarkupParser()

        if isinstance(data, str):
            try:
                phml_parser.feed(data)
                if len(phml_parser.cur_tags) > 0:
                    last = phml_parser.cur_tags[-1].position
                    raise Exception(
                        f"Unbalanced tags in source at [{last.start.line}:{last.start.column}]"
                    )
                return AST(phml_parser.cur)
            except Exception as exception:
                raise Exception(
                    f"{data[:6] + '...' if len(data) > 6 else data}\
: {exception}"
                ) from exception
        raise Exception("Data passed to PHMLFormat.parse must be a str")

    @classmethod
    def compile(
        cls,
        ast: AST,
        components: Optional[dict[str, dict[str, list | All_Nodes]]] = None,
        indent: int = 4,
        **kwargs,
    ) -> str:
        indent = indent or 4

        return ToML(ast, indent).compile()
