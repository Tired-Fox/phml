from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from phml import All_Nodes, Root, Element

Test = None | str | list | dict | Callable

def test(
    node: All_Nodes,
    _test: Test,
    index: Optional[int] = None,
    parent: Optional[Root | Element] = None,
) -> bool:
    """Test if a node passes the given test(s).

    Test Types:
        - `None`: Just checks that the node is a valid node.
        - `str`: Checks that the test value is == the `node.type`.
        - `dict`: Checks all items are valid attributes on the node.
        and that the values are strictly equal.
        - `Callable`: Passes the given function the node and it's index, if provided,
        and checks if the callable returned true.
        - `list[Test]`: Apply all the rules above for each Test in the list.
        
    If the `parent` arg is passed so should the `index` arg.

    Args:
        node (All_Nodes): Node to test. Can be any phml node.
        test (Test): Test to apply to the node. See previous section
        for more info.
        index (Optional[int], optional): Index in the parent where the
        node exists. Defaults to None.
        parent (Optional[Root | Element], optional): The nodes parent. Defaults to None.

    Returns:
        True if all tests pass.
    """
    if parent is not None:
        # If parent is given then index has to be also.
        #   Validate index is correct in parent.children
        if index is None or parent.children[index] is not node:
            return False

    if _test is None:
        if not isinstance(node, All_Nodes):
            return False
        else:
            return True
    elif isinstance(_test, str):
        # If string then validate that the type is the same
        return hasattr(node, "type") and node.type == _test
    elif isinstance(_test, dict):
        # If dict validate all items with properties are the same
        # Either in attributes or in
        for key, value in _test.items():
            if not hasattr(node, key) or value != getattr(node, key):
                if not hasattr(node, "properties") or key not in node.properties or value != node.properties[key]:
                    return False
        return True
    elif isinstance(_test, list):
        # If list then recursively apply tests
        for t in _test:
            if isinstance(t, Test):
                if not test(node, t, index, parent):
                    return False
        return True
    elif isinstance(test, Callable):
        # If callable return result of collable after passing node, index, and parent
        return _test(node, index, parent)
    else:
        print("NOTHING TO SEE HERE")
