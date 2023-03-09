"""phml.utilities.transform.transform

Utility methods that revolve around transforming or manipulating the ast.
"""

from typing import Callable, Optional

from phml.core.nodes import AST, NODE, Element, Root
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
    tree: Root | Element | AST,
    condition: Test,
    strict: bool = True,
):
    """Take a given tree and filter the nodes with the condition.
    Only nodes passing the condition stay. If the parent node fails,
    all children are moved up in scope. Depth first

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
        children = []
        for i, child in enumerate(node.children):
            if child.type in ["root", "element"]:
                node.children[i] = filter_children(node.children[i])
                if not check(child, condition, strict=strict):
                    for idx, _ in enumerate(child.children):
                        child.children[idx].parent = node
                    children.extend(node.children[i].children)
                else:
                    children.append(node.children[i])
            elif check(child, condition, strict=strict):
                children.append(node.children[i])

        node.children = children
        return node

    filter_children(tree)


def remove_nodes(
    tree: Root | Element | AST,
    condition: Test,
    strict: bool = True,
):
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
        node.children = [n for n in node.children if not check(n, condition, strict=strict)]
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

    def recursive_map(node):
        for i, child in enumerate(node.children):
            if isinstance(child, Element):
                recursive_map(node.children[i])
                node.children[i] = transform(child)
            else:
                node.children[i] = transform(child)

    recursive_map(tree)


def replace_node(
    start: Root | Element,
    condition: Test,
    replacement: Optional[NODE | list[NODE]],
    all_nodes: bool = False,
    strict: bool = True,
):
    """Search for a specific node in the tree and replace it with either
    a node or list of nodes. If replacement is None the found node is just removed.

    Args:
        start (Root | Element): The starting point.
        condition (test): Test condition to find the correct node.
        replacement (NODE | list[NODE] | None): What to replace the node with.
    """
    for node in walk(start):
        if check(node, condition, strict=strict):
            if node.parent is not None:
                idx = node.parent.children.index(node)
                if replacement is not None:
                    parent = node.parent
                    if isinstance(replacement, list):
                        for item in replacement:
                            item.parent = node.parent
                        parent.children = (
                            node.parent.children[:idx]
                            + replacement
                            + node.parent.children[idx + 1 :]
                        )
                    else:
                        replacement.parent = node.parent
                        parent.children = (
                            node.parent.children[:idx]
                            + [replacement]
                            + node.parent.children[idx + 1 :]
                        )
                else:
                    parent = node.parent
                    parent.children.pop(idx)

            if not all_nodes:
                break


def find_and_replace(start: Root | Element, *replacements: tuple[str, str | Callable]) -> int:
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
    from phml.utilities import visit_children  # pylint: disable=import-outside-toplevel

    def inner(start: AST | Element | Root):
        if isinstance(start, AST):
            start = start.tree

        for idx, child in enumerate(visit_children(start)):
            start.children[idx] = func(child, idx, child.parent)

    return inner
