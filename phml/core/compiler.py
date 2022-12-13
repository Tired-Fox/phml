"""phml.core.compile

The heavy lifting module that compiles phml ast's to different string/file formats.
"""

from typing import Any, Optional

from phml.core.formats import Format, Formats
from phml.core.formats.compile import *  # pylint: disable=unused-wildcard-import
from phml.core.nodes import AST, All_Nodes
from phml.utilities import parse_component, tag_from_file, valid_component_dict

__all__ = ["Compiler"]


class Compiler:
    """Used to compile phml into other formats. HTML, PHML,
    JSON, Markdown, etc...
    """

    ast: AST
    """phml ast used by the compiler to generate a new format."""

    def __init__(
        self,
        ast: Optional[AST] = None,
        components: Optional[dict[str, dict[str, list | All_Nodes]]] = None,
    ):
        self.ast = ast
        self.components = components or {}

    def add(
        self,
        *components: dict[str, dict[str, list | All_Nodes] | AST]
        | tuple[str, dict[str, list | All_Nodes] | AST],
    ):
        """Add a component to the compilers component list.

        Components passed in can be of a few types. It can also be a dictionary of str
        being the name of the element to be replaced. The name can be snake case, camel
        case, or pascal cased. The value can either be the parsed result of the component
        from phml.utilities.parse_component() or the parsed ast of the component. Lastely,
        the component can be a tuple. The first value is the name of the element to be
        replaced; with the second value being either the parsed result of the component
        or the component's ast.

        Note:
            Any duplicate components will be replaced.

        Args:
            components: Any number values indicating
            name of the component and the the component. The name is used
            to replace a element with the tag==name.
        """

        for component in components:
            if isinstance(component, dict):
                for key, value in component.items():
                    if isinstance(value, AST):
                        self.components[tag_from_file(key)] = parse_component(value)
                    elif isinstance(value, dict) and valid_component_dict(value):
                        self.components[tag_from_file(key)] = value
            elif isinstance(component, tuple):
                if isinstance(component[0], str) and isinstance(component[1], AST):
                    self.components[tag_from_file(component[0])] = parse_component(component[1])
                elif isinstance(component[0], str) and valid_component_dict(component[1]):
                    self.components[tag_from_file(component[0])] = component[1]

        return self

    def remove(self, *components: str | All_Nodes):
        """Takes either component names or components and removes them
        from the dictionary.

        Args:
            components (str | All_Nodes): Any str name of components or
            node value to remove from the components list in the compiler.
        """
        for component in components:
            if isinstance(component, str):
                if component in self.components:
                    self.components.pop(component, None)
                else:
                    raise KeyError(f"Invalid component name '{component}'")
            elif isinstance(component, All_Nodes):
                for key, value in self.components.items():
                    if isinstance(value, dict) and value["component"] == component:
                        self.components.pop(key, None)
                        break

        return self

    def compile(
        self,
        ast: Optional[AST] = None,
        to_format: Format = Formats.HTML,
        indent: Optional[int] = None,
        scopes: Optional[list[str]] = None,
        safe_vars: bool = False,
        **kwargs: Any,
    ) -> str:
        """Execute compilation to a different format."""

        ast = ast or self.ast

        if ast is None:
            raise Exception("Must provide an ast to compile")

        # Insert the scopes into the path
        scopes = scopes or ["./"]
        if scopes is not None:
            from sys import path  # pylint: disable=import-outside-toplevel

            for scope in scopes:
                path.insert(0, scope)

        # Depending on the format parse with the appropriate function
        return to_format.compile(ast, self.components, indent, safe_vars=safe_vars, **kwargs)
