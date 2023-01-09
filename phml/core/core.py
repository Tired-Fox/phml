from io import TextIOWrapper
from pathlib import Path
from typing import Any, Optional

from phml.core.formats import Format, Formats
from phml.core.nodes import AST, All_Nodes
from phml.utilities import cmpt_name_from_path, parse_component

from .compiler import Compiler
from .parser import Parser

__all__ = ["PHML"]


class PHML:
    """A helper class that bundles the functionality
    of the parser and compiler together. Allows for loading source files,
    parsing strings and dicts, rendering to a different format, and finally
    writing the results of a render to a file.
    """

    @property
    def ast(self) -> AST:
        """The parsed ast value."""
        return self._parser.ast

    @ast.setter
    def ast(self, _ast: AST):
        self._parser.ast = _ast
        
    @property
    def components(self) -> dict:
        """The components currently stored in the compiler."""
        return self._compiler.components

    def __init__(
        self,
        scopes: Optional[list[str]] = None,
        components: Optional[dict[str, dict[str, list | All_Nodes]]] = None,
        **exposable: Any,
    ):
        self._parser = Parser()
        self._compiler = Compiler(components=components)
        self._scopes = scopes or []
        self._exposable = dict(exposable)

    def expose(self, **kwargs: Any):
        """Add additional data to the compilers global values. These values are exposed for every
        call to render or write.
        """
        self._exposable.update(kwargs)

    def redact(self, key: str):
        """Remove a value from the compilers globally exposed values."""
        self._exposable.pop(key, None)

    def expand(self, *args: str):
        """Add relative paths to a directory, that you want added to the python path
        for every time render or write is called.
        """
        self._scopes.extend([arg for arg in args if arg not in self._scopes])

    def restrict(self, *args: str):
        """Remove relative paths to a directory, that are in the compilers globally added scopes.
        This prevents them from being added to the python path.
        """
        for arg in args:
            if arg in self._scopes:
                self._scopes.remove(arg)

    def add(
        self,
        *components: dict[str, dict[str, list | All_Nodes] | AST]
        | tuple[str, dict[str, list | All_Nodes] | AST]
        | Path
        | str,
        strip_root: bool = False,
    ):
        """Add a component to the compiler's component list.

        Components passed in can be of a few types. The first type it can be is a
        pathlib.Path type. This will allow for automatic parsing of the file at the
        path and then the filename and parsed ast are passed to the compiler. It can
        also be a dictionary of str being the name of the element to be replaced.
        The name can be snake case, camel case, or pascal cased. The value can either
        be the parsed result of the component from phml.utilities.parse_component() or the
        parsed ast of the component. Lastely, the component can be a tuple. The first
        value is the name of the element to be replaced; with the second value being
        either the parsed result of the component or the component's ast.

        Note:
            Any duplicate components will be replaced.

        Args:
            components: Any number values indicating
            name of the component and the the component. The name is used
            to replace a element with the tag==name.
        """

        for component in components:
            if isinstance(component, (Path, str)):
                self._parser.load(Path(component))
                self._compiler.add(
                    (
                        cmpt_name_from_path(Path(component), strip_root),
                        parse_component(self._parser.ast),
                    )
                )
            elif isinstance(component, tuple) and isinstance(component[1], (Path, str)):
                self._parser.load(Path(component[1]))
                self._compiler.add((component[0], parse_component(self._parser.ast)))
            else:
                self._compiler.add(component)
        return self

    def remove(self, *components: str | All_Nodes):
        """Remove an element from the list of element replacements.

        Takes any number of strings or node objects. If a string is passed
        it is used as the key that will be removed. If a node object is passed
        it will attempt to find a matching node and remove it.
        """
        self._compiler.remove(*components)
        return self

    def load(self, file_path: str | Path, from_format: Optional[Format] = None):
        """Load a source files data and parse it to phml.

        Args:
            file_path (str | Path): The file path to the source file.
        """
        self._parser.load(file_path, from_format)
        return self

    def parse(self, data: str | dict, from_format: Format = Formats.PHML):
        """Parse a str or dict object into phml.

        Args:
            data (str | dict): Object to parse to phml
        """
        self._parser.parse(data, from_format)
        return self

    def render(
        self,
        file_type: str = Formats.HTML,
        indent: Optional[int] = None,
        scopes: Optional[list[str]] = None,
        components: Optional[dict] = None,
        **kwargs,
    ) -> str:
        """Render the parsed ast to a different format. Defaults to rendering to html.

        Args:
            file_type (str): The format to render to. Currently support html, phml, and json.
            indent (Optional[int], optional): The number of spaces per indent. By default it will
            use the standard for the given format. HTML has 4 spaces, phml has 4 spaces, and json
            has 2 spaces.

        Returns:
            str: The rendered content in the appropriate format.
        """

        scopes = scopes or []
        for scope in self._scopes:
            if scope not in scopes:
                scopes.append(scope)

        return self._compiler.compile(
            self._parser.ast,
            to_format=file_type,
            indent=indent,
            scopes=scopes,
            components=components,
            **{**self._exposable, **kwargs},
        )

    def write(
        self,
        file: str | Path | TextIOWrapper,
        file_type: str = Formats.HTML,
        indent: Optional[int] = None,
        scopes: Optional[list[str]] = None,
        replace_suffix: bool = False,
        components: Optional[dict] = None,
        **kwargs,
    ):
        """Renders the parsed ast to a different format, then writes
        it to a given file. Defaults to rendering and writing out as html.

        Args:
            file (str | Path | TextIOWrapper): The path to the file to be written to, or the opened
            file to write to.

            file_type (str): The format to render the ast as.

            indent (Optional[int], optional): The number of spaces per indent. By default it will
            use the standard for the given format. HTML has 4 spaces, phml has 4 spaces, and json
            has 2 spaces.

            scopes (list[str], None): The relative paths from the cwd to the directory that will
            be inserted into the python path.

            replace_suffix (bool): Override to use the preferred file suffix no matter what.
            Defaults to False, as the preferred suffix will only be used if no suffix is provided.

            kwargs: Any additional data to pass to the compiler that will be exposed to the
            phml files.
        """
        if isinstance(file, (str | Path)):
            file = Path(file)
            
            file.parent.mkdir(parents=True, exist_ok=True)

            if file.suffix == "" or replace_suffix:
                file = file.with_suffix(file_type.suffix())

            with open(file, "+w", encoding="utf-8") as dest_file:
                dest_file.write(
                    self.render(
                        file_type=file_type,
                        indent=indent,
                        scopes=scopes,
                        components=components,
                        **kwargs,
                    )
                )
        elif isinstance(file, TextIOWrapper):
            file.write(
                self.render(
                    file_type=file_type,
                    indent=indent,
                    scopes=scopes,
                    components=components,
                    **kwargs,
                )
            )
        return self
