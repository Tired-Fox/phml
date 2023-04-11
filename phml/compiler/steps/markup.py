from pathlib import Path
from typing import Any

from phml.components import ComponentManager
from phml.embedded import exec_embedded
from phml.nodes import Element, Parent
from phml.utilities import sanatize

from .base import scoped_step

try:  # pragma: no cover
    from markdown import Markdown as PyMarkdown

    MARKDOWN = PyMarkdown
except ImportError:  # pragma: no cover
    error = Exception(
        "You do not have the package 'markdown' installed. Install it to be able to use <Markdown /> tags",
    )

    class Markdown:
        def __init__(self, *_a, **_k) -> None:
            raise error

        def registerExtensions(self, *_a, **_k):
            raise error

        def reset(self, *_a, **_k):
            raise error

    MARKDOWN = Markdown


@scoped_step
def step_compile_markdown(
    node: Parent, components: ComponentManager, context: dict[str, Any]
):
    """Step to compile markdown. This step only works when you have `markdown` installed."""
    from phml.core import HypertextManager

    md_tags = [
        child
        for child in node
        if isinstance(child, Element) and child.tag == "Markdown"
    ]

    if len(md_tags) > 0:
        markdown = MARKDOWN(extensions=["codehilite", "tables", "fenced_code"])
        for md in md_tags:
            extras = str(md.get(":extras", None) or md.pop("extras", None) or "")
            configs = md.pop(":configs", None)
            if configs is not None:
                configs = exec_embedded(
                    str(configs),
                    "<Markdown :configs='<dict>'",
                    **context,
                )
            if extras is not None:
                if ":extras" in md:
                    extras = exec_embedded(
                        str(md.pop(":extras")),
                        "<Markdown :extras='<list|str>'",
                        **context,
                    )
                if isinstance(extras, str):
                    extras = extras.split(" ")
                elif isinstance(extras, list):
                    markdown.registerExtensions(
                        extensions=extras, configs=configs or {}
                    )
                else:
                    raise TypeError(
                        "Expected ':extras' attribute to be a space seperated list as a str or a python list of str",
                    )

            src = md.pop(":src", None) or md.pop("src", None)
            if src is None or not isinstance(src, str):
                raise ValueError(
                    "<Markdown /> element must have a 'src' or ':src' attribute that is a string",
                )

            if context.get("_phml_path_", None) is not None:
                path = Path(context["_phml_path_"])
                if path.suffix not in ["", None]:
                    path = path.parent / Path(src)
                else:
                    path = path / Path(src)
            else:
                path = Path.cwd() / Path(src)

            if not path.is_file():
                raise FileNotFoundError(f"No markdown file at path '{path}'")

            with path.open("r", encoding="utf-8") as md_file:
                content = str(markdown.reset().convert(md_file.read()))

            phml = HypertextManager()
            phml.components = components
            ast = phml.parse(content).ast

            if len(ast) > 0 and md.parent is not None:
                wrapper = Element(
                    "article", attributes=md.attributes, children=ast.children
                )
                sanatize(wrapper)

                idx = md.parent.index(md)

                md.parent.remove(md)
                md.parent.insert(idx, wrapper)
