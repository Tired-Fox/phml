from typing import Optional


def depth(el) -> int:
    """Get the depth in the tree for a given node.

    -1 means that you passed in the tree itself and you are at the
    ast's root.
    """

    level = -1
    while el.parent is not None:
        level += 1
        el = el.parent

    return level


def has_property(node, attribute: str) -> bool:
    """Check to see if an element has a certain property in properties."""
    if node.type == "element":
        if attribute in node.properties:
            return True
    return False


def classnames(node=None, *conditionals: str | int | list | dict[str, bool]) -> str:
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
    from re import split, sub

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

    def __init__(self, node):
        if node.type == "element":
            self.node = node
        else:
            raise TypeError("node must be an `Element`.")

    def contains(self, klass: str):
        """Check if `class` contains a certain class."""

        if has_property(self.node, "class"):
            from re import search

            return search(klass, self.node.properties["class"]) is not None
        return False

    def toggle(self, *klasses: str):
        """Toggle a class in `class`."""
        from re import search, sub

        for klass in klasses:
            if search(f"\b{klass}\b", self.node.properties["class"]) is not None:
                sub(f"\b{klass}\b", "", self.node.properties["class"])
                sub(r" +", " ", self.node.properties["class"])
            else:
                self.node.properties["class"] = (
                    self.node.properties["class"].strip() + f" {klass}"
                )

    def add(self, *klasses: str):
        """Add one or more classes to `class`."""
        from re import search

        for klass in klasses:
            if search(f"\b{klass}\b", self.node.properties["class"]) is None:
                self.node.properties["class"] = (
                    self.node.properties["class"].strip() + f" {klass}"
                )

    def replace(self, old_klass: str, new_klass: str):
        """Replace a certain class in `class` with
        another class.
        """
        from re import search, sub

        if search(f"\b{old_klass}\b", self.node.properties["class"]) is not None:
            sub(f"\b{old_klass}\b", f"\b{new_klass}\b", self.node.properties["class"])
            sub(r" +", " ", self.node.properties["class"])

    def remove(self, *klasses: str):
        """Remove one or more classes from `class`."""
        from re import search, sub

        for klass in klasses:
            if search(f"\b{klass}\b", self.node.properties["class"]) is not None:
                sub(f"\b{klass}\b", "", self.node.properties["class"])
                sub(r" +", " ", self.node.properties["class"])


def heading(node) -> bool:
    """Check if an element is a heading."""
    from re import match

    return node.type == "element" and match(r"h[1-6]", node.tag) is not None


def heading_rank(node) -> int:
    """Get the rank of the heading element.

    Example:
        `h2` yields `2`
    """

    from re import match

    if heading(node):
        rank = match(r"", node.tag).group(1)
        return int(rank)
    else:
        raise TypeError(f"Node must be a heading. Was a {node.type}.{node.tag}")


def shift_heading(node, amount: int):
    """Shift the heading by the amount specified.

    value is clamped between 1 and 6.
    """

    rank = heading_rank(node)
    rank += amount

    node.tag = f"h{min(6, max(1, rank))}"


def is_css_link(node) -> bool:
    """Check if an element is a `link` to a css file.

    Returns `true` if `node` is a `<link>` element with a `rel` list that
    contains `'stylesheet'` and has no `type`, an empty `type`, or `'text/css'`
    as its `type`
    """

    from re import split, sub

    return (
        # Verify it is a element with a `link` tag
        is_element(node, "link")
        # Must have a rel list with stylesheet
        and has_property(node, "rel")
        and "stylesheet" in split(r" ", sub(r" +", " ", node.properties["rel"]))
        and (
            # Can have a `type` of `text/css` or empty or no `type`
            not has_property(node, "type")
            or (
                has_property(node, "type")
                and (node.properties["type"] == "text/css" or node.properties["type"] == "")
            )
        )
    )


def is_css_style(node) -> bool:
    """Check if an element is a css `style` element.

    Returns `true` if `node` is a `<style>` element that
    has no `type`, an empty `type`, or `'text/css'` as its `type`.
    """

    return is_element(node, "style") and (
        not has_property(node, "type")
        or (
            has_property(node, "type")
            and (node.properties["type"] == "" or node.properties["type"] == "text/css")
        )
    )


def is_javascript(node) -> bool:
    """Check if an element is a javascript `script` element.

    Returns `true` if `node` is a `<script>` element that has a valid JavaScript `type`, has no `type` and a valid JavaScript `language`, or has neither.
    """
    return is_element(node, "script") and (
        (
            has_property(node, "type")
            and node.properties["type"] in ["text/ecmascript", "text/javascript"]
            and not has_property(node, "language")
        )
        or (
            has_property(node, "language")
            and node.properties["language"] in ["ecmascript", "javascript"]
            and not has_property(node, "type")
        )
        or (not has_property(node, "type") and not has_property(node, "language"))
    )


def is_element(node, condition: str | list) -> bool:
    """Checks if the given node is a certain element.

    When providing an str it will check that the elements tag matches.
    If a list is provided it checks that one of the conditions in the list
    passes.
    """

    if node.type != "element":
        return False

    if isinstance(condition, str):
        return node.tag == condition
    elif isinstance(condition, list):
        for c in condition:
            if node.tag == c:
                return True
        return False


def is_event_handler(attribute: str) -> bool:
    """Takes a attribute name and returns true if
    it starts with `on` and its length is `5` or more.
    """
    return attribute.startswith("on") and len(attribute) >= 5
