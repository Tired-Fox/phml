from copy import deepcopy
from typing import Optional

from phml.core.nodes import AST, All_Nodes
from phml.core.virtual_python import VirtualPython
from phml.utilities import find_all, remove_nodes

from .compile import ToML, apply_conditions, apply_python, replace_components
from .format import Format
from .parse import parse_hypertest_markup


def parse_markup(data: str, class_name: str) -> AST:
    """Parse a string as a markup document."""
    return parse_hypertest_markup(data, class_name)


class HTMLFormat(Format):
    """Logic for parsing and compiling html files."""

    extension: list[str] = ["html", "htm"]

    @classmethod
    def parse(cls, data: str) -> str:
        return parse_markup(data, cls.__name__)

    @classmethod
    def compile(
        cls,
        ast: AST,
        components: Optional[dict[str, dict[str, list | All_Nodes]]] = None,
        indent: int = 4,
        **kwargs,
    ) -> str:
        indent = indent or 4
        components = components or {}
        src = deepcopy(ast)

        # 1. Search for all python elements and get source info.
        #    - Remove when done
        virtual_python = VirtualPython()

        for python_block in find_all(src, {"tag": "python"}):
            if len(python_block.children) == 1:
                if python_block.children[0].type == "text":
                    virtual_python += VirtualPython(python_block.children[0].value)

        remove_nodes(src, ["element", {"tag": "python"}])

        # 2. Replace specific element node with given replacement components
        replace_components(src, components, virtual_python, **kwargs)

        for python_block in find_all(src, {"tag": "python"}):
            if len(python_block.children) == 1:
                if python_block.children[0].type == "text":
                    virtual_python += VirtualPython(python_block.children[0].value)

        remove_nodes(src, ["element", {"tag": "python"}])

        # 3. Search each element and find py-if, py-elif, py-else, and py-for
        #    - Execute those statements

        apply_conditions(src, virtual_python, **kwargs)

        # 4. Search for python blocks and process them.

        apply_python(src, virtual_python, **kwargs)

        return ToML(src, indent).compile()
