from typing import Callable

from phml.nodes import Element, Root, All_Nodes
from phml.utils.test import Test, test
from .travel import walk


def filter_nodes(tree: Root | Element, condition: Test):
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
    
    if  tree.__class__.__name__ == "AST":
        tree = tree.tree

    def filter_children(node: Root | Element):
        node.children = [n for n in node.children if test(n, condition)] 
        for i, child in enumerate(node.children):
            if isinstance(child, (Root, Element)):
                filter_children(child)

    filter_children(tree)


def remove_nodes(tree: Root | Element, condition: Test):
    """Take a given tree and remove the nodes that match the condition.
    If a parent node is removed so is all the children.

    Same as filter_nodes except removes nodes that match.

    Args:
        tree (Root | Element): The parent node to start recursively removing from.
        condition (Test): The condition to apply to each node.
    """
    if tree.__class__.__name__ == "AST":
        tree = tree.tree

    def filter_children(node: Root | Element):
        node.children = [n for n in node.children if not test(n, condition)] 
        for child in node.children:
            if isinstance(child, (Root, Element)):
                filter_children(child)
                
    filter_children(tree)


def map_nodes(tree: Root | Element, transform: Callable):
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

    if  tree.__class__.__name__ == "AST":
        tree = tree.tree
        
    for node in walk(tree):
        node = transform(node)
        

def size(node: All_Nodes) -> int:
    """Get the number of nodes recursively."""

    count = 0

    for _ in walk(node):
        count += 1

    return count
