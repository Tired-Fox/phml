"""utilities.select

A collection of utilities around querying for specific
types of data.
"""

import re
from typing import Callable

from phml.nodes import Element, Node, Parent
from phml.utilities.travel.travel import walk

__all__ = ["query", "query_all", "matches", "parse_specifiers"]


def query(tree: Parent, specifier: str) -> Element | None:
    """Same as javascripts querySelector. `#` indicates an id and `.`
    indicates a class. If they are used alone they match anything.
    Any tag can be used by itself or with `#` and/or `.`. You may use
    any number of class specifiers, but may only use one id specifier per
    tag name. Complex specifiers are accepted are allowed meaning you can
    have space seperated specifiers indicating nesting or a parent child
    relationship.

    Rules:
    * `*` = any element
    * `>` = direct child of the current element
    * `+` = first sibling
    * `~` = elements after the current element
    * `.` = class
    * `#` = id
    * `[attribute]` = elements with attribute
    * `[attribute=value]` = elements with attribute=value
    * `[attribute~=value]` = elements with attribute containing value
    * `[attribute|=value]` = elements with attribute=value or attribute starting with value-
    * `[attribute^=value]` = elements with an attribute starting with value
    * `[attribute$=value]` = elements with an attribute ending with value
    * `[attribute*=value]` = elements with an attribute containing value

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

    def all_nodes(current: Parent, rules: list, include_self: bool = True):
        """Get all nodes starting with the current node."""

        result = None
        for node in walk(current):
            if isinstance(node, Element) and (include_self or node != current):
                result = branch(node, rules)
                if result is not None:
                    break
        return result

    def all_children(current: Parent, rules: list):
        """Get all children of the curret node."""
        result = None
        for node in current:
            if isinstance(node, Element):
                result = branch(node, rules)
                if result is not None:
                    break
        return result

    def first_sibling(node: Parent, rules: list):
        """Get the first sibling following the node."""
        if node.parent is None:
            return None

        idx = node.parent.index(node)
        if idx + 1 < len(node.parent) and isinstance(node.parent[idx + 1], Element):
            return branch(node.parent[idx + 1], rules)
        return None

    def all_siblings(current: Parent, rules: list):
        """Get all siblings after the current node."""
        if current.parent is None:
            return None

        result = None
        idx = current.parent.index(current)
        if idx + 1 < len(current.parent):
            for node in range(idx + 1, len(current.parent)):
                if isinstance(current.parent[node], Element):
                    result = branch(current.parent[node], rules)
                    if result is not None:
                        break
        return result

    def process_dict(rules: list, node: Element):
        if is_equal(rules[0], node):
            if len(rules) - 1 == 0:
                return node

            if isinstance(rules[1], dict) or rules[1] == "*":
                return (
                    all_nodes(node, rules[1:], False)
                    if isinstance(rules[1], dict)
                    else all_nodes(node, rules[2:], False)
                )

            return branch(node, rules[1:])
        return None

    def branch(node: Node, rules: list):  # pylint: disable=too-many-return-statements
        """Based on the current rule, recursively check the nodes.
        If on the last rule then return the current valid node.
        """

        if isinstance(node, Parent):
            if len(rules) == 0:
                return node

            if isinstance(rules[0], dict) and isinstance(node, Element):
                return process_dict(rules, node)

            if rules[0] == "*":
                return all_nodes(node, rules[1:])

            if rules[0] == ">":
                return all_children(node, rules[1:])

            if rules[0] == "+":
                return first_sibling(node, rules[1:])

            if rules[0] == "~":
                return all_siblings(node, rules[1:])

    rules = parse_specifiers(specifier)
    return all_nodes(tree, rules)


def query_all(tree: Parent, specifier: str) -> list[Element]:
    """Same as javascripts querySelectorAll. `#` indicates an id and `.`
    indicates a class. If they are used alone they match anything.
    Any tag can be used by itself or with `#` and/or `.`. You may use
    any number of class specifiers, but may only use one id specifier per
    tag name. Complex specifiers are accepted are allowed meaning you can
    have space seperated specifiers indicating nesting or a parent child
    relationship.

    Rules:
    * `*` = any element
    * `>` = direct child of the current element
    * `+` = first sibling
    * `~` = elements after the current element
    * `.` = class
    * `#` = id
    * `[attribute]` = elements with attribute
    * `[attribute=value]` = elements with attribute=value
    * `[attribute~=value]` = elements with attribute containing value
    * `[attribute|=value]` = elements with attribute=value or attribute starting with value-
    * `[attribute^=value]` = elements with an attribute starting with value
    * `[attribute$=value]` = elements with an attribute ending with value
    * `[attribute*=value]` = elements with an attribute containing value

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
        list[Element] | None: The all elements matching the specifier or and empty list if no
        elements were found.
    """

    def all_nodes(current: Parent, rules: list, include_self: bool = True):
        """Get all nodes starting with the current node."""
        results = []
        for node in walk(current):
            if isinstance(node, Element) and (include_self or node != current):
                results.extend(branch(node, rules) or [])
        return results

    def all_children(current: Parent, rules: list):
        """Get all children of the curret node."""
        results = []
        for node in current:
            if isinstance(node, Element):
                results.extend(branch(node, rules) or [])
        return results

    def first_sibling(node: Parent, rules: list):
        """Get the first sibling following the node."""
        if node.parent is None:
            return []

        idx = node.parent.index(node)
        if idx + 1 < len(node.parent) and node.parent[idx + 1].type == "element":
            result = branch(node.parent[idx + 1], rules)
            return result
        return []

    def all_siblings(current: Parent, rules: list):
        """Get all siblings after the current node."""
        if current.parent is None:
            return []

        results = []
        idx = current.parent.index(current)
        if idx + 1 < len(current.parent):
            for node in range(idx + 1, len(current.parent)):
                if current.parent[node].type == "element":
                    results.extend(branch(current.parent[node], rules) or [])
        return results

    def process_dict(rules: list, node: Element):
        if is_equal(rules[0], node):
            if len(rules) - 1 == 0:
                return [node]

            if isinstance(rules[1], dict) or rules[1] == "*":
                return (
                    all_nodes(node, rules[1:])
                    if isinstance(rules[1], dict)
                    else all_nodes(node, rules[2:], False)
                )

            return branch(node, rules[1:])
        return []

    def branch(node: Node, rules: list):  # pylint: disable=too-many-return-statements
        """Based on the current rule, recursively check the nodes.
        If on the last rule then return the current valid node.
        """

        if isinstance(node, Parent):
            if len(rules) == 0:
                return [node]

            if isinstance(rules[0], dict) and isinstance(node, Element):
                return process_dict(rules, node)

            if rules[0] == "*":
                return all_nodes(node, rules[1:])

            if rules[0] == ">":
                return all_children(node, rules[1:])

            if rules[0] == "+":
                return first_sibling(node, rules[1:])

            if rules[0] == "~":
                return all_siblings(node, rules[1:])

    rules = parse_specifiers(specifier)
    return all_nodes(tree, rules)
    # return [result[i] for i in range(len(result)) if i == result.index(result[i])]


def matches(node: Element, specifier: str) -> bool:
    """Works the same as the Javascript matches. `#` indicates an id and `.`
    indicates a class. If they are used alone they match anything.
    Any tag can be used by itself or with `#` and/or `.`. You may use
    any number of class specifiers, but may only use one id specifier per
    tag name. Complex specifiers are not supported. Everything in the specifier
    must relate to one element/tag.

    Rules:
    * `.` = class
    * `#` = id
    * `[attribute]` = elements with attribute
    * `[attribute=value]` = elements with attribute=value
    * `[attribute~=value]` = elements with attribute containing value
    * `[attribute|=value]` = elements with attribute=value or attribute starting with value-
    * `[attribute^=value]` = elements with an attribute starting with value
    * `[attribute$=value]` = elements with an attribute ending with value
    * `[attribute*=value]` = elements with an attribute containing value

    Examles:
    * `.some-example` matches the element with the class `some-example`
    * `#some-example` matches the element with the id `some-example`
    * `li` matches an `li` element
    * `li.red` matches the an `li` with the class `red`
    * `li#red` matches the an `li` with the id `red`
    * `input[type="checkbox"]` matches the `input` element with the attribute `type="checkbox"`
    """

    rules = parse_specifiers(specifier)

    if len(rules) > 1:
        raise Exception(f"Complex specifier detected and is not allowed.\n{specifier}")
    if not isinstance(rules[0], dict):
        raise Exception(
            "Specifier must only include tag name, classes, id, and or attribute specfiers.\n\
Example: `li.red#sample[class^='form-'][title~='sample']`",
        )

    return is_equal(rules[0], node)


def is_equal(rule: dict, node: Node) -> bool:
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
    if rule["id"] is not None and ("id" not in node or rule["id"] != node["id"]):
        return False

    # Validate class list
    if len(rule["classList"]) > 0:
        for klass in rule["classList"]:
            if "class" not in node or klass not in str(node["class"]).split(" "):
                return False

    # Validate all attributes
    if len(rule["attributes"]) > 0:
        return all(
            attr["name"] in node.attributes and __validate_attr(attr, node)
            for attr in rule["attributes"]
        )

    return True


def compare_equal(attr: str, c_value: str) -> bool:
    return attr == c_value


def compare_equal_or_start_with_value_dash(attr: str, c_value: str) -> bool:
    return attr == c_value or attr.startswith(f"{c_value}-")


def compare_startswith(attr: str, c_value: str) -> bool:
    return attr.startswith(c_value)


def compare_endswith(attr: str, c_value: str) -> bool:
    return attr.endswith(c_value)


def compare_contains(attr: str, c_value: str) -> bool:
    return c_value in attr


def compare_exists(attr: str, _) -> bool:
    return attr == "true"


def __validate_attr(attr: dict, node: Element):
    attribute = node[attr["name"]]
    if isinstance(attribute, bool):
        attribute = str(node[attr["name"]]).lower()

    if attr["compare"] == "=":
        return is_valid_attr(
            attr=attribute,
            sub=attr["value"],
            name=attr["name"],
            validator=compare_equal,
        )

    if attr["compare"] == "|=":
        return is_valid_attr(
            attr=attribute,
            sub=attr["value"],
            name=attr["name"],
            validator=compare_equal_or_start_with_value_dash,
        )

    if attr["compare"] == "^=":
        return is_valid_attr(
            attr=attribute,
            sub=attr["value"],
            name=attr["name"],
            validator=compare_startswith,
        )

    if attr["compare"] == "$=":
        return is_valid_attr(
            attr=attribute,
            sub=attr["value"],
            name=attr["name"],
            validator=compare_endswith,
        )

    if attr["compare"] in ["*=", "~="]:
        return is_valid_attr(
            attr=attribute,
            sub=attr["value"],
            name=attr["name"],
            validator=compare_contains,
        )

    if attr["compare"] == "" and attr["value"] == "":
        return is_valid_attr(
            attr=attribute,
            sub=attr["value"],
            name=attr["name"],
            validator=compare_exists,
        )


def is_valid_attr(attr: str, sub: str, name: str, validator: Callable) -> bool:
    """Validate an attribute value with a given string and a validator callable.
    If classlist, create list with attribute value seperated on spaces. Otherwise,
    the list will only have the attribute value. For each item in the list, check
    against validator, if valid add to count.

    Returns:
        True if the valid count is greater than 0.
    """
    list_attributes = ["class"]

    compare_values = [attr]
    if name in list_attributes:
        compare_values = attr.split(" ")

    return bool(len([item for item in compare_values if validator(item, sub)]) > 0)


def __parse_el_with_attribute(
    tag: str | None, context: str | None, attributes: str | None
) -> dict:
    el_from_class_from_id = re.compile(r"(#|\.)([\w\-]+)")

    attr_compare_val = re.compile(
        r"\[\s*([\w\-:@]+)\s*([\~\|\^\$\*]?=)?\s*(\"[^\"\[\]=]*\"|\'[^\'\[\]=]*\'|[^\s\[\]=\"']+)?\s*\]"
    )
    re.compile(r"\[\s*([\w\-:@]+)\]")

    element = {
        "tag": tag or "*",
        "classList": [],
        "id": None,
        "attributes": [],
    }

    if attributes is not None:
        for attr in attr_compare_val.findall(attributes):
            name, compare, value = attr
            if value is not None:
                value = value.lstrip("'\"").rstrip("'\"")
            element["attributes"].append(
                {
                    "name": name,
                    "compare": compare,
                    "value": value,
                },
            )

    if context is not None:
        for part in el_from_class_from_id.finditer(context):
            if part.group(1) == ".":
                if part.group(2) not in element["classList"]:
                    element["classList"].append(part.group(2))
            elif part.group(1) == "#":
                if element["id"] is None:
                    element["id"] = part.group(2)
                else:
                    raise Exception(
                        f"There may only be one id per element specifier. '{(tag or '') + (context or '')}{attributes or ''}'",
                    )
    return element


def __parse_attr_only_element(token: str) -> dict:
    attr_compare_val = re.compile(
        r"\[([a-zA-Z0-9_:\-]+)([~|^$*]?=)?(\"[^\"]+\"|'[^']+'|[^'\"]+)?\]"
    )

    element = {
        "tag": None,
        "classList": [],
        "id": None,
        "attributes": [],
    }

    element["tag"] = "*"

    if token not in ["", None]:
        for attr in attr_compare_val.finditer(token):
            name, compare, value = attr.groups()
            if value is not None:
                value = value.lstrip("'\"").rstrip("'\"")
            element["attributes"].append(
                {
                    "name": name,
                    "compare": compare,
                    "value": value,
                },
            )

    return element


def parse_specifiers(specifier: str) -> list:
    """
    Rules:
    * `*` = any element
    * `>` = direct child of the current element
    * `+` = first sibling
    * `~` = elements after the current element
    * `.` = class
    * `#` = id
    * `[attribute]` = elements with attribute
    * `[attribute=value]` = elements with attribute=value
    * `[attribute~=value]` = elements with attribute containing value
    * `[attribute|=value]` = elements with attribute=value or attribute starting with value-
    * `[attribute^=value]` = elements with an attribute starting with value
    * `[attribute$=value]` = elements with an attribute ending with value
    * `[attribute*=value]` = elements with an attribute containing value
    """
    splitter = re.compile(
        r"([~>\*+])|((?:\[[^\[\]]+\])+)|([^.#\[\]\s]+)?((?:(?:\.|#)[^.#\[\]\s]+)+)?((?:\[[^\[\]]+\])+)?"
    )

    tokens = []
    for token in splitter.finditer(specifier):
        (
            sibling,
            just_attributes,
            tag,
            context,
            attributes,
        ) = token.groups()
        if sibling in ["*", ">", "+", "~"]:
            tokens.append(sibling)
        elif tag is not None or context is not None or attributes is not None:
            tokens.append(__parse_el_with_attribute(tag, context, attributes))
        elif just_attributes is not None:
            tokens.append(__parse_attr_only_element(just_attributes))
    return tokens
