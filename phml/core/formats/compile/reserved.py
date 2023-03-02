from __future__ import annotations

from copy import deepcopy
from re import match, sub
from traceback import print_exc

from saimll import SAIML
from markdown import Markdown

from phml.core.nodes import Root, Element, Text
from phml.core.virtual_python import VirtualPython, get_python_result
from phml.utilities import (
    visit_children,
    check,
    replace_node,
    # sanatize
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

MARKDOWN = Markdown(extensions=["codehilite", "tables", "fenced_code"])

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
    """Replace the `<Markdown />` element with it's `src` attributes parsed markdown
    string."""

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
        markdown = MARKDOWN
        rendered_html = []

        # If extras are provided then add them as extensions. Don't allow configs
        # and only allow extensions built into the markdown package.
        if "extra" in elem:
            markdown = deepcopy(MARKDOWN)
            markdown.registerExtensions(
                [
                    extra.strip()
                    for extra in elem["extra"].split(" ")
                    if extra.strip() != ""
                ],
                {}
            )
        elif ":extra" in elem:
            extra_list = get_python_result(elem[":extra"], **context)
            if not isinstance(extra_list, list):
                raise TypeError("Expected extra's to be a list of strings")
            markdown = deepcopy(MARKDOWN)
            markdown.registerExtensions(extra_list, {})

        # Append the rendered markdown from the children, src, and referenced
        # file in that order
        if (
            not elem.startend
            and len(elem.children) == 1
            and isinstance(elem.children[0], Text)
        ):
            html = markdown.reset().convert(elem.children[0].normalized())
            rendered_html.append(html)

        if ":src" in elem or "src" in elem:
            if ":src" in elem:
                src = str(
                    get_python_result(
                        elem[":src"],
                        **context
                    )
                )
            else:
                src = elem["src"]
            html = markdown.reset().convert(src)
            rendered_html.append(html)

        if "file" in elem:
            with open(elem["file"], "r", encoding="utf-8") as md_file:
                html = markdown.reset().convert(md_file.read())

            rendered_html.append(html)

        # Replace node with rendered nodes of the markdown. Remove node if no
        # markdown was provided
        if len(rendered_html) > 0:
            replace_node(
                node,
                elem,
                PHML().parse('\n'.join(rendered_html)).ast.tree.children
            )
        else:
            replace_node(
                node,
                elem,
                None
            )


def process_html(
    node: Root | Element,
    virtual_python: VirtualPython,
    **kwargs
):
    """Replace the `<HTML />` element with it's `src` attributes html string.
    """

    from phml import PHML

    html_elems: list[Element] = [
        elem 
        for elem in visit_children(node)
        if check(elem, {"tag": "HTML"})
    ]

    kwargs.update(virtual_python.context)
    context = build_locals(node, **kwargs)

    # Don't escape the html values from context
    kwargs["safe_vars"] = True

    for elem in html_elems:
        if not elem.startend:
            raise TypeError(
                f"<HTML /> elements are not allowed to have children \
elements: {elem.position}"
            )

        if ":src" in elem or "src" in elem:
            if ":src" in elem:
                src = str(get_python_result(elem[":src"], **context))
            else:
                src = str(elem["src"])

            ast = PHML().parse(src).ast
            print(ast.tree)
            # sanatize(ast)

            replace_node(node, elem, ast.tree.children)
        else:
            print("REMOVING HTML NODE")
            replace_node(node, elem, None)

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

    if hasattr(child, "context"):
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

    items.group(3)

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
        SAIML.print(f"\\[[@Fred]*Error[@]\\] Failed to execute loop expression \
[@Fblue]@for[@]=[@Fgreen]'[@]{expression}[@Fgreen]'[@]")
        print_exc()

    # Return the new complete list of children after generation
    return local_env["new_children"]

RESERVED = {
    "For": process_loops,
    "Markdown": process_markdown,
    "HTML": process_html
}