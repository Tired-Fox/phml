import re
from copy import deepcopy
from typing import Any

from phml.embedded import exec_embedded
from phml.helpers import build_recursive_context
from phml.nodes import Element, Literal, Parent

from .base import scoped_step


def _update_fallbacks(node: Element, exc: Exception):
    fallbacks = _get_fallbacks(node)
    for fallback in fallbacks:
        fallback.context["_loop_fail_"] = exc


def _remove_fallbacks(node: Element):
    fallbacks = _get_fallbacks(node)
    for fallback in fallbacks:
        if fallback.parent is not None:
            fallback.parent.remove(fallback)


def _get_fallbacks(node: Element) -> list[Element]:
    fallbacks = []
    if node.parent is not None:
        idx = node.parent.index(node)
        for i in range(idx + 1, len(node.parent)):
            if isinstance(node.parent[i], Element):
                if "@elif" in node.parent[i]:
                    fallbacks.append(node.parent[i])
                    continue
                elif "@else" in node.parent[i]:
                    fallbacks.append(node.parent[i])

            # Ignore comments
            if not Literal.is_comment(node.parent[i]):
                break
    return fallbacks


def replace_default(
    node: Element, exc: Exception, sub: Element = Element("", {"@if": "False"})
):
    """Set loop node to a False if condition and update all sibling fallbacks with the
    loop failure exception.
    """
    if node.parent is not None and len(node.parent) > 0:
        node.attributes.pop("@elif", None)
        node.attributes.pop("@else", None)
        node.attributes["@if"] = "False"

        _update_fallbacks(node, exc)


@scoped_step
def step_expand_loop_tags(
    node: Parent,
    _,
    context: dict[str, Any],
    _results
):
    """Step to process and expand all loop (<For/>) elements. Will also set loop elements
    to have a false condition attribute to allow for fallback sibling elements."""
    if len(node) == 0:
        return

    for_loops = [
        child
        for child in node
        if isinstance(child, Element) and child.tag == "For" and len(node) > 0
    ]

    def gen_new_children(node: Parent, context: dict[str, Any]) -> list:
        new_children = deepcopy(node[:])
        for child in new_children:
            if isinstance(child, Element):
                child.context.update(context)
            child.parent = None
            child._position = None
        return new_children

    for loop in for_loops:
        parsed_loop = re.match(
            r"(?:for\\s*)?(?P<captures>.+) in (?P<source>.+):?",
            str(loop.get(":each", loop.get("each", ""))),
        )

        if parsed_loop is None:
            raise ValueError(
                "Expected expression in 'each' attribute for <For/> to be a valid list comprehension.",
            )

        parsed_loop = parsed_loop.groupdict()

        captures = re.findall(r"([^\s,]+)", parsed_loop["captures"])
        parsed_loop["source"].strip()

        def dict_key(a):
            return f"'{a}':{a}"

        process = f"""\
__children__ = []
__iterations__ = 0
for {loop.get(":each", loop.get("each", ""))}:
    __children__.extend(
        __gen_new_children__(
            __node__,
            {{{','.join(dict_key(key) for key in captures)}}}
        )
    )
    __iterations__ += 1
(__iterations__, __children__)
"""

        if ":each" in loop:
            _each = f':each="{loop[":each"]}"'
        else:
            _each = f'each="{loop["each"]}"'

        try:
            iterations, new_nodes = exec_embedded(
                process,
                f"<For {_each}>",
                **build_recursive_context(loop, context),
                __gen_new_children__=gen_new_children,
                __node__=loop,
            )

            if iterations == 0:
                replace_default(
                    loop,
                    Exception("No iterations occured. Expected non empty iterator."),
                )
            elif loop.parent is not None:
                _remove_fallbacks(loop)

                idx = loop.parent.index(loop)
                loop.parent.remove(loop)
                loop.parent.insert(idx, new_nodes)
        except Exception as exec:
            replace_default(loop, exec)
