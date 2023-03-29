from pathlib import Path
from typing import Any

from phml.v2.nodes import Parent, Element
from phml.v2.components import ComponentManager
from phml.v2.core import PHML
from phml.v2.embedded import exec_embedded
from .base import comp_step

try:
    from markdown import Markdown as PyMarkdown
    MARKDOWN = PyMarkdown
except ImportError:
    class Markdown():
        def __init__(self, *args, **kwargs):
            raise Exception(
                "You do not have the package 'markdown' installed. Install it to be able to use <Markdown /> tags"
            )
    MARKDOWN = PyMarkdown

@comp_step
def step_compile_markdown(*, node: Parent, components: ComponentManager, context: dict[str, Any]):
    """Step to compile markdown. This step only works when you have `markdown` installed."""

    md_tags = [child for child in node if isinstance(child, Element) and child.tag == "Markdown"]

    if len(md_tags) > 0:
        markdown = MARKDOWN(extensions=["codehilite", "tables", "fenced_code"])
        for md in md_tags:
            if len(md) > 0:
                raise ValueError("Cannot have children in <Markdown /> element")

            extras = md.get(":extra") or md.get("extra")
            configs = md.get(":configs")
            if configs is not None:
                configs = exec_embedded(
                    str(configs),
                    "<Markdown :configs='<configs:dict>'",
                    **context
                ) 
            if extras is not None:
                if isinstance(extras, str):
                    extras = extras.split(" ")
                elif isinstance(extras, list):
                    markdown.registerExtensions(extensions=extras, configs=configs or {})
                raise TypeError(
                    "Expected ':extras' attribute to be a space seperated list as a str or a python list of str"
                )

            src = md.get(":src") or md.get("src")
            if src is None or not isinstance(src, str):
                raise ValueError(
                    "<Markdown /> element must have a 'src' or ':src' attribute that is a string"
                )

            path = Path(src).resolve()
            if not path.is_file():
                raise FileNotFoundError(f"No markdown file at path {src!r}")

            with path.open("r", encoding="utf-8") as md_file:
                content = str(markdown.reset().convert(md_file.read()))

            # TODO:
            # PERF: Sanatize the markdown
            ast = PHML.parse(content).ast
            if len(ast) > 0 and md.parent is not None:
                idx = md.parent.children.index(md)
                md.parent.remove(md)
                md.parent.insert(idx, ast.children)

