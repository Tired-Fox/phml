
# TODO: For each scope apply list of steps
# - Each step takes; node, context, component manager
# - Each step mutates the current scope
from copy import deepcopy
from functools import wraps
from inspect import getfullargspec
import re
from typing import Any, Callable

from nodes import Parent, Element
from components import ComponentManager
from embedded import exec_embedded

def comp_step(func: Callable):
    @wraps(func)
    def inner(
        node: Parent,
        components: ComponentManager,
        context: dict[str, Any]
    ):
        (
            args,
            varargs,
            varkw,
            _,
            kwonlyargs,
            _,
            _,
        ) = getfullargspec(func)
        values={ "node": node, "components": components, "context": context }
        if args is not None and len(args) > 0:
            # If less then full amount is specifiec then only pass in amount specified
            return func(*[node, components, context][:min(len(args), len(values))])
        elif kwonlyargs is not None and len(kwonlyargs) > 0:
            return func(**{key: values[key] for key in kwonlyargs if key in values})
        elif varargs is not None:
            return func(node, components, context)
        elif varkw is not None:
            return func(node=node, components=components, context=context)
        raise TypeError("Step methods are expected to have a combination of args, kwargs, *, and **")
    return inner

@comp_step
def compile_for_tags(
    *,
    node: Parent,
    context: dict[str, Any]
):
    if node.children is None:
        return

    for_loops = [
        child for child in node
        if isinstance(child, Element)
        and child.tag == "For"
        and node.children is not None
    ]

    def gen_new_children(node: Parent, context: dict[str, Any]) -> list:
        new_children = deepcopy(node.children or [])
        for child in new_children:
            if isinstance(child, Element):
                child.context.update(context)
            child.parent = None
            child._position = None
        return new_children


    for loop in for_loops:

        parsed_loop = re.match(
                r"(?:for\s*)?(?P<captures>.+) in (?P<source>.+):?",
                loop.get(":each", loop.get("each", ""))
        )

        if parsed_loop is None:
            raise ValueError(
                "Expected expression in 'each' attribute for <For/> to be a valid list comprehension."
            )

        parsed_loop = parsed_loop.groupdict()

        captures = re.findall(r"([^\s,]+)", parsed_loop["captures"])
        source = parsed_loop["source"].strip()

        dict_key = lambda a: f"'{a}':{a}"
        process = f"""\
__children__ = []
for {loop.get(":each", loop.get("each"))}:
    __children__.extend(
        __gen_new_children__(
            __node__,
            {{{','.join(dict_key(key) for key in captures)}}}
        )
    )
__children__
"""
        if ":each" in loop:
            _each = f':each="{loop[":each"]}"'
        elif "each" in loop:
            _each = f':each="{loop[":each"]}"'
        else:
            _each = ""

        new_nodes = exec_embedded(
            process,
            f"<For {_each}>",
            **context,
            __gen_new_children__=gen_new_children,
            __node__=loop,
        )

        # TODO: Add fallbacks for Loop element

        if loop.parent is not None:
            idx = loop.parent.children.index(loop)
            loop.parent.remove(loop)
            loop.parent.insert(idx, new_nodes)
