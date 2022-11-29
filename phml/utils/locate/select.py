"""utils.select

A collection of utilities around querying for specific
types of data.
"""

from typing import Callable

from phml.utils.travel import walk, visit_children
from phml.nodes import Root, Element, AST

__all__ = ["query", "queryAll", "matches"]


def query(tree: AST | Root | Element, specifier: str) -> Element:
    """Same as javascripts querySelector. `#` indicates an id and `.`
    indicates a class. If they are used alone they match anything.
    Any tag can be used by itself or with `#` and/or `.`. You may use
    any number of class specifiers, but may only use one id specifier per
    tag name. Complex specifiers are accepted are allowed meaning you can
    have space seperated specifiers indicating nesting or a parent child
    relationship.

    Examles:
    * `.some-example` matches the first element with the class `some-example`
    * `#some-example` matches the first element with the id `some-example`
    * `li` matches the first `li` element
    * `li.red` matches the first `li` with the class `red`
    * `li#red` matches the first `li` with the id `red`
    * `input[type="checkbox"]` matches the first `input` with the attribute `type="checkbox"`
    * `div.form-control input[type="checkbox"]` matches the first `input` with the
    attribute `type="checked"` that has a parent `div` with the class `form-control`.

    Return:
        Element | None: The first element matching the specifier or None if no element was
        found.
    """
    if isinstance(tree, AST):
        tree = tree.tree

    rules = __parse_specifiers(specifier)

    def all_nodes(node: Element, rules: list, include_self: bool = True):
        """Get all nodes starting with the current node."""

        result = None
        for n in walk(node):
            if n.type == "element" and (include_self or n != node):
                result = branch(n, rules)
                if result is not None:
                    break
        return result

    def all_children(node: Element, rules: list):
        """Get all children of the curret node."""
        result = None
        for n in visit_children(node):
            if n.type == "element":
                result = branch(n, rules)
                if result is not None:
                    break
        return result

    def first_sibling(node: Element, rules: list):
        """Get the first sibling following the node."""
        if node.parent == None:
            return None

        idx = node.parent.children.index(node)
        if idx + 1 < len(node.parent.children):
            if node.parent.children[idx + 1].type == "element":
                return branch(node.parent.children[idx + 1], rules)
        return None

    def all_siblings(node: Element, rules: list):
        """Get all siblings after the current node."""
        if node.parent == None:
            return None

        result = None
        idx = node.parent.children.index(node)
        if idx + 1 < len(node.parent.children):
            for n in range(idx + 1, len(node.parent.children)):
                if node.parent.children[n].type == "element":
                    result = branch(node.parent.children[n], rules)
                    if result is not None:
                        break
        return result

    def branch(node: Element, rules: list):
        """Based on the current rule, recursively check the nodes.
        If on the last rule then return the current valid node.
        """

        if len(rules) == 0:
            return node
        elif isinstance(rules[0], dict):
            if is_equal(rules[0], node):
                if len(rules) - 1 == 0:
                    return node
                else:
                    if isinstance(rules[1], dict):
                        return all_nodes(node, rules[1:])
                    elif rules[1] == "*":
                        return all_nodes(node, rules[2:], False)
                    else:
                        return branch(node, rules[1:])
            else:
                return None
        elif rules[0] == "*":
            return all_nodes(node, rules[1:])
        elif rules[0] == ">":
            return all_children(node, rules[1:])
        elif rules[0] == "+":
            return first_sibling(node, rules[1:])
        elif rules[0] == "~":
            return all_siblings(node, rules[1:])

    return all_nodes(tree, rules)


def queryAll(tree: AST | Root | Element, specifier: str) -> list[Element]:
    """Same as javascripts querySelectorAll. `#` indicates an id and `.`
    indicates a class. If they are used alone they match anything.
    Any tag can be used by itself or with `#` and/or `.`. You may use
    any number of class specifiers, but may only use one id specifier per
    tag name. Complex specifiers are accepted are allowed meaning you can
    have space seperated specifiers indicating nesting or a parent child
    relationship.

    Examles:
    * `.some-example` matches the first element with the class `some-example`
    * `#some-example` matches the first element with the id `some-example`
    * `li` matches the first `li` element
    * `li.red` matches the first `li` with the class `red`
    * `li#red` matches the first `li` with the id `red`
    * `input[type="checkbox"]` matches the first `input` with the attribute `type="checkbox"`
    * `div.form-control input[type="checkbox"]` matches the first `input` with the
    attribute `type="checked"` that has a parent `div` with the class `form-control`.

    Return:
        list[Element] | None: The all elements matching the specifier or and empty list if no elements were
        found.
    """
    if isinstance(tree, AST):
        tree = tree.tree

    rules = __parse_specifiers(specifier)

    def all_nodes(node: Element, rules: list, include_self: bool = True):
        """Get all nodes starting with the current node."""
        results = []
        for n in walk(node):
            if n.type == "element" and (include_self or n != node):
                result = branch(n, rules)
                if result is not None:
                    results.extend(result)
        return results

    def all_children(node: Element, rules: list):
        """Get all children of the curret node."""
        results = []
        for n in visit_children(node):
            if n.type == "element":
                result = branch(n, rules)
                if result is not None:
                    results.extend(result)
        return results

    def first_sibling(node: Element, rules: list):
        """Get the first sibling following the node."""
        if node.parent == None:
            return []

        idx = node.parent.children.index(node)
        if idx + 1 < len(node.parent.children):
            if node.parent.children[idx + 1].type == "element":
                return [*branch(node.parent.children[idx + 1], rules)]
        return []

    def all_siblings(node: Element, rules: list):
        """Get all siblings after the current node."""
        if node.parent == None:
            return []

        results = []
        idx = node.parent.children.index(node)
        if idx + 1 < len(node.parent.children):
            for n in range(idx + 1, len(node.parent.children)):
                if node.parent.children[n].type == "element":
                    result = branch(node.parent.children[n], rules)
                    if result is not None:
                        results.extend(result)
        return results

    def branch(node: Element, rules: list):
        """Based on the current rule, recursively check the nodes.
        If on the last rule then return the current valid node.
        """
        if len(rules) == 0:
            return [node]
        elif isinstance(rules[0], dict):
            if is_equal(rules[0], node):
                if len(rules) - 1 == 0:
                    return [node]
                else:
                    if isinstance(rules[1], dict):
                        return all_nodes(node, rules[1:])
                    elif rules[1] == "*":
                        return all_nodes(node, rules[2:], False)
                    else:
                        return branch(node, rules[1:])
            else:
                return None
        elif rules[0] == "*":
            return all_nodes(node, rules[1:])
        elif rules[0] == ">":
            return all_children(node, rules[1:])
        elif rules[0] == "+":
            return first_sibling(node, rules[1:])
        elif rules[0] == "~":
            return all_siblings(node, rules[1:])

    return all_nodes(tree, rules)


def matches(node: Element, specifier: str) -> bool:
    """Works the same as the Javascript matches. `#` indicates an id and `.`
    indicates a class. If they are used alone they match anything.
    Any tag can be used by itself or with `#` and/or `.`. You may use
    any number of class specifiers, but may only use one id specifier per
    tag name. Complex specifiers are not supported. Everything in the specifier
    must relate to one element/tag.

    Examles:
    * `.some-example` matches the first element with the class `some-example`
    * `#some-example` matches the first element with the id `some-example`
    * `li` matches the first `li` element
    * `li.red` matches the first `li` with the class `red`
    * `li#red` matches the first `li` with the id `red`
    * `input[type="checkbox"]` matches the first `input` with the attribute `type="checkbox"`
    """

    rules = __parse_specifiers(specifier)

    if len(rules) > 1:
        raise Exception(f"Complex specifier detected and is not allowed.\n{specifier}")
    if not isinstance(rules[0], dict):
        raise Exception(
            "Specifier must only include tag name, classes, id, and or attribute specfiers.\n\
Example: `li.red#sample[class^='form-'][title~='sample']`"
        )

    return is_equal(rules[0], node)


def is_equal(rule: dict, node: Element) -> bool:
    """Checks if a rule is valid on a node.
    A rule is a dictionary of possible values and each value must
    be valid on the node.

    A rule may have a tag, id, classList, and attribute list:
    * If the `tag` is provided, the nodes `tag` must match the rules `tag`
    * If the `id` is provided, the nodes `id` must match the rules `id`
    * If the `classList` is not empty, each class in the `classList` must exist in the nodes
    class attribute
    * If the `attribute` list is not empty, each attribute in the attribute list with be compared
    against the nodes attributes given the `attribute` lists comparators. Below is the list of
    possible comparisons.
        1. Exists: `[checked]` yields any element that has the attribute `checked` no matter it's
        value.
        2. Equals: `[checked='no']` yields any element with `checked='no'`
        3. Contains: `[class~=sample]` or `[class*=sample]` yields any element with a class
        containing `sample`
        4. Equal to or startswith value-: `[class|=sample]` yields elements that either have
        a class that equals `sample` or or a class that starts with `sample-`
        5. Starts with: `[class^=sample]` yields elements with a class that starts with `sample`
        6. Ends with: `[class$="sample"]` yields elements with a class that ends wtih `sample`

    Args:
        rule (dict): The rule to apply to the node.
        node (Element): The node the validate.

    Returns:
        bool: Whether the node passes all the rules in the dictionary.
    """

    # Validate tag
    if rule["tag"] != "*" and rule["tag"] != node.tag:
        return False

    # Validate id
    if rule["id"] is not None and rule["id"] != node.properties["id"]:
        return False

    # Validate class list
    if len(rule["classList"]) > 0:
        for klass in rule["classList"]:
            if "class" not in node.properties or klass not in node.properties["class"].split(" "):
                return False

    # Validate all attributes
    if len(rule["attributes"]) > 0:
        for attr in rule["attributes"]:
            if attr["name"] in node.properties.keys():
                if attr["compare"] is not None:
                    if attr["compare"] == "=":
                        if attr["value"] != node.properties[attr["name"]]:
                            return False
                    elif attr["compare"] == "|":

                        if not is_valid_attr(
                            attr=node.properties[attr["name"]],
                            sub=attr["value"],
                            validator=lambda x, y: x == y or x.startswith(f"{y}-"),
                        ):
                            return False
                    elif attr["compare"] == "^":
                        if not is_valid_attr(
                            attr=node.properties[attr["name"]],
                            sub=attr["value"],
                            validator=lambda x, y: x.startswith(y),
                        ):
                            return False
                    elif attr["compare"] == "$":
                        if not is_valid_attr(
                            attr=node.properties[attr["name"]],
                            sub=attr["value"],
                            validator=lambda x, y: x.endswith(y),
                        ):
                            return False
                    elif attr["compare"] in ["*", "~"]:
                        if not is_valid_attr(
                            attr=node.properties[attr["name"]],
                            sub=attr["value"],
                            validator=lambda x, y: y in x,
                        ):
                            return False
                else:
                    return True
            else:
                return False
    return True


def is_valid_attr(attr: str, sub: str, validator: Callable) -> bool:
    """Validate an attribute value with a given string and a validator callable.
    If classlist, create list with attribute value seperated on spaces. Otherwise,
    the list will only have the attribute value. For each item in the list, check
    against validator, if valid add to count.

    Returns:
        True if the valid count is greater than 0.
    """
    list_attributes = ["class"]

    compare_values = [attr]
    if attr["name"] in list_attributes:
        compare_values = attr.split(" ")

    if len([item for item in compare_values if validator(item, sub)]) == 0:
        return False


def __parse_specifiers(specifier: str) -> dict:
    """
    Rules:
    * `*` = any element
    * `>` = Everything with certain parent child relationship
    * `+` = first sibling
    * `~` = All after
    * `.` = class
    * `#` = id
    * `[attribute]` = all elements with attribute
    * `[attribute=value]` = all elements with attribute=value
    * `[attribute~=value]` = all elements with attribute containing value
    * `[attribute|=value]` = all elements with attribute=value or attribute starting with value-
    * `node[attribute^=value]` = all elements with attribute starting with value
    * `node[attribute$=value]` = all elements with attribute ending with value
    * `node[attribute*=value]` = all elements with attribute containing value

    """
    from re import compile

    splitter = compile(r"([~>\*+])|(([.#]?[a-zA-Z0-9_-]+)+((\[[^\[\]]+\]))*)|(\[[^\[\]]+\])+")

    el_with_attr = compile(r"([.#]?[a-zA-Z0-9_-]+)+(\[[^\[\]]+\])*")
    el_only_attr = compile(r"((\[[^\[\]]+\]))+")

    el_classid_from_attr = compile(r"([a-zA-Z0-9_#.-]+)((\[.*\])*)")
    el_from_class_from_id = compile(r"(#|\.)?([a-zA-Z0-9_-]+)")
    attr_compare_val = compile(r"\[([a-zA-Z0-9_-]+)([~|^$*]?=)?(\"[^\"]+\"|'[^']+'|[^'\"]+)?\]")

    tokens = []
    for token in splitter.finditer(specifier):
        if token.group() in ["*", ">", "+", "~"]:
            tokens.append(token.group())
        elif el_with_attr.match(token.group()):
            element = {
                "tag": "*",
                "classList": [],
                "id": None,
                "attributes": [],
            }

            res = el_classid_from_attr.match(token.group())

            el_class_id, attrs = res.group(1), res.group(2)

            if attrs not in ["", None]:
                for attr in attr_compare_val.finditer(attrs):
                    name, compare, value = attr.groups()
                    if value is not None:
                        value = value.lstrip("'\"").rstrip("'\"")
                    element["attributes"].append(
                        {
                            "name": name,
                            "compare": compare,
                            "value": value,
                        }
                    )

            if el_class_id not in ["", None]:
                for item in el_from_class_from_id.finditer(el_class_id):
                    if item.group(1) == ".":
                        if item.group(2) not in element["classList"]:
                            element["classList"].append(item.group(2))
                    elif item.group(1) == "#":
                        if element["id"] is None:
                            element["id"] = item.group(2)
                        else:
                            raise Exception(
                                f"There may only be one id per element specifier.\n{token.group()}"
                            )
                    else:
                        element["tag"] = item.group(2) or "*"

            tokens.append(element)
        elif el_only_attr.match(token.group()):
            element = {
                "tag": None,
                "classList": [],
                "id": None,
                "attributes": [],
            }

            element["tag"] = "*"

            if token.group() not in ["", None]:
                for attr in attr_compare_val.finditer(token.group()):
                    name, compare, value = attr.groups()
                    if value is not None:
                        value = value.lstrip("'\"").rstrip("'\"")
                    element["attributes"].append(
                        {
                            "name": name,
                            "compare": compare,
                            "value": value,
                        }
                    )

            tokens.append(element)

    return tokens
