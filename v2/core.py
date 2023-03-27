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
from utils import PHMLTryCatch
from components import ComponentManager, ComponentType

class PHMCore:
    parser: HypertextMarkupParser
    """PHML parser."""
    compiler: HypertextMarkupCompiler
    """PHML compiler to HTML."""
    components: ComponentManager
    """PHML component parser and manager."""
    context: dict[str, Any]
    """PHML global variables to expose to each phml file compiled with this instance.
    This is the highest scope and is overridden by more specific scoped variables.
    """

    def __init__(self) -> None:
        self.parser = HypertextMarkupParser()
        self.compiler = HypertextMarkupCompiler()
        self.components = ComponentManager()
        self.context = {}
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
        context = {**self.context, **context}
        if self._ast is not None:
            with PHMLTryCatch(self._from_path):
                return self.compiler.compile(self._ast, self.components, **context)
        raise ValueError("Must first parse a phml file before compiling to an AST")

    def render(self, _compress: bool = False, **context: Any) -> str | None:
        """Renders the phml ast into an html string. If currently in a context manager
        the resulting string will also be output to an associated file.
        """
        context = {**self.context, **context}
        if self._ast is not None:
            with PHMLTryCatch(self._from_path):
                result = self.compiler.render(
                    self._ast,
                    _components=self.components,
                    _compress="" if _compress else "\n", **context
                )
                if self._to_file is not None:
                    self._to_file.write(result)
                elif self._from_file is not None and self._from_path is not None:
                    self._to_file = Path(self._from_path).with_suffix(".html").open("+w", encoding="utf-8")
                    self._to_file.write(result)
                return result
        raise ValueError("Must first parse a phml file before rendering a phml AST")

    def add(
        self,
        file: str | None = None,
        *,
        cmpt: tuple[str, str] | None = None,
        data: tuple[str, ComponentType] | None = None,
        ignore: str = "",
    ):
        """Add a component to the component manager. The components are used by the compiler
        when generating html files from phml.
        """
        self.components.add(file, cmpt=cmpt, data=data, ignore=ignore)

    def remove(self, key: str):
        """Remove a component from the component manager based on the components name/tag.
        """
        self.components.remove(key)

    def expose(self, _context: dict[str, Any] | None = None, **context: Any):
        """Expose global variables to each phml file compiled with this instance.
        This data is the highest scope and will be overridden by more specific
        scoped variables with equivelant names.
        """
        self.context.update(_context or {})
        self.context.update(context)

    def redact(self, key: str):
        """Remove global variable from this instance."""
        del self.context[key]
