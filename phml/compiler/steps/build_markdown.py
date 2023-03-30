from pathlib import Path
from typing import Any

from phml.nodes import Parent, Element
from phml.embedded import exec_embedded
from phml.components import ComponentManager
from .base import comp_step

try:
    from markdown import Markdown as PyMarkdown
    MARKDOWN = PyMarkdown
except ImportError:
    error = Exception(
        "You do not have the package 'markdown' installed. Install it to be able to use <Markdown /> tags"
    )
    class Markdown():
        def __init__(self, *args, **kwargs):
            raise error 
        def registerExtensions(self, *args, **kwargs):
            raise error 
        def reset(self, *args, **kwargs):
            raise error
    MARKDOWN = Markdown

@comp_step
def step_compile_markdown(*, node: Parent, components: ComponentManager, context: dict[str, Any]):
    """Step to compile markdown. This step only works when you have `markdown` installed."""
    from phml.core import PHML

    md_tags = [child for child in node if isinstance(child, Element) and child.tag == "Markdown"]

    if len(md_tags) > 0:
        markdown = MARKDOWN(extensions=["codehilite", "tables", "fenced_code"])
        for md in md_tags:
            if len(md) > 0:
                raise ValueError("Cannot have children in <Markdown /> element")

            extras = str(md.pop(":extra", None) or md.pop("extra", None) or "")
            configs = md.pop(":configs", None)
            if configs is not None:
                configs = exec_embedded(
                    str(configs),
                    "<Markdown :configs='<dict>'",
                    **context
                ) 
            if extras is not None:
                if ":extra" in md:
                    extras = exec_embedded(
                        extras,
                        "<Markdown :extras='<list|str>'",
                        **context
                    ) 
                if isinstance(extras, str):
                    extras = extras.split(" ")
                elif isinstance(extras, list):
                    markdown.registerExtensions(extensions=extras, configs=configs or {})
                else:
                    raise TypeError(
                        "Expected ':extras' attribute to be a space seperated list as a str or a python list of str"
                    )

            src = md.get(":src", None) or md.get("src", None)
            if src is None or not isinstance(src, str):
                raise ValueError(
                    "<Markdown /> element must have a 'src' or ':src' attribute that is a string"
                )

            path = Path(src).resolve()
            if not path.is_file():
                raise FileNotFoundError(f"No markdown file at path '{path}'")

            with path.open("r", encoding="utf-8") as md_file:
                content = str(markdown.reset().convert(md_file.read()))

            # TODO:
            # PERF: Sanatize the markdown
            phml = PHML()
            phml.components = components
            ast = phml.parse(content).ast

            if len(ast) > 0 and md.parent is not None:
                idx = md.parent.index(md)
                md.parent.remove(md)
                md.parent.insert(idx, Element("article", attributes=md.attributes, children=ast.children))

