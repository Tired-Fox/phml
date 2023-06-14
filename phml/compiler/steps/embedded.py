from typing import Any

from phml.embedded import USED_VARS, exec_embedded, exec_embedded_blocks
from phml.helpers import build_recursive_context
from phml.nodes import Element, Literal, Parent

from .base import scoped_step

def _process_attributes(node: Element, context: dict[str, Any]) -> USED_VARS:
    used = []
    for attribute in list(node.attributes.keys()):
        if attribute.startswith(":"):
            used_vars, result = exec_embedded(
                str(node[attribute]).strip(),
                f"<{node.tag} {attribute}='{node[attribute]}'>",
                **context,
            )
            if result is not None:
                node.pop(attribute, None)
                node[attribute.lstrip(":")] = result
            used.extend(used_vars)
        else:
            if isinstance(node[attribute], str):
                used_vars, value = exec_embedded_blocks(
                    str(node.attributes[attribute]).strip(),
                    f"<{node.tag} {attribute}='{node.attributes[attribute]}'>",
                    **context,
                )
                if value is not None:
                    node[attribute] = value
                used.extend(used_vars)
    return used


@scoped_step
def step_execute_embedded_python(node: Parent, _, context: dict[str, Any], results: dict[str, Any]):
    """Step to process embedded python inside of attributes and text nodes."""

    if "used_vars" not in results:
        results["used_vars"] = []

    for child in node:
        ctxt = build_recursive_context(child, context)

        if isinstance(child, Element):
            results["used_vars"].extend(_process_attributes(child, ctxt))
        elif (
            Literal.is_text(child)
            and "{{" in child.content
            and child.parent.tag not in ["script", "style", "python", "code"]
        ):
            used, content = exec_embedded_blocks(
                child.content.strip(),
                f"Text in <{node.tag}> at {node.position!r}",
                **ctxt,
            )

            results["used_vars"].extend(used)
            child.content = f" {content.strip()}"

