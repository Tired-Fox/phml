from phml.nodes import All_Nodes


def depth(el: All_Nodes) -> int:
    """Get the depth in the tree for a given node.

    -1 means that you passed in the tree itself and you are at the
    ast's root.
    """

    level = -1
    while el.parent is not None:
        level += 1
        el = el.parent

    return level
