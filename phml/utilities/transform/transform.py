"""phml.utilities.transform.transform

Utility methods that revolve around transforming or manipulating the ast.
"""

from typing import Callable, Optional

from phml.nodes import AST, Node, Element, Parent 
from phml.utilities.misc import heading_rank
from phml.utilities.travel.travel import walk
from phml.utilities.validate.check import Test, check

__all__ = [
    "filter_nodes",
    "remove_nodes",
    "map_nodes",
    "find_and_replace",
    "shift_heading",
    "replace_node",
    "modify_children",
]


def filter_nodes(
    tree: Parent,
    condition: Test,
    strict: bool = True,
):
    """Take a given tree and filter the nodes with the condition.
    Only nodes passing the condition stay. If the parent node fails,
    all children are moved up in scope. Depth first

    Same as remove_nodes but keeps the nodes that match.

    Args:
        tree (Parent): The tree node to filter.
        condition (Test): The condition to apply to each node.

    Returns:
        Parent: The given tree after being filtered.
    """

    def filter_children(node):
        children = []
        for i, child in enumerate(node):
            if isinstance(child, Parent):
                node[i] = filter_children(node[i])
                if not check(child, condition, strict=strict):
                    for idx, _ in enumerate(child):
                        child[idx].parent = node
                    children.extend(node[i].children or [])
                else:
                    children.append(node[i])
            elif check(child, condition, strict=strict):
                children.append(node[i])

        node.children = children
        return node

    filter_children(tree)


def remove_nodes(
    tree: Parent,
    condition: Test,
    strict: bool = True,
):
    """Take a given tree and remove the nodes that match the condition.
    If a parent node is removed so is all the children.

    Same as filter_nodes except removes nodes that match.

    Args:
        tree (Parent): The parent node to start recursively removing from.
        condition (Test): The condition to apply to each node.
    """

    def filter_children(node):
        node.children = [n for n in node if not check(n, condition, strict=strict)]
        for child in node:
            if isinstance(child, Parent):
                filter_children(child)

    filter_children(tree)


def map_nodes(tree: Parent, transform: Callable):
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
        tree (Parent): Tree to transform.
        transform (Callable): The Callable that returns a node that is assigned
        to each node.
    """

    def recursive_map(node):
        for i, child in enumerate(node):
            if isinstance(child, Element):
                recursive_map(node[i])
                node[i] = transform(child)
            else:
                node[i] = transform(child)

    recursive_map(tree)


def replace_node(
    start: Parent,
    condition: Test,
    replacement: Node | list[Node] | None,
    all_nodes: bool = False,
    strict: bool = True,
):
    """Search for a specific node in the tree and replace it with either
    a node or list of nodes. If replacement is None the found node is just removed.

    Args:
        start (Parent): The starting point.
        condition (test): Test condition to find the correct node.
        replacement (Node | list[Node] | None): What to replace the node with.
    """
    for node in walk(start):
        if check(node, condition, strict=strict):
            if node.parent is not None:
                idx = node.parent.index(node)
                if replacement is not None:
                    parent = node.parent
                    if isinstance(replacement, list):
                        for item in replacement:
                            item.parent = node.parent
                        parent.children = [
                            *node.parent[:idx],
                            replacement,
                            *node.parent[idx + 1 :]
                        ]
                    else:
                        replacement.parent = node.parent
                        parent.children = [
                            *node.parent[:idx],
                            replacement,
                            *node.parent[idx + 1 :]
                        ]
                else:
                    parent = node.parent
                    parent.pop(idx)

            if not all_nodes:
                break


def find_and_replace(start: Parent, *replacements: tuple[str, str | Callable]):
    """Takes a ast, root, or any node and replaces text in `text`
    nodes with matching replacements.

    First value in each replacement tuple is the regex to match and
    the second value is what to replace it with. This can either be
    a string or a callable that returns a string or a new node. If
    a new node is returned then the text element will be split.
    """
    from re import finditer  # pylint: disable=import-outside-toplevel

    for node in walk(start):
        if node.type == "text":
            for replacement in replacements:
                if isinstance(replacement[1], str):
                    for match in finditer(replacement[0], node.value):
                        node.value = (
                            node.value[: match.start()] + replacement[1] + node.value[match.end() :]
                        )


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

    def inner(start: Parent):
        for idx, child in enumerate(start):
            start[idx] = func(child, idx, child.parent)

    return inner
