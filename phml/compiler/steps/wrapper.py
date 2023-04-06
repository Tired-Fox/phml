from phml.compiler.steps.base import comp_step
from phml.nodes import Element, Parent


@comp_step
def step_replace_phml_wrapper(node: Parent, *_):
    for child in list(node):
        if isinstance(child, Element) and child.tag in ["", "Template"]:
            idx = node.index(child)
            for c in child:
                if isinstance(c, Element):
                    c.context.update(child.context)

            del node[idx]
            node.insert(idx, child.children or [])
