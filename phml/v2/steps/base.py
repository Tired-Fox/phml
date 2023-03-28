from typing import Callable, Any
from functools import wraps
from inspect import getfullargspec

from ..nodes import Parent
from ..components import ComponentManager

def comp_step(func: Callable):
    """Wrapper for compilation steps. This wraps a function that takes a parent node,
    the current context, and mutates the nodes children. It is expected that this is not recursive.

    Args:
        Node (Parent): The parent node that is the current scope
        components (ComponentManager): The manager instance for the components
        context (dict[str, Any]): Additional global context from parent objects

    Note:
        There may be any combination of arguments, keyword only arguments, or catch alls with *arg and **kwarg.
        This wrapper will predictably and automatically pass the arguments that are specified.
    """
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
