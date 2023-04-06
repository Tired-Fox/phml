from functools import wraps
from inspect import getfullargspec
from typing import Any, Callable

from phml.components import ComponentManager
from phml.nodes import AST, Parent


def comp_step(func: Callable[[Parent, ComponentManager, dict[str, Any]], None]):  # pragma: no cover
    """Wrapper for compilation steps. This wraps a function that takes a parent node,
    the current context, and component manager. The function is expected to mutate the children nodes.
    It is also expected that the function is not recursive and only mutates the direct children of the node
    passed in.

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
        context: dict[str, Any],
    ):
        return func(node, components, context)
    return inner


def boundry_step(func: Callable[[AST, ComponentManager, dict[str, Any]], None]):  # pragma: no cover
    """Wrapper for setup and post compile steps. This wraps a function that takes an AST node,
    the current context, and the component manager. The funciton is expected to mutate the AST recursively

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
        node: AST,
        components: ComponentManager,
        context: dict[str, Any],
    ):
        return func(node, components, context)
    return inner
