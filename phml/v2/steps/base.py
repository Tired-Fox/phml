from typing import Callable, Any
from functools import wraps
from inspect import getfullargspec

from ..nodes import Parent
from ..components import ComponentManager

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
