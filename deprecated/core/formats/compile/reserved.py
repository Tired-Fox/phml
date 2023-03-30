from __future__ import annotations

from copy import deepcopy
from re import match, sub
from typing import Any
from pyparsing import sys

from saimll import SAIML
from markdown import Markdown

from phml.core.nodes import Root, Element, Text
from phml.core.virtual_python import VirtualPython, get_python_result
from phml.core.print_errors import print_warn
from phml.utilities import (
    visit_children,
    check,
    replace_node,
    find_all_after,
    find_after,
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

def process_loops(node: Root | Element, virtual_python: VirtualPython, compile_context: dict, **kwargs):
    """Expands all `<For />` tags giving their children context for each iteration."""
    for_loops = [
        loop
        for loop in visit_children(node)
        if check(loop, {"tag": "For"})
    ]

    kwargs.update(virtual_python.context)

    for loop in for_loops:
        fallbacks = get_for_fallbacks(loop)
        each = loop.get(":each", loop.get("each"))
        if each is not None and each.strip() != "":
            result = run_phml_for(loop, **kwargs)
            if result.success and result.count > 0:
                remove_fallbacks(node, fallbacks)
                replace_node(node, loop, result.children)
            else:
                # Replace For element with a blank element with a always false if condition
                # This allows for the following @elif and @else to be run as fallbacks
                replace_node(node, loop, Element("", {"@if": "False"}))
                update_fallbacks(fallbacks, result)
                print_warn(compile_context.get("file", ""), loop, result.error)
        else:
            remove_fallbacks(node, fallbacks)
            replace_node(node, loop, None)

def update_fallbacks(fallbacks: list[Element], result: ForResult):
    for fallback in fallbacks:
        fallback.context["for_except"] = result.message

def remove_fallbacks(node: Root|Element, fallbacks: list[Element]):
    for fallback in fallbacks:
        replace_node(node, fallback, None)

def get_for_fallbacks(loop: Element) -> list[Element]:
    fallbacks: list[Element] = find_all_after(loop, {"@elif": True, "@if": True}, False)
    if len(fallbacks) == 0:
        else_cond: Element = find_after(loop, {"@else": True})
    else:
        if "@if" in fallbacks[0]:
            return []

        for i, fallback in enumerate(fallbacks):
            if "@if" in fallback:
                return fallbacks[:i]

        else_cond: Element = find_after(fallbacks[-1], {"@else": True})

    if else_cond is not None:
       fallbacks.append(else_cond) 
    return fallbacks

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

class ForResult:
    """Holds the results for running a `For` elements iterations."""

    success: bool
    """Success of the for loop/element iteration."""
    message: str
    """Possible error message if the for loop threw an exeption."""
    children: list
    """The new children generated by the for loop/element."""
    error: str
    """PHML error message for what happened."""

    def __init__(self) -> None:
        self.success = True
        self.message = ""
        self.error = ""
        self.children = []

    @property
    def count(self) -> int:
        """Get the number of iterations/count of children."""
        return len(self.children)

    def __repr__(self) -> str:
        return f"ForResult(success: {self.success}, count: {self.count}, message: {self.message})"

def run_phml_for(node: Element, **kwargs) -> ForResult:
    """Repeat the nested elements inside the `<For />` elements for the iterations provided by the
    `:each` attribute. The values from the `:each` attribute are exposed as context for each node in
    the `<For />` element for each iteration.

    Args:
        node (Element): The `<For />` element that is to be used.

    Returns:
        list of new children and whether the for loop errored out along with how many iterations
        occured.
    """
    clocals = build_locals(node)
    result = ForResult()

    # Format for loop condition
    for_loop = sub(r"for |:\s*$", "", node.get(":each", node.get("each"))).strip()

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

    of_local=items.group(3)

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
            if isinstance(new_child, Element):
                new_child.context.update(context)
            new_children.append(new_child)
        return new_children

    expression = for_loop # original expression

    for_loop = f'''\
new_children = []
iteration = 0
for {for_loop}:
    new_children.extend(
        children_with_context(
            {{{", ".join([f"{key_value.format(key=key)}" for key in new_locals])}}}
        )
    )
    iteration += 1
'''

    # Construct locals for dynamic for loops execution
    local_env: dict[str, Any] = {
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
    except Exception as exc:  # pylint: disable=broad-except
        result.error = (
            SAIML.parse(
                f"Failed to execute loop attribute [@Fblue]:each[@]=[@Fgreen]'[@]{', '.join(new_locals)} [@Fmagenta]in[@F]{of_local}[@Fgreen]'[@] because: {exc}"
            )
        )
        result.success = False
        result.message = str(exc) 

    result.children = local_env["new_children"]
    return result 

RESERVED = {
    "For": process_loops,
    "Markdown": process_markdown,
    "HTML": process_html
}
