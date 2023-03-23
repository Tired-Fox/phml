from __future__ import annotations
from collections.abc import Iterator
from os import write
from pathlib import Path
from contextlib import contextmanager
from traceback import print_tb
from typing import Any

from parser import HypertextMarkupParser
from compiler import HypertextMarkupCompiler
from nodes import Parent, AST

class PHMLTryCatch:
    def __init__(self, path: str|Path|None = None):
        self._path = str(path or "")

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None and not isinstance(exc_val, SystemExit):
            print_tb(exc_tb)
            if self._path != "":
                print(f'[{self._path}]:', exc_val)
            else:
                print(exc_val)
            exit()

class PHMCore:
    parser: HypertextMarkupParser
    """PHML parser."""
    compiler: HypertextMarkupCompiler
    """PHML compiler to HTML."""

    def __init__(self) -> None:
        self.parser = HypertextMarkupParser()
        self.compiler = HypertextMarkupCompiler()
        self._ast = None
        self._from_path = None
        self._from_file = None
        self._to_file = None

    @staticmethod
    @contextmanager
    def open(_from: str, _to: str | None = None) -> Iterator[PHMCore]:
        with PHMLTryCatch():
            core = PHMCore()
            core._from_file = Path(_from).open("r", encoding="utf-8")
            core._from_path = _from
            if _to is not None:
                core._to_file = Path(_to).open("+w", encoding="utf-8")
            yield core
            core._from_file.close()
            if core._to_file is not None:
                core._to_file.close()

    @property
    def ast(self) -> AST:
        """The current ast that has been parsed. Defaults to None."""
        return self._ast or AST()

    def load(self, path: str|Path):
        """Loads the contents of a file and sets the core objects ast
        to the results after parsing.
        """
        with PHMLTryCatch(), Path(path).open("r", encoding="utf-8") as file:
            self._from_path = path
            self._ast = self.parser.parse(file.read())
        return self

    def parse(self, data: str|None = None):
        """Parse a given phml string into a phml ast.
        
        Returns:
            Instance of the core object for method chaining.
        """

        if data is None and self._from_file is None:
            raise ValueError("Must either provide a phml str to parse or use parse in the open context manager")

        with PHMLTryCatch(self._from_path):
            if data is not None:
                self._from_path = None
                self._ast = self.parser.parse(data)
            elif self._from_file is not None:
                self._ast = self.parser.parse(self._from_file.read())

        return self

    def compile(self, **context: Any) -> Parent:
        """Compile the python blocks, python attributes, and phml components and return the resulting ast.
        The resulting ast replaces the core objects ast.
        """
        if self._ast is not None:
            with PHMLTryCatch(self._from_path):
                return self.compiler.compile(self._ast, **context)
        raise ValueError("Must first parse a phml file before compiling to an AST")

    def render(self, _compress: bool = False, **context: Any) -> str | None:
        """Renders the phml ast into an html string. If currently in a context manager
        the resulting string will also be output to an associated file.
        """
        if self._ast is not None:
            with PHMLTryCatch(self._from_path):
                result = self.compiler.render(self._ast, _compress="" if _compress else "\n", **context)
                if self._to_file is not None:
                    self._to_file.write(result)
                elif self._from_file is not None and self._from_path is not None:
                    self._to_file = Path(self._from_path).with_suffix(".html").open("+w", encoding="utf-8")
                    self._to_file.write(result)
                return result
        raise ValueError("Must first parse a phml file before rendering a phml AST")
