from copy import deepcopy
from pathlib import Path
from typing import Optional
from re import sub, match
from defusedxml.ElementTree import fromstring

from phml.core.nodes import All_Nodes, AST, Element, Text, Root, PI
from phml.core.virtual_python import VirtualPython

from .format import Format
from .compile import ToML, apply_conditions, apply_python

__all__ = ["XMLFormat"]


def tag(element) -> str:
    """Parse the element tag from the xml tag.

    Example:
        `{http://www.sitemaps.org/schemas/sitemap/0.9}url`
        yields
        `url`
    """
    return sub(r"\{[^}]+\}", "", element.tag)


def namespace(element) -> str:
    """Get the xmlns value from the tag prefix."""
    xmlns = match(r"\{([^}]+)\}", element.tag)
    return xmlns.group(1) or ""


def construct_element(element):
    """Construct a phml element from a xml element."""

    current = Element(tag(element), {**element.attrib})

    if element.text is not None and element.text.strip() != "":
        current.append(Text(element.text))

    if len(element) > 0:
        for child in element:
            current.append(construct_element(child))

    return current


class XMLFormat(Format):
    """Logic for parsing and compiling html files."""

    extension: str = "xml"

    @classmethod
    def parse(cls, data: ...) -> str:
        if isinstance(data, Path):
            with open(data, "r", encoding="utf-8") as file:
                data = file.read()

        if isinstance(data, str):
            root = fromstring(data)
            _namespace = namespace(root)
            root = AST(Root(children=[construct_element(root)]))

            if _namespace != "":
                root.children[0]["xmlns"] = _namespace

            return root
        raise Exception("Data passed into XMLFormat.parse must be either str or pathlib.Path")

    @classmethod
    def compile(
        cls,
        ast: AST,
        components: Optional[dict[str, dict[str, list | All_Nodes]]] = None,
        indent: int = 2,
        **kwargs,
    ) -> str:
        indent = indent or 2

        attribs = {
            "version": kwargs.pop("version", None) or "1.0",
            "encoding": kwargs.pop("encoding", None) or "UTF-8",
        }

        ast.tree.insert(0, PI("xml", attribs))

        src = deepcopy(ast)

        # 3. Search each element and find py-if, py-elif, py-else, and py-for
        #    - Execute those statements

        apply_conditions(src, VirtualPython(), **kwargs)

        # 4. Search for python blocks and process them.

        apply_python(src, VirtualPython(), **kwargs)

        return ToML(src, indent).compile(include_doctype=False)
