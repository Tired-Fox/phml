from phml.utils.travel import walk, visit_children
from phml.nodes import Root, Element
from phml import AST


def select(node: AST | Root, specifier: str) -> Element:
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
    if isinstance(node, AST):
        node = node.tree

    rules = __parse_specifiers(specifier)

    def all_nodes(node: Element, rules: list):
        result = None
        for n in walk(node):
            if n.type == "element":
                result = branch(n, rules)
                if result is not None:
                    break
        return result

    def all_children(node: Element, rules: list):
        result = None
        for n in visit_children(node):
            if n.type == "element":
                result = branch(n, rules)
                if result is not None:
                    break
        return result

    def first_sibling(node: Element, rules: list):
        if node.parent == None:
            return None

        idx = node.parent.children.index(node)
        if idx + 1 < len(node.parent.children):
            if node.parent.children[idx + 1].type == "element":
                return branch(node.parent.children[idx + 1], rules)
        return None

    def all_siblings(node: Element, rules: list):
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
        if len(rules) == 0:
            return node
        elif isinstance(rules[0], dict):
            if is_equal(rules[0], node):
                if len(rules) - 1 == 0:
                    return node
                else:
                    if isinstance(rules[1], dict):
                        return all_nodes(node, rules[1:])
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

    return all_nodes(node, rules)


def selectAll(tree: AST | Root, specifier: str) -> list[Element]:
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

    def all_nodes(node: Element, rules: list):
        results = []
        for n in walk(node):
            if n.type == "element":
                result = branch(n, rules)
                if result is not None:
                    results.extend(result)
        return results

    def all_children(node: Element, rules: list):
        results = []
        for n in visit_children(node):
            if n.type == "element":
                result = branch(n, rules)
                if result is not None:
                    results.extend(result)
        return results

    def first_sibling(node: Element, rules: list):
        if node.parent == None:
            return []

        idx = node.parent.children.index(node)
        if idx + 1 < len(node.parent.children):
            if node.parent.children[idx + 1].type == "element":
                return [*branch(node.parent.children[idx + 1], rules)]
        return []

    def all_siblings(node: Element, rules: list):
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
        if len(rules) == 0:
            return [node]
        elif isinstance(rules[0], dict):
            if is_equal(rules[0], node):
                if len(rules) - 1 == 0:
                    return [node]
                else:
                    if isinstance(rules[1], dict):
                        return all_nodes(node, rules[1:])
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
    if rule["tag"] != "*" and rule["tag"] != node.tag:
        input("failed on tag")
        return False
    if rule["id"] is not None and rule["id"] != node.properties["id"]:
        input("failed on id")
        return False
    if len(rule["classList"]) > 0:
        from re import search

        for klass in rule["classList"]:
            if "class" not in node.properties or klass not in node.properties["class"].split(" "):
                input("failed on classList")
                return False
    if len(rule["attributes"]) > 0:
        from re import search

        # ? Here is where more attr types can be added for list attributes.
        list_attributes = ["class"]
        for attr in rule["attributes"]:
            if attr["name"] in node.properties.keys():
                if attr["compare"] is not None:
                    if attr["compare"] == "=":
                        if attr["value"] != node.properties[attr["name"]]:
                            return False
                    elif attr["compare"] == "~":
                        if attr["name"] in list_attributes:
                            itemList = node.properties[attr["name"]].split(" ")
                            matches = 0
                            for item in itemList:
                                if search(attr["value"], item) is not None:
                                    matches += 1
                            if matches == 0:
                                return False
                        else:
                            if search(attr["value"], node.properties[attr["name"]]) is None:
                                return False
                    elif attr["compare"] == "|":
                        if attr["name"] in list_attributes:
                            itemList = node.properties[attr["name"]].split(" ")
                            matches = 0
                            for item in itemList:
                                if attr["value"] == node.properties[attr["name"]]:
                                    match += 1
                                elif node.properties[attr["name"]].startswith(f"{attr['value']}-"):
                                    match += 1
                            if matches == 0:
                                return False
                        elif attr["value"] != node.properties[attr["name"]]:
                            if not node.properties[attr["name"]].startswith(f"{attr['value']}-"):
                                return False
                    elif attr["compare"] == "^":
                        if attr["name"] in list_attributes:
                            itemList = node.properties[attr["name"]].split(" ")
                            matches = 0
                            for item in itemList:
                                if item.startswith(attr["value"]):
                                    matches += 1
                            if matches == 0:
                                return False
                        if not node.properties[attr["name"]].startswith(attr['value']):
                            return False
                    elif attr["compare"] == "$":
                        if attr["name"] in list_attributes:
                            itemList = node.properties[attr["name"]].split(" ")
                            matches = 0
                            for item in itemList:
                                if item.endswith(attr["value"]):
                                    matches += 1
                            if matches == 0:
                                return False
                        if not node.properties[attr["name"]].endswith(attr['value']):
                            return False
                    elif attr["compare"] == "*":
                        if attr["name"] in list_attributes:
                            itemList = node.properties[attr["name"]].split(" ")
                            matches = 0
                            for item in itemList:
                                if search(attr["value"], node.properties[attr["name"]]) is None:
                                    matches += 1
                            if matches == 0:
                                return False
                        if search(attr["value"], node.properties[attr["name"]]) is None:
                            return False
            else:
                return False
    return True

# TODO: Add better splitting
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
    
    splitter = compile(r"([~>*+])|(([.#]?[a-zA-Z0-9_-]+)+(\[[a-zA-Z0-9_-]+[~|^$*]?=?['\"]?.+?['\"]?\])?)|(\[[a-zA-Z0-9_-]+[~|^$*]?=?['\"]?.+?['\"]?\])")
    
    selector = compile(r"[~>*+]")
    el_with_attr = compile(r"([.#]?[a-zA-Z0-9_-]+)+(\[[a-zA-Z0-9_-]+[~|^$*]?=?['\"]?.+?['\"]?\])?")
    el_only_attr = compile(r"\[[a-zA-Z0-9_-]+[~|^$*]?=?['\"]?.+?['\"]?\]")

    # TODO: swap over to using full regex for splitting needed values
    el_classid_from_attr = compile(r"([a-zA-Z0-9_#.-]+)(\[[a-zA-Z0-9_-]+[~|^$*]?=?['\"]?.+?['\"]?\])?")
    el_from_class_from_id = compile(r"(#|\.)?([a-zA-Z0-9_-]+)")
    attr_compare_val = compile(r"\[([a-zA-Z0-9_-]+)([~|^$*]?)=?(\"[^\"]+\"|'[^']+'|[^'\"]+)\]")

    tokens = []
    for token in splitter.finditer(specifier):
        
        
        if token in ["*", ">", "+", "~"]:
            tokens.append(token)
        elif el_with_attr.match(token):
            element = {
                "tag": None,
                "classList": [],
                "id": None,
                "attributes": [],
            }

            
            if "[" in spec:
                specs = spec.split("[")
                for token in specs:
                    if token.strip().endswith("]"):
                        attr_token = {"name": None, "value": None, "compare": None}
                        res = match(
                            r"([a-zA-Z0-9_-]+)([~|^$*]?=)?(\"([^\"]+)\"|'([^']+)'|(?<!['\"])(.+)(?!['\"]))?",
                            token.rstrip(']'),
                        )

                        attr, compare, _, dq_value, sq_value, nq_value = res.groups()
                        if attr is not None:
                            attr_token["name"] = attr
                            if compare is not None:
                                if compare == "=":
                                    attr_token["compare"] = "="
                                elif compare == "~=":
                                    attr_token["compare"] = "~"
                                elif compare == "|=":
                                    attr_token["compare"] = "|"
                                elif compare == "^=":
                                    attr_token["compare"] = "^"
                                elif compare == "$=":
                                    attr_token["compare"] = "$"
                                elif compare == "*=":
                                    attr_token["compare"] = "*"
                            value = dq_value or sq_value or nq_value
                            if value is not None and compare is not None:
                                attr_token["value"] = value
                            element["attributes"].append(attr_token)
                    else:
                        if token.strip() != "":
                            items = []
                            for item in finditer(r"((\.|#)?([a-zA-Z0-9_-]+))", token.strip()):
                                items.append(item.groups())

                            if items[0][1] is None:
                                element["tag"] = items[0][2]
                                items = items[1:]
                            for item in items:
                                if item[1] is not None and item[1] == ".":
                                    element["classList"].append(item[2])
                                elif item[1] is not None and item[1] == "#":
                                    if element["id"] is None:
                                        element["id"] = item[2]
                                    else:
                                        raise Exception(
                                            f"There may only be one id per element specifier.\n{spec}"
                                        )
                        else:
                            element["tag"] = "*"
            else:
                items = []
                for item in finditer(r"((\.|#)?([a-zA-Z0-9_-]+))", spec.strip()):
                    items.append(item.groups())

                if items[0][1] is None:
                    element["tag"] = items[0][2]
                    items = items[1:]
                for item in items:
                    if item[1] is not None and item[1] == ".":
                        element["classList"].append(item[2])
                    elif item[1] is not None and item[1] == "#":
                        if element["id"] is None:
                            element["id"] = item[2]
                        else:
                            raise Exception(
                                f"There may only be one id per element specifier.\n{spec}"
                            )

            tokens.append(element)

    return tokens


if __name__ == "__main__":
    from phml.nodes import *

    sample_ast = AST(
        Root(
            children=[
                DocType(position=Position(Point(1, 0), Point(1, 0))),
                Element(
                    "html",
                    {"lang": "en"},
                    position=Position(Point(2, 0), Point(13, 0), 0),
                    children=[
                        Element(
                            "head",
                            {},
                            position=Position(Point(3, 4), Point(8, 4), 1),
                            children=[
                                Element(
                                    "meta",
                                    {"charset": "UTF-8"},
                                    position=Position(Point(4, 8), Point(4, 30)),
                                    startend=True,
                                ),
                                Element(
                                    "meta",
                                    {
                                        "http-equiv": "X-UA-Compatible",
                                        "content": "IE=edge",
                                    },
                                    position=Position(Point(5, 8), Point(5, 61)),
                                    startend=True,
                                ),
                                Element(
                                    "meta",
                                    {
                                        "name": "viewport",
                                        "content": "width=device-width, initial-scale=1.0",
                                    },
                                    position=Position(Point(6, 8), Point(6, 78)),
                                    startend=True,
                                ),
                                Element(
                                    "title",
                                    {},
                                    position=Position(Point(7, 8), Point(7, 23)),
                                    children=[
                                        Text(
                                            "Document",
                                            position=Position(Point(7, 15), Point(7, 23)),
                                        )
                                    ],
                                ),
                            ],
                        ),
                        Element(
                            "body",
                            {},
                            position=Position(Point(9, 4), Point(12, 4), 1),
                            children=[
                                Comment(
                                    " Text Comment ",
                                    position=Position(Point(10, 8), Point(10, 29)),
                                ),
                                Element(
                                    "h1",
                                    {},
                                    position=Position(Point(11, 8), Point(11, 24)),
                                    children=[
                                        Text(
                                            "Hello World!",
                                            position=Position(Point(11, 12), Point(11, 24)),
                                        )
                                    ],
                                ),
                                Element(
                                    "div",
                                    properties={"id": "sample"},
                                    children=[
                                        Element(
                                            "p",
                                            properties={"id": "sample-1"},
                                            children=[Text("Sample 1")],
                                        ),
                                        Element(
                                            "p",
                                            properties={"id": "sample-2"},
                                            children=[
                                                Text("Sample 2"),
                                                Element(
                                                    "div",
                                                    properties={"id": "sample-2-nested"},
                                                    children=[
                                                        Element(
                                                            "p",
                                                            properties={"style": "width:100;"},
                                                            children=[Text("Deep Nested")],
                                                        )
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ]
        )
    )

    print(
        matches(
            Element(
                "h1",
                position=Position(Point(11, 8), Point(11, 24)),
                properties={"id": "header-1", "title": "some text here", "class": "red flex shadow border"},
                children=[
                    Text(
                        "Hello World!",
                        position=Position(Point(11, 12), Point(11, 24)),
                    )
                ],
            ),
            "h1#header-1.red[title~='text he'] li ~ p [id~=sample]",
        )
    )
"h1#header-1.red[title~='text he'] li ~ p [id~=sample]"
r"([~>*+])|(([.#]?[a-zA-Z0-9_-]+)+(\[[a-zA-Z0-9_-]+[~|^$*]?=?['\"]?.+?['\"]?\])?)|(\[[a-zA-Z0-9_-]+[~|^$*]?=?['\"]?.+?['\"]?\])"