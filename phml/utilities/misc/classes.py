"""utilities.misc

A collection of utilities that don't fit in with finding, selecting, testing,
transforming, traveling, or validating nodes.
"""

from re import split, sub
from typing import Optional

from phml.core.nodes import NODE, Element

__all__ = ["classnames", "ClassList"]


def classnames(  # pylint: disable=keyword-arg-before-vararg
    node: Optional[Element] = None, *conditionals: str | int | list | dict[str, bool]
) -> str:
    """Concat a bunch of class names. Can take a str as a class,
    int which is cast to a str to be a class, a dict of conditional classes,
    and a list of all the previous conditions including itself.

    Examples:
        Assume that the current class on node is `bold`
    * `classnames(node, 'flex')` yields `'bold flex'`
    * `classnames(node, 13)` yields `'bold 13'`
    * `classnames(node, {'shadow': True, 'border': 0})` yields `'bold shadow'`
    * `classnames('a', 13, {'b': True}, ['c', {'d': False}])` yields `'a b c'`

    Args:
        node (Element | None): Node to apply the classes too. If no node is given
        then the function returns a string.

    Returns:
        str: The concat string of classes after processing.
    """

    node, conditionals = validate_node(node, conditionals)

    classes = init_classes(node)

    for condition in conditionals:
        if isinstance(condition, str):
            classes.extend(
                [
                    klass
                    for klass in split(r" ", sub(r" +", "", condition.strip()))
                    if klass not in classes
                ]
            )
        elif isinstance(condition, int) and str(condition) not in classes:
            classes.append(str(condition))
        elif isinstance(condition, dict):
            for key, value in condition.items():
                if value:
                    classes.extend(
                        [
                            klass
                            for klass in split(r" ", sub(r" +", "", key.strip()))
                            if klass not in classes
                        ]
                    )
        elif isinstance(condition, list):
            classes.extend(
                [klass for klass in classnames(*condition).split(" ") if klass not in classes]
            )
        else:
            raise TypeError(f"Unkown conditional statement: {condition}")

    if node is None:
        return " ".join(classes)

    node["class"] = " ".join(classes)
    return None


class ClassList:
    """Utility class to manipulate the class list on a node.

    Based on the hast-util-class-list:
    https://github.com/brechtcs/hast-util-class-list
    """

    def __init__(self, node: Element):
        self.node = node
        self.classes = node["class"].split(" ") if "class" in node.properties else []

    def contains(self, klass: str):
        """Check if `class` contains a certain class."""

        return klass.strip().replace(" ", "-") in self.classes

    def toggle(self, *klasses: str):
        """Toggle a class in `class`."""

        for klass in klasses:
            if klass.strip().replace(" ", "-") in self.classes:
                self.classes.remove(klass.strip().replace(" ", "-"))
            else:
                self.classes.append(klass.strip().replace(" ", "-"))

        self.node["class"] = self.class_list()

    def add(self, *klasses: str):
        """Add one or more classes to `class`."""

        for klass in klasses:
            if klass not in self.classes:
                self.classes.append(klass.strip().replace(" ", "-"))

        self.node["class"] = self.class_list()

    def replace(self, old_class: str, new_class: str):
        """Replace a certain class in `class` with
        another class.
        """

        old_class = old_class.strip().replace(" ", "-")
        new_class = new_class.strip().replace(" ", "-")

        if old_class in self.classes:
            idx = self.classes.index(old_class)
            self.classes[idx] = new_class
            self.node["class"] = self.class_list()

    def remove(self, *klasses: str):
        """Remove one or more classes from `class`."""

        for klass in klasses:
            if klass in self.classes:
                self.classes.remove(klass)

        if len(self.classes) == 0:
            self.node.properties.pop("class", None)
        else:
            self.node["class"] = self.class_list()

    def class_list(self) -> str:
        """Return the formatted string of classes."""
        return ' '.join(self.classes)


def validate_node(node, conditionals: list) -> bool:
    """Validate a node is a node and that it is an element."""
    if not isinstance(node, NODE):
        return None, [node, *conditionals]

    if not isinstance(node, Element):
        raise TypeError("Node must be an element")

    return node, conditionals


def init_classes(node) -> list[str]:
    """Get the list of classes from an element."""
    if node is not None:
        if "class" in node.properties:
            return sub(r" +", " ", node["class"]).split(" ")

        node["class"] = ""
        return []

    return []
