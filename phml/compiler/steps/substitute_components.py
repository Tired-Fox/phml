from copy import deepcopy
import re
from typing import Any, TypedDict

from phml.nodes import Parent, AST, Element, Literal, LiteralType, Node
from phml.helpers import iterate_nodes, normalize_indent
from phml.components import ComponentManager
from .base import boundry_step, comp_step

def scope_styles(styles: list[Element], hash: int) -> str:
    """Parse styles and find selectors with regex. When a selector is found then add scoped
    hashed data attribute to the selector.
    """
    result = []
    for style in styles:
        lines = normalize_indent(style[0].content).split('\n')
        # PERF: More efficient and reliable way of grabbing start of selector
        if "scoped" in style:
            for i, line in enumerate(lines):
                match = re.match(r"^(\s*)([^@{\n]+) *\{ *$", line)
                if match is not None:
                    offset, selector = match.groups()
                    lines[i] = f"{offset}[data-phml-cmpt-scope='{hash}'] {selector.strip()} {{"

        result.extend(lines)

    return "\n".join(result)

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
        style += f'\n{scope_styles(cache[cmpt]["styles"], cache[cmpt]["hash"])}'

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

class SlotNames(TypedDict):
    __blank__: Node | None
    named: dict[str, Node]

class SlotChildren(TypedDict):
    __blank__: list[Node]
    named: dict[str, list[Node]]

def replace_slots(child: Element, component: Element):
    slots: SlotNames = {"__blank__": None, "named": {}}
    for node in iterate_nodes(component):
        if isinstance(node, Element) and node.tag == "Slot":
            if "name" in node: 
                name = str(node["name"])
                if name in slots["named"]:
                    raise ValueError("Can not have more that one of the same named slot in a component")
                slots["named"][name] = node
            else:
                if slots["__blank__"] is not None:
                    raise ValueError("Can not have more that one catch all slot in a component")
                slots["__blank__"] = node

    children: SlotChildren = {"__blank__": [], "named": {}}
    if len(child) > 0:
        for node in child:
            if isinstance(node, Element) and "slot" in node:
                slot = str(node["slot"])
                if slot not in children["named"]:
                    children["named"][slot] = []
                children["named"][slot].append(node)
            elif isinstance(node, Element):
                children["__blank__"].append(node)
            elif isinstance(node, Literal):
                children["__blank__"].append(node)

    if slots["__blank__"] is not None:
        slot = slots["__blank__"]
        parent = slot.parent
        if parent is not None:
            idx = parent.index(slot)
            parent.remove(slot)
            parent.insert(idx, children["__blank__"])

    for slot in slots["named"]:
        node = slots["named"][slot]
        parent = node.parent
        if parent is not None:
            if slot in children["named"]:
                idx = parent.index(node)
                parent.remove(node)
                parent.insert(idx, children["named"][slot])
            else:
                parent.remove(node)

@comp_step
def step_substitute_components(
    node: Parent,
    components: ComponentManager,
    context: dict[str, Any]
):
    """Step to substitute components in for matching nodes."""

    for child in node:
        if isinstance(child, Element) and child.tag in components:
            # Need a deep copy of the component as to not manipulate the cached comonent data
            element = deepcopy(components[child.tag]["element"])
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

            if child.parent is not None:
                idx = child.parent.index(child)
                child.parent.remove(child)
                component = Element(
                    "div",
                    attributes={"data-phml-cmpt-scope": f"{components[child.tag]['hash']}"},
                    children=elements,
                )

                if len(child) > 0:
                    replace_slots(child, component)

                child.parent[idx] = component
               

            components.cache(child.tag, components[child.tag])
