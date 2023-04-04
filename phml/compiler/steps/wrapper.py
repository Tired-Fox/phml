from phml.compiler.steps.base import comp_step
from phml.nodes import Parent, Element


@comp_step
def step_replace_phml_wrapper(*, node: Parent):
    for child in node:
        if isinstance(child, Element) and child.tag in ["", "Template"]:
            idx = child.parent.index(child)
            for c in child:
                if isinstance(c, Element):
                    c.context.update(child.context)

            del child.parent[idx]
            child.parent.insert(idx, child.children or [])
