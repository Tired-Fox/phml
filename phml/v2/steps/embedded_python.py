from typing import Any
from html import escape

from ..embedded import exec_embedded, exec_embedded_blocks
from ..nodes import Element, Literal, Parent
from ..utils import build_recursive_context
from .base import comp_step

ESCAPE_OPTIONS = {
    "quote": False
}

def escape_args(args: dict):
    """Take a dictionary of args and escape the html inside string values.

    Args:
        args (dict): Collection of values to html escape.

    Returns:
        A html escaped collection of arguments.
    """

    for key in args:
        if isinstance(args[key], str):
            args[key] = escape(args[key], **ESCAPE_OPTIONS)

def _process_attributes(node: Element, context: dict[str, Any]):
    context = build_recursive_context(node, context)
    for attribute in list(node.attributes.keys()):
        if attribute.startswith(":"):
            result = exec_embedded(
                str(node[attribute]).strip(),
                f"<{node.tag} {attribute}='{node[attribute]}'>",
                **context
            )
            node.pop(attribute, None)
            node[attribute.lstrip(":")] = str(escape(result, **ESCAPE_OPTIONS))
        else:
            if isinstance(node[attribute], str):
                value = exec_embedded_blocks(
                    str(node.attributes[attribute]).strip(),
                    f"<{node.tag} {attribute}='{node.attributes[attribute]}'>",
                    **context
                )
                node[attribute] = escape(value, **ESCAPE_OPTIONS) 

@comp_step
def step_execute_embedded_python(*, node: Parent, context: dict[str, Any]):
    """Step to process embedded python inside of attributes and text nodes."""
    for child in node:
        if isinstance(child, Element):
            _process_attributes(
                    child, 
                    build_recursive_context(child, context)
            )
        elif Literal.is_text(child):
            if "{{" in child.content:
                child.content = escape(
                    exec_embedded_blocks(
                        child.content.strip(),
                        f"Text in <{node.tag}> at {node.position!r}",
                        **build_recursive_context(child, context)
                    ),
                    **ESCAPE_OPTIONS
                )

