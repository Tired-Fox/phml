"""phml.core.parser

The core parsing module for phml. Handles parsing html and phmls strings
along with json.

Exposes phml.core.parser.Parser which handles all parsing functionality.
"""

from json import loads
from pathlib import Path
from typing import Callable, Optional

from phml.core.nodes import AST, Root

from .hypertext_markup_parser import HypertextMarkupParser
from .json import json_to_ast

__all__ = ["Parser"]


class Parser:
    """Primary logic to handle everything with a phml file.

    This class can parse files as phml files and create an ast.
    The ast and the nodes themselfs can translate themselves to;
    html, phml, and json. The ast can recursively return itself as
    an html string. However, only this class can process the python
    blocks inside of the phml file.

    Call Parser.convert() and pass any kwargs you wish to be exposed to
    the process that processes the python. You may also use Parser.util to
    pass extensions to convert and manipulate the html along with the python
    processing.
    """

    parser: HypertextMarkupParser
    """The custom builtin `html.parser` class that builds phml ast."""

    ast: AST
    """The recursive node tree of the phml ast."""

    def __init__(self):
        self.phml_parser = HypertextMarkupParser()
        self.ast = None

    def load(self, path: str | Path, handler: Optional[Callable] = None):
        """Parse a given phml file to AST following hast and unist.

        When finished the PHML.ast variable will be populated with the
        resulting ast.

        Args:
            path (str | Path): The path to the file that should be parsed.
            handler (Callable | None): A function to call instead of the built in
            parser to parse to a phml.AST. Must take a string and return a phml.AST.
        """

        self.phml_parser.cur_tags = []

        with open(path, "r", encoding="utf-8") as source:
            src = source.read()

        if handler is None:
            path = Path(path)

            if path.suffix == ".json":
                self.ast = AST(json_to_ast(loads(src)))
            else:
                self.phml_parser.reset()
                self.phml_parser.cur = Root()

                try:
                    self.phml_parser.feed(src)
                    if len(self.phml_parser.cur_tags) > 0:
                        last = self.phml_parser.cur_tags[-1].position
                        raise Exception(
                            f"Unbalanced tags in source file '{path.as_posix()}' at \
[{last.start.line}:{last.start.column}]"
                        )
                    self.ast = AST(self.phml_parser.cur)
                except Exception as exception:
                    self.ast = None
                    raise Exception(f"'{path.as_posix()}': {exception}") from exception
        else:
            self.ast = handler(src)

        return self

    def parse(self, data: str | dict, handler: Optional[Callable] = None):
        """Parse data from a phml/html string or from a dict to a phml ast.

        Args:
            data (str | dict): Data to parse in to a ast
            data_type (str): Can be `HTML`, `PHML`, `MARKDOWN`, or `JSON` which
            tells parser how to parse the data. Otherwise it will assume
            str data to be html/phml and dict as `json`.
            handler (Callable | None): A function to call instead of the built in
            parser to parse to a phml.AST. Must take a string and return a phml.AST.
        """

        self.phml_parser.cur_tags = []

        if handler is None:
            if isinstance(data, dict):
                self.ast = AST(json_to_ast(data))
            elif isinstance(data, str):
                self.phml_parser.reset()
                self.phml_parser.cur = Root()

                try:
                    self.phml_parser.feed(data)
                    if len(self.phml_parser.cur_tags) > 0:
                        last = self.phml_parser.cur_tags[-1].position
                        raise Exception(
                            f"Unbalanced tags in source at [{last.start.line}:{last.start.column}]"
                        )
                    self.ast = AST(self.phml_parser.cur)
                except Exception as exception:
                    self.ast = None
                    raise Exception(
                        f"{data[:6] + '...' if len(data) > 6 else data}\
: {exception}"
                    ) from exception
        else:
            self.ast = handler(data)

        return self
