import re
from copy import deepcopy
from typing import Any, TypedDict

from phml.components import ComponentManager
from phml.helpers import iterate_nodes, normalize_indent
from phml.nodes import AST, Element, Literal, LiteralType, Node, Parent

from .base import post_step, scoped_step

DATA_ATTR = "data-phml-scope"

re_selector = re.compile(r"(\n|\}| *)([^}@/]+)(\s*{)")
re_split_selector = re.compile(r"(?:\)(?:.|\s)*|(?<!\()(?:.|\s)*)(,)")


def lstrip(value: str) -> tuple[str, str]:
    offset = len(value) - len(value.lstrip())
    return value[:offset], value[offset:]


def scope_style(style: str, scope: str) -> str:
    """Takes a styles string and adds a scope to the selectors."""

    next_style = re_selector.search(style)
    result = ""
    while next_style is not None:
        start, end = next_style.start(), next_style.start() + len(next_style.group(0))
        leading, selector, trail = next_style.groups()
        if start > 0:
            result += style[:start]
        result += leading

        parts = [""]
        balance = 0
        for char in selector:
            if char == "," and balance == 0:
                parts.append("")
                continue
            elif char == "(":
                balance += 1
            elif char == ")":
                balance = min(0, balance - 1)
            parts[-1] += char

        for i, part in enumerate(parts):
            w, s = lstrip(part)
            parts[i] = w + f"{scope} {s}"
        result += ",".join(parts) + trail

        style = style[end:]
        next_style = re_selector.search(style)
    if len(style) > 0:
        result += style

    return result


def scope_styles(styles: list[Element], hash: str) -> str:
    """Parse styles and find selectors with regex. When a selector is found then add scoped
    hashed data attribute to the selector.
    """
    result = []
    for style in styles:
        content = normalize_indent(style[0].content)
        if "scoped" in style:
            content = scope_style(content, f"[{DATA_ATTR}='{hash}']")

        result.append(content)

    return "\n".join(result)


@post_step
def step_add_cached_component_elements(node: AST, components: ComponentManager, _, results: dict[str, Any]):
    """Step to add the cached script and style elements from components."""
    from phml.utilities import query

    n_style = query(node, "head > style")
    n_script = query(node, "head > script")
    target = query(node, "head") or  node

    cache = components.get_cache()
    results["components"] = [key for key in cache.keys()]

    style = ""
    script = ""
    for cmpt in cache:
        style += f'\n{scope_styles(cache[cmpt]["styles"], cache[cmpt]["hash"])}'

        scripts = "\n".join(
            normalize_indent(s[0].content) for s in cache[cmpt]["scripts"]
        )
        script += f"\n{scripts}"

    if len(style.strip()) > 0:
        if n_style is not None:
            if len(n_style) == 0 or not Literal.is_text(n_style[0]):
                n_style.children = []
                n_style.append(Literal(LiteralType.Text, ""))
            n_style[0].content = normalize_indent(n_style[0].content) + style
        else:
            style = Element("style", children=[Literal(LiteralType.Text, style)])
            target.append(style)

    if len(script.strip()) > 0:
        if n_script is not None:
            if len(n_script) == 0 or not Literal.is_text(n_script[0]):
                n_script.children = []
                n_script.append(Literal(LiteralType.Text, ""))
            n_script[0].content = normalize_indent(n_script[0].content) + script
        else:
            script = Element("script", children=[Literal(LiteralType.Text, script)])
            target.append(script)

    components.clear_cache()


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
                    raise ValueError(
                        "Can not have more that one of the same named slot in a component"
                    )
                slots["named"][name] = node
            else:
                if slots["__blank__"] is not None:
                    raise ValueError(
                        "Can not have more that one catch all slot in a component"
                    )
                slots["__blank__"] = node

    children: SlotChildren = {"__blank__": [], "named": {}}
    for node in child:
        if isinstance(node, Element) and "slot" in node:
            slot = str(node["slot"])
            if slot not in children["named"]:
                children["named"][slot] = []
            node.pop("slot", None)
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


@scoped_step
def step_substitute_components(
    node: Parent,
    components: ComponentManager,
    *_
):
    """Step to substitute components in for matching nodes."""

    for child in node:
        if isinstance(child, Element) and child.tag in components:
            # Need a deep copy of the component as to not manipulate the cached component data
            elements = deepcopy(components[child.tag]["elements"])
            props = components[child.tag]["props"]
            ctxt = {**child.context, **components[child.tag]["context"]}

            attrs = {
                key: value
                for key, value in child.attributes.items()
                if key.lstrip(":") in props
            }

            props.update(attrs)
            ctxt.update({"props": props})

            component = Element(
                "div",
                attributes={DATA_ATTR: f"{components[child.tag]['hash']}"},
                children=[],
            )

            for elem in elements:
                elem.parent = component
                if isinstance(elem, Element):
                    elem.context.update(ctxt)

            component.extend(elements)

            if child.parent is not None:
                idx = child.parent.index(child)
                replace_slots(child, component)
                child.parent[idx] = component

            components.cache(child.tag, components[child.tag])
