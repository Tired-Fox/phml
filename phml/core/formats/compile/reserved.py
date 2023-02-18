from __future__ import annotations

from copy import deepcopy
from re import match, sub
from traceback import print_exc

from teddecor import TED
from markdown2 import markdown

from phml.core.nodes import Root, Element, Text
from phml.core.virtual_python import VirtualPython, get_python_result
from phml.utilities import (
    visit_children,
    check,
    replace_node,
    sanatize
)

__all__ = [
    "RESERVED"
]

EXTRAS = [
    "cuddled-lists",
    "fenced-code-blocks",
    "header-ids",
    "footnotes",
    "strike",
]

def process_loops(node: Root | Element, virtual_python: VirtualPython, **kwargs):
    """Expands all `<For />` tags giving their children context for each iteration."""

    for_loops = [
        loop
        for loop in visit_children(node)
        if check(loop, {"tag": "For", ":each": True})
    ]

    kwargs.update(virtual_python.context)

    for loop in for_loops:
        if loop[":each"].strip() != "":
            children = run_phml_for(loop, **kwargs)
            replace_node(node, loop, children)
        else:
            replace_node(node, loop, None)

def process_markdown(node: Root | Element, virtual_python: VirtualPython, **kwargs):
    """Replace the `<Markdown />` element with it's `src` attributes parsed markdown string."""

    from phml import PHML

    md_elems: list[Element] = [
        loop 
        for loop in visit_children(node) 
        if check(loop, {"tag": "Markdown"})
    ]

    kwargs.update(virtual_python.context)
    context = build_locals(node, **kwargs)
    
    # Don't escape the html values from context for html tags in markdown strings
    kwargs["safe_vars"] = True

    for elem in md_elems:
        if elem.startend and ":src" in elem or "src" in elem:
            if ":src" in elem:
                src = str(get_python_result(elem[":src"], **context))
            else:
                src = str(elem["src"])

            html = markdown(src, extras=EXTRAS)
            replace_node(node, elem, PHML().parse(html).ast.tree.children)
        elif not elem.startend and len(elem.children) == 1 and isinstance(elem.children[0], Text):
            html = markdown(elem.children[0].normalized(), extras=EXTRAS)
            replace_node(node, elem, PHML().parse(html).ast.tree.children)
        else:
            replace_node(node, elem, None)

def process_html(node: Root | Element, virtual_python: VirtualPython, **kwargs):
    """Replace the `<HTML />` element with it's `src` attributes html string."""

    from phml import PHML

    md_elems: list[Element] = [
        loop 
        for loop in visit_children(node)
        if check(loop, {"tag": "HTML"})
    ]

    kwargs.update(virtual_python.context)
    context = build_locals(node, **kwargs)
    
    # Don't escape the html values from context
    kwargs["safe_vars"] = True

    for elem in md_elems:
        if not elem.startend:
            raise Exception(f"<HTML /> elements are not allowed to have children elements: {elem.position}")

        if ":src" in elem or "src" in elem:
            if ":src" in elem:
                src = str(get_python_result(elem[":src"], **context))
            else:
                src = str(elem["src"])

            ast = PHML().parse(src).ast
            # sanatize(ast)

            replace_node(node, elem, ast.tree.children)

def build_locals(child, **kwargs) -> dict:
    """Build a dictionary of local variables from a nodes inherited locals and
    the passed kwargs.
    """
    from phml.utilities import path  # pylint: disable=import-outside-toplevel

    clocals = {**kwargs}

    # Inherit locals from top down
    for parent in path(child):
        if parent.type == "element":
            clocals.update(parent.context)

    clocals.update(child.context)
    return clocals

def run_phml_for(node: Element, **kwargs) -> list:
    """Repeat the nested elements inside the `<For />` elements for the iterations provided by the
    `:each` attribute. The values from the `:each` attribute are exposed as context for each node in
    the `<For />` element for each iteration.

    Args:
        node (Element): The `<For />` element that is to be used.
    """
    clocals = build_locals(node)

    # Format for loop condition
    for_loop = sub(r"for |:\s*$", "", node[":each"]).strip()

    # Get local var names from for loop condition
    items = match(r"(for )?(.*)(?<= )in(?= )(.+)", for_loop)

    new_locals = [
        item.strip()
        for item in sub(
            r"\s+",
            " ",
            items.group(2),
        ).split(",")
    ]

    source = items.group(3)

    # Formatter for key value pairs
    key_value = "\"{key}\": {key}"

    # Set children position to 0 since all copies are generated
    children = node.children
    for child in children:
        child.position = None

    def children_with_context(context: dict):
        new_children = []
        for child in children:
            new_child = deepcopy(child)
            if check(new_child, "element"):
                new_child.context.update(context)
            new_children.append(new_child)
        return new_children

    expression = for_loop # original expression

    for_loop = f'''\
new_children = []
for {for_loop}:
    new_children.extend(
        children_with_context(
            {{{", ".join([f"{key_value.format(key=key)}" for key in new_locals])}}}
        )
    )
'''

    # Construct locals for dynamic for loops execution
    local_env = {
        "local_vals": clocals,
    }

    try:
        # Execute dynamic for loop
        exec(  # pylint: disable=exec-used
            for_loop,
            {
                **kwargs,
                **globals(),
                **clocals,
                "children_with_context": children_with_context
            },
            local_env,
        )
    except Exception:  # pylint: disable=broad-except
        TED.print(f"\\[[@Fred]*Error[@]\\] Failed to execute loop expression \
[@Fblue]@for[@]=[@Fgreen]'[@]{expression}[@Fgreen]'[@]")
        print_exc()

    # Return the new complete list of children after generation
    return local_env["new_children"]

RESERVED = {
    "For": process_loops,
    "Markdown": process_markdown,
    "HTML": process_html
}