"""phml.core.parser

The core parsing module for phml. Handles parsing html and phmls strings
along with json.

Exposes phml.core.parser.Parser which handles all parsing functionality.
"""

from pathlib import Path
from typing import Optional

from phml.core.formats import Format, Formats
from phml.core.nodes import AST

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

    ast: AST
    """The recursive node tree of the phml ast."""

    def __init__(self):
        self.ast = None

    def load(self, path: str | Path, from_format: Optional[Format] = None, auto_close: bool = True):
        """Parse a given phml file to AST following hast and unist.

        When finished the PHML.ast variable will be populated with the
        resulting ast.

        Args:
            path (str | Path): The path to the file that should be parsed.
            from_format (Format): phml.core.formats.Format class that will parse the given source.
        """

        path = Path(path)
        if from_format is None:
            for file_format in Formats():
                if file_format.is_format(path.suffix):
                    with open(path, "r", encoding="utf-8") as source:
                        src = source.read()

                    self.ast = file_format.parse(src, auto_close=auto_close)
                    return self
        else:
            with open(path, "r", encoding="utf-8") as source:
                src = source.read()
            self.ast = from_format.parse(src, auto_close=auto_close)
            return self

        raise Exception(f"Could not parse unknown filetype {path.suffix.lstrip('.')!r}")

    def parse(
        self,
        data: str | dict,
        from_format: Format = Formats.PHML,
        auto_close: bool = True
    ):
        """Parse data from a phml/html string or from a dict to a phml ast.

        Args:
            data (str | dict): Data to parse in to a ast
            data_type (str): Can be `HTML`, `PHML`, `MARKDOWN`, or `JSON` which
            tells parser how to parse the data. Otherwise it will assume
            str data to be html/phml and dict as `json`.
            from_format (Format): phml.core.formats.Format class that will parse the given source.
        """

        if isinstance(data, dict):
            self.ast = Formats.JSON.parse(data)
        else:
            self.ast = from_format.parse(data, auto_close=auto_close)

        return self
