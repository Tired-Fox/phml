"""utils.misc

A collection of utilities that don't fit in with finding, selecting, testing,
transforming, traveling, or validating nodes.
"""

from re import search, split, sub
from typing import Optional

from phml.nodes import Element

__all__ = ["classnames", "ClassList"]


def classnames(
    node: Optional[Element] = None, *conditionals: str | int | list | dict[str, bool]
) -> str:
    """Concat a bunch of class names. Can take a str as a class,
    int which is cast to a str to be a class, a dict of conditional classes,
    and a list of all the previous conditions including itself.

    Examples:
    * `classnames(node, 'flex')` yields `'flex'`
    * `classnames(node, 13)` yields `'13'`
    * `classnames(node, {'shadow': True, 'border': 0})` yields `'shadow'`
    * `classnames(node, 'a', 13, {'b': True}, ['c', {'d': False}])` yields `'a b c'`

    Args:
        node (Element | None): Node to apply the classes too. If no node is given
        then the function returns a string.

    Returns:
        str: The concat string of classes after processing.
    """

    classes = []
    for condition in conditionals:
        if isinstance(condition, str):
            classes.extend(split(r" ", sub(r" +", "", condition.strip())))
        elif isinstance(condition, int):
            classes.append(str(condition))
        elif isinstance(condition, dict):
            for key, value in condition.items():
                if value:
                    classes.extend(split(r" ", sub(r" +", "", key.strip())))
        elif isinstance(condition, list):
            classes.extend(classnames(*condition).split(" "))
        else:
            raise TypeError(f"Unkown conditional statement: {condition}")

    if node is None:
        return " ".join(classes)
    else:
        node.properties["class"] = node.properties["class"] or "" + f" {' '.join(classes)}"


class ClassList:
    """Utility class to manipulate the class list on a node.

    Based on the hast-util-class-list:
    https://github.com/brechtcs/hast-util-class-list
    """

    def __init__(self, node: Element):
        self.node = node

    def contains(self, klass: str):
        """Check if `class` contains a certain class."""
        from phml.utils import has_property

        if has_property(self.node, "class"):
            return search(klass, self.node.properties["class"]) is not None
        return False

    def toggle(self, *klasses: str):
        """Toggle a class in `class`."""

        for klass in klasses:
            if search(f"\b{klass}\b", self.node.properties["class"]) is not None:
                sub(f"\b{klass}\b", "", self.node.properties["class"])
                sub(r" +", " ", self.node.properties["class"])
            else:
                self.node.properties["class"] = self.node.properties["class"].strip() + f" {klass}"

    def add(self, *klasses: str):
        """Add one or more classes to `class`."""

        for klass in klasses:
            if search(f"\b{klass}\b", self.node.properties["class"]) is None:
                self.node.properties["class"] = self.node.properties["class"].strip() + f" {klass}"

    def replace(self, old_klass: str, new_klass: str):
        """Replace a certain class in `class` with
        another class.
        """

        if search(f"\b{old_klass}\b", self.node.properties["class"]) is not None:
            sub(f"\b{old_klass}\b", f"\b{new_klass}\b", self.node.properties["class"])
            sub(r" +", " ", self.node.properties["class"])

    def remove(self, *klasses: str):
        """Remove one or more classes from `class`."""

        for klass in klasses:
            if search(f"\b{klass}\b", self.node.properties["class"]) is not None:
                sub(f"\b{klass}\b", "", self.node.properties["class"])
                sub(r" +", " ", self.node.properties["class"])
