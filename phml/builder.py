from __future__ import annotations
from typing import Optional

from phml.nodes import *


def p(
    selector: Optional[str] = None,
    *args: str | list | int | All_Nodes,
):
    def __process_children(node, children: list[str | list | int | b | All_Nodes]):
        for child in children:
            if isinstance(child, str):
                node.children.append(Text(child, node))
            elif isinstance(child, int):
                node.children.append(Text(str(child), node))
            elif isinstance(child, All_Nodes):
                child.parent = node
                node.children.append(child)
            elif isinstance(child, list):
                for c in child:
                    if isinstance(c, str):
                        node.children.append(Text(c, node))
                    elif isinstance(c, int):
                        node.children.append(Text(str(c), node))
                    elif isinstance(c, All_Nodes):
                        c.parent = node
                        node.children.append(c)
                    else:
                        raise TypeError(f"Unkown type <{type(c).__name__}> in {child}: {c}")

    if isinstance(selector, str) and selector.startswith("<!--") and selector.endswith("-->"):
        return Comment(selector.lstrip("<!--").rstrip("-->"))
    if not isinstance(selector, str) or len(selector.split(" ")) > 1:
        args = [selector, *args]
        selector = None

    children = [child for child in args if isinstance(child, (str, list, int, All_Nodes))]
    props = [prop for prop in args if isinstance(prop, dict)]

    if selector is not None:
        node = __parse_specifiers(selector)
        if len(node) > 1:
            raise Exception("Selector can not be a complex selector")
        if not isinstance(node[0], dict) or len(node[0]["attributes"]) > 0:
            raise EncodingWarning("Selector must be of the format `tag?[#id][.classes...]`")

        node = node[0]

        node["tag"] = "div" if node["tag"] == "*" else node["tag"]

        if node["tag"].lower() == "doctype":
            return DocType()
        else:
            properties = {}
            for prop in props:
                properties.update(prop)

            if len(node["classList"]) > 0:
                properties["class"] = properties["class"] or ""
                properties["class"] += " ".join(node["classList"])
            if node["id"] is not None:
                properties["id"] = node["id"]

            children = [child for child in args if isinstance(child, (str, list, int, All_Nodes))]

            node = Element(
                node["tag"],
                properties=properties,
                startend=len(children) == 0,
            )
    else:
        node = Root()

    if len(children) > 0:
        __process_children(node, children)

    return node


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

    splitter = compile(r"([~>*+])|(([.#]?[a-zA-Z0-9_-]+)+((\[[^\[\]]+\]))*)|(\[[^\[\]]+\])+")

    el_with_attr = compile(r"([.#]?[a-zA-Z0-9_-]+)+(\[[^\[\]]+\])*")
    el_only_attr = compile(r"((\[[^\[\]]+\]))+")

    el_classid_from_attr = compile(r"([a-zA-Z0-9_#.-]+)((\[.*\])*)")
    el_from_class_from_id = compile(r"(#|\.)?([a-zA-Z0-9_-]+)")
    attr_compare_val = compile(r"\[([a-zA-Z0-9_-]+)([~|^$*]?=)?(\"[^\"]+\"|'[^']+'|[^'\"]+)?\]")

    tokens = []
    for token in splitter.finditer(specifier):

        if token in ["*", ">", "+", "~"]:
            tokens.append(token.group())
        elif el_with_attr.match(token.group()):
            element = {
                "tag": None,
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
                        element["tag"] = item.group(2)

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


if __name__ == "__main__":
    print(
        p(
            "Some Text",
            p(
                "div",
                p("h1", "Header 1"),
                p("<!-- Text Comment -->"),
                p(
                    "p",
                    p("span", "Some text"),
                ),
            ),
        ).inspect()
    )
