"""phml.utilities.locate.find

Collection of utility methods to find one or many of a specific node.
"""

from phml.nodes import Node, Parent
from phml.utilities.travel.travel import path, walk
from phml.utilities.validate import Test, check

__all__ = [
    "ancestor",
    "find",
    "find_all",
    "find_after",
    "find_all_after",
    "find_all_before",
    "find_before",
    "find_all_between",
]


def ancestor(*nodes: Node) -> Node | None:
    """Get the common ancestor between two nodes.

    Args:
        *nodes (Node): A list of any number of nodes
        to find the common ancestor form. Worst case it will
        return the root.

    Returns:
        Optional[Node]: The node that is the common
        ancestor or None if not found.
    """
    total_path: list | None = None

    def filter_func(node, total_path) -> bool:
        return node in total_path

    for node in nodes:
        if total_path is not None:
            total_path = list(filter(lambda n: filter_func(n, total_path), path(node)))
        else:
            total_path = path(node)

    total_path = total_path or []
    return total_path[-1] if len(total_path) > 0 else None


def find(start: Parent, condition: Test, strict: bool = True) -> Node | None:
    """Walk the nodes children and return the desired node.

    Returns the first node that matches the condition.

    Args:
        start (Parent): Starting node.
        condition (Test): Condition to check against each node.

    Returns:
        Optional[Node]: Returns the found node or None if not found.
    """
    for node in walk(start):
        if check(node, condition, strict=strict):
            return node

    return None


def find_all(start: Parent, condition: Test, strict: bool = True) -> list[Node]:
    """Find all nodes that match the condition.

    Args:
        start (Root | Element): Starting node.
        condition (Test): Condition to apply to each node.

    Returns:
        list[Node]: List of found nodes. Empty if no nodes are found.
    """
    results = []
    for node in walk(start):
        if check(node, condition, strict=strict):
            results.append(node)
    return results


def find_after(
    start: Node,
    condition: Test | None = None,
    strict: bool = True,
) -> Node | None:
    """Get the first sibling node following the provided node that matches
    the condition.

    Args:
        start (Node): Node to get sibling from.
        condition (Test): Condition to check against each node.

    Returns:
        Optional[Node]: Returns the first sibling or None if there
        are no siblings.
    """

    if start.parent is not None:
        idx = start.parent.index(start)
        if len(start.parent) - 1 > idx:
            for node in start.parent[idx + 1:]:
                if condition is not None:
                    if check(node, condition, strict=strict):
                        return node
                else:
                    return node
    return None


def find_all_after(
    start: Node,
    condition: Test | None = None,
    strict: bool = True,
) -> list[Node]:
    """Get all sibling nodes that match the condition.

    Args:
        start (Node): Node to get siblings from.
        condition (Test): Condition to check against each node.

    Returns:
        list[Node]: Returns the all siblings that match the
        condition or an empty list if none were found.
    """
    if start.parent is None:
        return []

    idx = start.parent.index(start)
    matches = []

    if len(start.parent) - 1 > idx:
        for node in start.parent[idx + 1 :]:
            if condition is not None:
                if check(node, condition, strict=strict):
                    matches.append(node)
            else:
                matches.append(node)

    return matches


def find_before(
    start: Node,
    condition: Test | None = None,
    strict: bool = True,
) -> Node | None:
    """Find the first sibling node before the given node. If a condition is applied
    then it will be the first sibling node that passes that condition.

    Args:
        start (Node): The node to find the previous sibling from.
        condition (Optional[Test]): The test that is applied to each node.

    Returns:
        Optional[Node]: The first node before the given node
        or None if no prior siblings.
    """

    if start.parent is not None:
        idx = start.parent.index(start)
        if idx > 0:
            for node in start.parent[idx - 1::-1]:
                if condition is not None:
                    if check(node, condition, strict=strict):
                        return node
                else:
                    return node
    return None


def find_all_before(
    start: Node,
    condition: Test | None = None,
    strict: bool = True,
) -> list[Node]:
    """Find all nodes that come before the given node.

    Args:
        start (Node): The node to find all previous siblings from.
        condition (Optional[Test]): The condition to apply to each node.

    Returns:
        list[Node]: A list of nodes that come before the given node.
        Empty list if no nodes were found.
    """
    if start.parent is None:
        return []

    idx = start.parent.index(start)
    matches = []

    if idx > 0:
        for node in start.parent[:idx]:
            if condition is not None:
                if check(node, condition, strict=strict):
                    matches.append(node)
            else:
                matches.append(node)
    return matches


def find_all_between(
    parent: Parent,
    start: int = 0,
    end: int | None = None,
    condition: Test | None = None,
    strict: bool = True,
) -> list[Node]:
    """Find all sibling nodes in parent that meet the provided condition from start index
    to end index.

    Args:
        parent (Parent): The parent element to get nodes from.
        start (int, optional): The starting index, inclusive. Defaults to 0.
        end (int, optional): The ending index, exclusive. Defaults to 0.
        condition (Test, optional): Condition to apply to each node. Defaults to None.

    Returns:
        list[Node]: List of all matching nodes or an empty list if none were found.
    """
    end = end or len(parent)

    results = []
    if start < len(parent) and end <= len(parent):
        for node in parent[start:end]:
            if condition is not None:
                if check(node, condition, strict=strict):
                    results.append(node)
            else:
                results.append(node)
    return results

