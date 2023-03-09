from copy import deepcopy
from typing import Optional

from phml.core.nodes import AST, NODE
from phml.core.virtual_python import VirtualPython
from phml.utilities.locate.find import find_all
from phml.utilities.transform import remove_nodes

from .compile import ASTRenderer, apply_conditions, apply_python
from .format import Format
from .parse import parse_hypertest_markup

from phml.types.config import Config


def parse_markup(data: str, class_name: str, auto_close: bool = True) -> AST:
    """Parse a string as a markup document."""
    return parse_hypertest_markup(data, class_name, auto_close)


class HTMLFormat(Format):
    """Logic for parsing and compiling html files."""

    extension: list[str] = ["html", "htm"]

    @classmethod
    def parse(cls, data: str, auto_close: bool = True) -> str:
        return parse_markup(data, cls.__name__, auto_close)

    @classmethod
    def compile(
        cls,
        ast: AST,
        config: Config,
        components: Optional[dict[str, dict[str, list | NODE]]] = None,
        **kwargs,
    ) -> AST:
        """Compile and process the given ast and return the resulting ast."""

        components = components or {}
        src = deepcopy(ast)

        # 1. Search for all python elements and get source info.
        #    - Remove when done
        virtual_python = VirtualPython()

        for python_block in find_all(src, {"tag": "python"}):
            if (
                len(python_block.children) == 1
                and python_block.children[0].type == "text"
            ):
                virtual_python += VirtualPython(
                    python_block.children[0].normalized(),
                    context={**kwargs}
                )

        remove_nodes(src, ["element", {"tag": "python"}])

        # 2. Replace specific element node with given replacement components
        # replace_components(src, components, virtual_python, **kwargs)

        # 3. Search each element and find @if, @elif, and @else
        #    - Execute those statements

        apply_conditions(src, config, virtual_python, components, **kwargs)

        for python_block in find_all(src, {"tag": "python"}):
            if (
                len(python_block.children) == 1
                and python_block.children[0].type == "text"
            ):
                virtual_python += VirtualPython(
                    python_block.children[0].normalized(),
                    context={**kwargs}
                )

        remove_nodes(src, ["element", {"tag": "python"}])

        # 4. Search for python blocks and process them.

        apply_python(src, virtual_python, **kwargs)
        remove_nodes(src, {"tag": "slot"})

        return src

    @classmethod
    def render(
        cls,
        ast: AST,
        config: Config,
        components: Optional[dict[str, dict[str, list | NODE]]] = None,
        indent: int = 4,
        **kwargs,
    ) -> str:
        indent = indent or 4
        components = components or {}
        src = ast

        # 1. Search for all python elements and get source info.
        #    - Remove when done
        virtual_python = VirtualPython()

        for python_block in find_all(src, {"tag": "python"}):
            if len(python_block.children) == 1:
                if python_block.children[0].type == "text":
                    virtual_python += VirtualPython(python_block.children[0].normalized())

        remove_nodes(src, ["element", {"tag": "python"}])

        # 2. Replace specific element node with given replacement components
        # replace_components(src, components, virtual_python, **kwargs)

        # 3. Search each element and find @if, @elif, and @else
        #    - Execute those statements

        apply_conditions(src, config, virtual_python, components, **kwargs)

        for python_block in find_all(src, {"tag": "python"}):
            if len(python_block.children) == 1:
                if python_block.children[0].type == "text":
                    virtual_python += VirtualPython(python_block.children[0].normalized())

        remove_nodes(src, ["element", {"tag": "python"}])

        # 4. Search for python blocks and process them.

        apply_python(src, virtual_python, **kwargs)
        remove_nodes(src, {"tag": "slot"})

        return ASTRenderer(src, indent).compile()
