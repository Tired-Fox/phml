from pathlib import Path
from typing import Optional

from phml.core.formats import Format, Formats
from phml.core.nodes import AST, All_Nodes
from phml.utilities import filename_from_path, parse_component

from .compiler import Compiler
from .parser import Parser

__all__ = ["PHML"]


class PHML:
    """A helper class that bundles the functionality
    of the parser and compiler together. Allows for loading source files,
    parsing strings and dicts, rendering to a different format, and finally
    writing the results of a render to a file.
    """

    parser: Parser
    """Instance of a [Parser][phml.parser.Parser]."""
    compiler: Compiler
    """Instance of a [Compiler][phml.compile.Compiler]."""
    scopes: Optional[list[str]]
    """List of paths from cwd to auto add to python path. This helps with
    importing inside of phml files.
    """

    @property
    def ast(self) -> AST:
        """Reference to the parser attributes ast value."""
        return self.parser.ast

    @ast.setter
    def ast(self, _ast: AST):
        self.parser.ast = _ast

    def __init__(
        self,
        scopes: Optional[list[str]] = None,
        components: Optional[dict[str, dict[str, list | All_Nodes]]] = None,
    ):
        self.parser = Parser()
        self.compiler = Compiler(components=components)
        self.scopes = scopes or []

    def add(
        self,
        *components: dict[str, dict[str, list | All_Nodes] | AST]
        | tuple[str, dict[str, list | All_Nodes] | AST]
        | Path,
    ):
        """Add a component to the element replacement list.

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
            if isinstance(component, Path):
                self.parser.load(component)
                self.compiler.add((filename_from_path(component), parse_component(self.parser.ast)))
            else:
                self.compiler.add(component)
        return self

    def remove(self, *components: str | All_Nodes):
        """Remove an element from the list of element replacements.

        Takes any number of strings or node objects. If a string is passed
        it is used as the key that will be removed. If a node object is passed
        it will attempt to find a matching node and remove it.
        """
        self.compiler.remove(*components)
        return self

    def load(self, file_path: str | Path, from_format: Optional[Format] = None):
        """Load a source files data and parse it to phml.

        Args:
            file_path (str | Path): The file path to the source file.
        """
        self.parser.load(file_path, from_format)
        return self

    def parse(self, data: str | dict, from_format: Format = Formats.PHML):
        """Parse a str or dict object into phml.

        Args:
            data (str | dict): Object to parse to phml
        """
        self.parser.parse(data, from_format)
        return self

    def render(
        self,
        file_type: str = Formats.HTML,
        indent: Optional[int] = None,
        scopes: Optional[list[str]] = None,
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

        scopes = scopes or ["./"]
        for scope in self.scopes:
            if scope not in scopes:
                scopes.append(scope)

        return self.compiler.compile(
            self.parser.ast,
            to_format=file_type,
            indent=indent,
            scopes=scopes,
            **kwargs,
        )

    def write(
        self,
        dest: str | Path,
        file_type: str = Formats.HTML,
        indent: Optional[int] = None,
        scopes: Optional[list[str]] = None,
        **kwargs,
    ):
        """Renders the parsed ast to a different format, then writes
        it to a given file. Defaults to rendering and writing out as html.

        Args:
            dest (str | Path): The path to the file to be written to.
            file_type (str): The format to render the ast as.
            indent (Optional[int], optional): The number of spaces per indent. By default it will
            use the standard for the given format. HTML has 4 spaces, phml has 4 spaces, and json
            has 2 spaces.
            kwargs: Any additional data to pass to the compiler that will be exposed to the
            phml files.
        """
        dest = Path(dest)

        if dest.suffix == "":
            dest = dest.with_suffix(file_type.suffix())

        with open(dest, "+w", encoding="utf-8") as dest_file:
            dest_file.write(
                self.render(file_type=file_type, indent=indent, scopes=scopes, **kwargs)
            )
        return self
