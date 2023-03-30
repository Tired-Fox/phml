from typing import Any

from phml.nodes import Parent, AST, Element, Literal, LiteralType
from phml.helpers import normalize_indent
from phml.components import ComponentManager
from .base import boundry_step, comp_step

@boundry_step
def step_add_cached_component_elements(
    *,
    node: AST,
    components: ComponentManager
):
    """Step to add the cached script and style elements from components."""
    target = None
    for child in node:
        if isinstance(child, Element) and child.tag == "html":
            target = child
            for c in child:
                if isinstance(c, Element) and c.tag == "head":
                    target = c

    cache = components.get_cache()
    style = ""
    script = ""
    for cmpt in cache:
        styles = "\n".join(normalize_indent(s[0].content) for s in cache[cmpt]["styles"])
        style += f"\n{styles}"

        scripts = "\n".join(normalize_indent(s[0].content) for s in cache[cmpt]["scripts"])
        script += f"\n{scripts}"

    if len(style.strip()) > 0:
        style = Element("style", children=[Literal(LiteralType.Text, style)])
        if target is not None:
            target.append(style)
        else:
            node.append(style)

    if len(script.strip()) > 0:
        script = Element("script", children=[Literal(LiteralType.Text, script)])
        if target is not None:
            target.append(script)
        else:
            node.append(script)


@comp_step
def step_substitute_components(
    node: Parent,
    components: ComponentManager,
    context: dict[str, Any]
):
    """Step to substitute components in for matching nodes."""

    for child in node:
        if isinstance(child, Element) and child.tag in components:
            element = components[child.tag]["element"]
            props = components[child.tag]["props"]
            context = {**child.context, **components[child.tag]["context"]}

            attrs = {
                key: value for key, value in child.attributes.items()
                if key.lstrip(":") in props
            }
            props.update(attrs)
            context.update(props)

            elements = [element]
            # PERF:                 ˅ Not sure what to name this  
            if element.tag in ["", "Template"]: # wrapper tag
                if element.children is not None:
                    elements = element.children

            for elem in elements:
                elem.parent = child.parent
                if isinstance(elem, Element):
                    elem.context.update(context)

            idx = child.parent.children.index(child)
            child.parent.remove(child)
            child.parent.children[idx:idx] = elements

            components.cache(child.tag, components[child.tag])
