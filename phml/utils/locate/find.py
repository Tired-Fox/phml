from typing import Optional

from phml.utils.validate import Test, test
from phml.utils.travel import walk, path

from phml.nodes import All_Nodes, Root, Element, AST

__all__ = [
    "ancestor",
    "find",
    "find_all",
    "find_after",
    "find_all_after",
    "find_all_before",
    "find_before",
    "find_all_between"
]

def ancestor(*nodes: All_Nodes) -> Optional[All_Nodes]:
    """Get the common ancestor between two nodes.

    Args:
        *nodes (All_Nodes): A list of any number of nodes
        to find the common ancestor form. Worst case it will
        return the root.

    Returns:
        Optional[All_Nodes]: The node that is the common
        ancestor or None if not found.
    """
    total_path: list = None

    for node in nodes:
        if total_path is not None:
            total_path = list(filter(lambda n: n in total_path, path(node)))
        else:
            total_path = path(node)

    return total_path[-1] if len(total_path) > 0 else None


def find(node: Root | Element | AST, condition: Test) -> Optional[All_Nodes]:
    """Walk the nodes children and return the desired node.

    Returns the first node that matches the condition.

    Args:
        node (Root | Element): Starting node.
        condition (Test): Condition to check against each node.

    Returns:
        Optional[All_Nodes]: Returns the found node or None if not found.
    """
    if isinstance(node, AST):
        node = node.tree
        
    for n in walk(node):
        if test(n, condition):
            return n

    return None


def find_all(node: Root | Element | AST, condition: Test) -> list[All_Nodes]:
    """Find all nodes that match the condition.

    Args:
        node (Root | Element): Starting node.
        condition (Test): Condition to apply to each node.

    Returns:
        list[All_Nodes]: List of found nodes. Empty if no nodes are found.
    """
    if isinstance(node, AST):
        node = node.tree

    results = []
    for n in walk(node):
        if test(n, condition):
            results.append(n)
    return results


def find_after(
    node: Root | Element | AST,
    condition: Optional[Test] = None,
) -> Optional[All_Nodes]:
    """Get the first sibling node following the provided node that matches
    the condition.

    Args:
        node (All_Nodes): Node to get sibling from.
        condition (Test): Condition to check against each node.

    Returns:
        Optional[All_Nodes]: Returns the first sibling or None if there
        are no siblings.
    """
    if isinstance(node, AST):
        node = node.tree

    idx = node.parent.children.index(node)
    if len(node.parent.children) - 1 > idx:
        for el in node.parent.children[idx + 1 :]:
            if condition is not None:
                if test(el, condition):
                    return el
            else:
                return el
    return None


def find_all_after(
    node: Element,
    condition: Optional[Test] = None,
) -> list[All_Nodes]:
    """Get all sibling nodes that match the condition.

    Args:
        node (All_Nodes): Node to get siblings from.
        condition (Test): Condition to check against each node.

    Returns:
        list[All_Nodes]: Returns the all siblings that match the
        condition or an empty list if none were found.
    """
    idx = node.parent.children.index(node)
    matches = []

    if len(node.parent.children) - 1 > idx:
        for el in node.parent.children[idx + 1:]:
            if condition is not None:
                if test(el, condition):
                    matches.append(el)
            else:
                matches.append(el)
    
    return matches


def find_before(
    node: Element,
    condition: Optional[Test] = None,
) -> Optional[All_Nodes]:
    """Find the first sibling node before the given node. If a condition is applied
    then it will be the first sibling node that passes that condition.

    Args:
        node (All_Nodes): The node to find the previous sibling from.
        condition (Optional[Test]): The test that is applied to each node.

    Returns:
        Optional[All_Nodes]: The first node before the given node
        or None if no prior siblings.
    """
    if isinstance(node, AST):
        node = node.tree
        
    idx = node.parent.children.index(node)
    if idx > 0:
        for el in node.parent.children[idx - 1 :: -1]:
            if condition is not None:
                if test(el, condition):
                    return el
            else:
                return el
    return None


def find_all_before(
    node: Element,
    condition: Optional[Test] = None,
) -> list[All_Nodes]:
    """Find all nodes that come before the given node.

    Args:
        node (All_Nodes): The node to find all previous siblings from.
        condition (Optional[Test]): The condition to apply to each node.

    Returns:
        list[All_Nodes]: A list of nodes that come before the given node.
        Empty list if no nodes were found.
    """
    idx = node.parent.children.index(node)
    matches = []

    if idx > 0:
        for el in node.parent.children[:idx]:
            if condition is not None:
                if test(el, condition):
                    matches.append(el)
            else:
                matches.append(el)
    return matches


def find_all_between(
    parent: Root | Element | AST,
    start: Optional[int] = 0,
    end: Optional[int] = 0,
    condition: Optional[Test] = None,
    _range: Optional[slice] = None,
) -> list[All_Nodes]:
    """Find all sibling nodes in parent that meet the provided condition from start index
    to end index.

    Args:
        parent (Root | Element): The parent element to get nodes from.
        start (int, optional): The starting index, inclusive. Defaults to 0.
        end (int, optional): The ending index, exclusive. Defaults to 0.
        condition (Test, optional): Condition to apply to each node. Defaults to None.
        _range (slice, optional): Slice to apply to the parent nodes children instead of start and end indecies. Defaults to None.

    Returns:
        list[All_Nodes]: List of all matching nodes or an empty list if none were found.
    """
    if isinstance(parent, AST):
        parent = parent.tree

    if _range is not None:
        start = _range.start
        end = _range.stop

    results = []
    if start >= 0 and end <= len(parent.children) and start < end:
        for node in parent.children[start:end]:
            if condition is not None:
                if test(node, condition):
                    results.append(node)
            else:
                results.append(node)
    return results