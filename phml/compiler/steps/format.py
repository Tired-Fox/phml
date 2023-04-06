from phml.nodes import AST, Element

from .base import boundry_step


@boundry_step
def step_ensure_doctype(node: AST, *_):  # pragma: no cover
    """Step to sure that the final ast has a doctype node."""

    doctypes = [c for c in node if isinstance(c, Element) and c.tag == "doctype"]
    if len(doctypes) == 0:
        node.insert(0, Element("doctype", {"html": True}))
