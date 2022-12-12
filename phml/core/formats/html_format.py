from copy import deepcopy
from typing import Optional

from phml.core.nodes import All_Nodes, AST
from phml.core.virtual_python import VirtualPython
from phml.utilities import remove_nodes, find_all

from .format import Format
from .compile import replace_components, apply_conditions, apply_python, ToML
from .parse import HypertextMarkupParser

class HTMLFormat(Format):
    """Logic for parsing and compiling html files."""

    extension: list[str] = ["html", "htm"]

    @classmethod
    def parse(cls, data: ...) -> str:
        phml_parser = HypertextMarkupParser()

        if isinstance(data, str):
            try:
                phml_parser.feed(data)
                if len(phml_parser.cur_tags) > 0:
                    last = phml_parser.cur_tags[-1].position
                    raise Exception(
                        f"Unbalanced tags in source at [{last.start.line}:{last.start.column}]"
                    )
                return AST(phml_parser.cur)
            except Exception as exception:
                raise Exception(
                    f"{data[:6] + '...' if len(data) > 6 else data}\
: {exception}"
                ) from exception
        raise Exception("Data passed to HTMLFormat.parse must be a str")

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
