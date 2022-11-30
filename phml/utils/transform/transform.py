from typing import Callable, Optional

from phml.nodes import AST, All_Nodes, Element, Root
from phml.utils.misc import heading_rank
from phml.utils.travel import walk
from phml.utils.validate.test import Test, test

__all__ = [
    "filter_nodes",
    "remove_nodes",
    "map_nodes",
    "find_and_replace",
    "shift_heading",
    "replace_node",
]


def filter_nodes(tree: Root | Element | AST, condition: Test):
    """Take a given tree and filter the nodes with the condition.
    Only nodes passing the condition stay. If the parent node fails,
    then all children are removed.

    Same as remove_nodes but keeps the nodes that match.

    Args:
        tree (Root | Element): The tree node to filter.
        condition (Test): The condition to apply to each node.

    Returns:
        Root | Element: The given tree after being filtered.
    """

    if tree.__class__.__name__ == "AST":
        tree = tree.tree

    def filter_children(node):
        node.children = [n for n in node.children if test(n, condition)]
        for child in node.children:
            if child.type in ["root", "element"]:
                filter_children(child)

    filter_children(tree)


def remove_nodes(tree: Root | Element | AST, condition: Test):
    """Take a given tree and remove the nodes that match the condition.
    If a parent node is removed so is all the children.

    Same as filter_nodes except removes nodes that match.

    Args:
        tree (Root | Element): The parent node to start recursively removing from.
        condition (Test): The condition to apply to each node.
    """
    if tree.__class__.__name__ == "AST":
        tree = tree.tree

    def filter_children(node):
        node.children = [n for n in node.children if not test(n, condition)]
        for child in node.children:
            if child.type in ["root", "element"]:
                filter_children(child)

    filter_children(tree)


def map_nodes(tree: Root | Element | AST, transform: Callable):
    """Takes a tree and a callable that returns a node and maps each node.

    Signature for the transform function should be as follows:

    1. Takes a single argument that is the node.
    2. Returns any type of node that is assigned to the original node.

    ```python
    def to_links(node):
        return Element("a", {}, node.parent, children=node.children)
            if node.type == "element"
            else node
    ```

    Args:
        tree (Root | Element): Tree to transform.
        transform (Callable): The Callable that returns a node that is assigned
        to each node.
    """

    if tree.__class__.__name__ == "AST":
        tree = tree.tree

    for node in walk(tree):
        if not isinstance(node, Root):
            node = transform(node)


def replace_node(
    node: Root | Element, condition: Test, replacement: Optional[All_Nodes | list[All_Nodes]]
):
    """Search for a specific node in the tree and replace it with either
    a node or list of nodes. If replacement is None the found node is just removed.

    Args:
        node (Root | Element): The starting point.
        condition (test): Test condition to find the correct node.
        replacement (All_Nodes | list[All_Nodes] | None): What to replace the node with.
    """
    for n in walk(node):
        if test(n, condition):
            if n.parent is not None:
                idx = n.parent.children.index(n)
                if replacement is not None:
                    n.parent.children = (
                        n.parent.children[:idx] + replacement + n.parent.children[idx + 1 :]
                        if isinstance(replacement, list)
                        else n.parent.children[:idx] + [replacement] + n.parent.children[idx + 1 :]
                    )
                else:
                    n.parent.children.pop(idx)
                break


def find_and_replace(node: Root | Element, *replacements: tuple[str, str | Callable]) -> int:
    """Takes a ast, root, or any node and replaces text in `text`
    nodes with matching replacements.

    First value in each replacement tuple is the regex to match and
    the second value is what to replace it with. This can either be
    a string or a callable that returns a string or a new node. If
    a new node is returned then the text element will be split.
    """
    from re import finditer

    for n in walk(node):
        if n.type == "text":
            for replacement in replacements:
                if isinstance(replacement[1], str):
                    for match in finditer(replacement[0], n.value):
                        n.value = n.value[: match.start()] + replacement[1] + n.value[match.end() :]
                else:
                    raise NotImplementedError(
                        "Callables are not yet supported for find_and_replace operations."
                    )
                # TODO add ability to inject nodes in place of text replacement
                # elif isinstance(replacement[1], Callable):
                #     for match in finditer(replacement[0], n.value):
                #         result = replacement[1](match.group())
                #         if isinstance(result, str):
                #             n.value = n.value[:match.start()] + replacement[1] + n.value[match.end():]
                #         elif isinstance(result, All_Nodes):
                #             pass
                #         elif isinstance(result, list):
                #             pass


def shift_heading(node: Element, amount: int):
    """Shift the heading by the amount specified.

    value is clamped between 1 and 6.
    """

    rank = heading_rank(node)
    rank += amount

    node.tag = f"h{min(6, max(1, rank))}"


def modify_children(func):
    """Function wrapper that when called and passed an
    AST, Root, or Element will apply the wrapped function
    to each child. This means that whatever is returned
    from the wrapped function will be assigned to the child.

    The wrapped function will be passed the child node,
    the index in the parents children, and the parent node
    """
    from phml.utils import visit_children

    def inner(start: AST | Element | Root):
        if isinstance(start, AST):
            start = start.tree

        for idx, child in enumerate(visit_children(start)):
            start.children[idx] = func(child, idx, child.parent)

    return inner
