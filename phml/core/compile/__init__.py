from typing import Any, Callable, Optional

from phml.nodes import All_Nodes, AST, DocType
from phml.core.file_types import HTML, PHML, JSON
from phml.utils import (
    parse_component,
    tag_from_file,
    visit_children,
    test,
)

from .convert import html, phml, json

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
        from phml.utils.parse_component() or the parsed ast of the component. Lastely,
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
                    else:
                        self.components[tag_from_file(key)] = value
            elif isinstance(component, tuple):
                if isinstance(component[1], AST):
                    self.components[tag_from_file(component[0])] = parse_component(component[1])
                else:
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
                    raise KeyError(f"Invalid component name {component}")
            elif isinstance(component, All_Nodes):
                for key, value in self.components:
                    if isinstance(value, dict) and value["component"] == component:
                        self.components.pop(key, None)
                        break
                    elif value == components:
                        self.components.pop(key, None)
                        break

        return self

    def compile(
        self,
        ast: Optional[AST] = None,
        to_format: str = HTML,
        indent: Optional[int] = None,
        handler: Optional[Callable] = None,
        **kwargs: Any,
    ) -> str:
        """Execute compilation to a different format."""

        ast = ast or self.ast
        
        if ast is None:
            raise Exception("Must provide an ast to compile.")

        doctypes = [dt for dt in visit_children(ast.tree) if test(dt, "doctype")]
        if len(doctypes) == 0:
            ast.tree.children.insert(0, DocType(parent=ast.tree))

        if to_format == PHML:
            return phml(ast, indent or 4)
        elif to_format == HTML:
            return html(ast, self.components, indent or 4, **kwargs)
        elif to_format == JSON:
            return json(ast, indent or 2)
        elif handler is None:
            raise Exception(f"Unkown format < { to_format } >")
        else:
            return handler(ast, indent)
