"""phml.utilities.validate.test

Logic that allows nodes to be tested against a series of conditions.
"""

from __future__ import annotations

from typing import Callable

from phml.nodes import Element, Node

Test = list | str | dict | Callable[[Node], bool]


def check(
    node: Node,
    _test: Test,
    strict: bool = True,
) -> bool:
    """Test if a node passes the given test(s).

    Test Types:
        - `None`: Just checks that the node is a valid node.
        - `str`: Checks that the node is an element and the condition == node.tag.
        - `dict`: Checks all items are valid attributes on the node.
        and that the values are strictly equal.
        - `Callable`: Passes the given function the node and it's index, if provided,
        and checks if the callable returned true.
        - `list[Test]`: Apply all the rules above for each Test in the list.

    If the `parent` arg is passed so should the `index` arg.

    Args:
        node (Node): Node to test. Can be any phml node.
        test (Test): Test to apply to the node. See previous section
            for more info.

    Returns:
        True if all tests pass.
    """

    if isinstance(_test, str):
        return isinstance(node, Element) and node.tag == _test

    if isinstance(_test, dict):
        # If dict validate all items with properties are the same
        # Either in attributes or in
        if strict:
            return bool(
                isinstance(node, Element)
                and all(
                    (key in node and (value is True or value == node[key]))
                    for key, value in _test.items()
                ),
            )
        return bool(
            isinstance(node, Element)
            and any(
                (key in node and (value is True or value == node[key]))
                for key, value in _test.items()
            ),
        )

    if isinstance(_test, list):
        # If list then recursively apply tests
        if strict:
            return bool(
                all(isinstance(cond, Test) and check(node, cond) for cond in _test),
            )

        return bool(
            any(isinstance(cond, Test) and check(node, cond) for cond in _test),
        )

    if isinstance(_test, Callable):
        # If callable return result of collable after passing node, index, and parent
        return _test(node)

    raise TypeError(f"Invalid test condition: {_test}")
