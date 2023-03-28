from .base import boundry_step
from phml.v2.nodes import AST, Element

@boundry_step
def step_ensure_doctype(*, node: AST):
    """Step to sure that the final ast has a doctype node."""

    doctypes = [c for c in node if isinstance(c, Element) and c.tag == "doctype"]
    if len(doctypes) == 0:
        node.insert(0, Element("doctype", {"html": True}))
