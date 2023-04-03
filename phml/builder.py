"""phml.utilities.builder

This module serves as a utility to make building elements and ast's easier.
"""

from __future__ import annotations
from typing import overload, Literal as Lit

from phml.nodes import Node, Element, Literal, LiteralType, AST, Parent

__all__ = ["p"]


def __process_children(node, children: list[str | list | int | Node]):
    for child in children:
        if isinstance(child, (str, float, int)):
            if isinstance(child, str) and child.startswith("<!--") and child.endswith("-->"):
                child = child.strip()
                node.append(Literal(LiteralType.Comment, child.lstrip("<!--").rstrip("-->")))
            else:
                node.append(Literal(LiteralType.Text, str(child)))
        elif isinstance(child, Node):
            node.append(child)
        elif isinstance(child, list):
            for nested_child in child:
                if isinstance(nested_child, (str, float, int)):
                    if isinstance(nested_child, str) and nested_child.startswith("<!--") and nested_child.endswith("-->"):
                        nested_child = nested_child.strip()
                        node.append(Literal(LiteralType.Comment, nested_child.lstrip("<!--").rstrip("-->")))
                    else:
                        node.append(Literal(LiteralType.Text, str(nested_child)))
                elif isinstance(nested_child, Node):
                    node.append(nested_child)
                else:
                    raise TypeError(
                        f"Unkown type <{type(nested_child).__name__}> in {child}:\
 {nested_child}"
                    )

@overload
def p(selector: Node|None=None, *args: str | list | dict | int | Node) -> AST:
    ...

@overload
def p(selector: str, *args: str | list | dict | int | Node) -> Element:
    ...

@overload
def p(selector: Lit["text"], *args: str) -> Literal:
    ...

@overload
def p(selector: Lit["comment"], *args: str) -> Literal:
    ...

def p(  # pylint: disable=[invalid-name,keyword-arg-before-vararg]
    selector: str | Node | None = None,
    *args: str | list | dict | int | Node | None,
) -> Node|AST|Parent:
    """Generic factory for creating phml nodes."""

    # Get all children | non dict objects
    children = [child for child in args if isinstance(child, (str, list, int, Node))]

    # Get all properties | dict objects
    props = {key: value for prop in args if isinstance(prop, dict) for key, value in prop.items()}

    if selector is not None:
        # Is a comment
        # if isinstance(selector, str) and selector.startswith("<!--"):
        #     return Literal(LiteralType.Comment, selector.replace("<!--", "").replace("-->", ""))
        # Is a text node
        # if (
        #     isinstance(selector, str)
        #     and (len(selector.split(" ")) > 1 or len(selector.split("\n")) > 1)
        #     and len(args) == 0
        # ):
        #     return Literal(LiteralType.Text, selector)
        if not isinstance(selector, str):
            args = (selector, *args)
            selector = None

            children = [child for child in args if isinstance(child, (str, list, int, Node))]
            return parse_root(children)
        return parse_node(selector, props, children)

    return parse_root(children)


def parse_root(children: list):
    """From the given information return a built root node."""

    node = AST()
    __process_children(node, children)
    return node


def parse_node(selector: str, props: dict, children: list):
    """From the provided selector, props, and children build an element node."""
    from phml.utilities import parse_specifiers  # pylint: disable=import-outside-toplevel

    node = parse_specifiers(selector)
    if not isinstance(node[0], dict) or len(node[0]["attributes"]) > 0:
        raise TypeError("Selector must be of the format `tag?[#id]?[.classes...]?`")

    node = node[0]

    node["tag"] = "div" if node["tag"] == "*" else node["tag"]

    if node["tag"].lower() == "doctype":
        return Element("doctype", {"html": True})

    if node["tag"].lower().strip() == "text":
        return Literal(
            LiteralType.Text,
            " ".join([str(child) for child in children if isinstance(child, (str, int, float))])
        )
    if node["tag"].lower().strip() == "comment":
        return Literal(
            LiteralType.Comment,
            " ".join([str(child) for child in children if isinstance(child, (str, int, float))])
        )

    properties = {**props}

    if len(node["classList"]) > 0:
        properties["class"] = "" if "class" not in properties else properties["class"]
        properties["class"] += " ".join(node["classList"])
    if node["id"] is not None:
        properties["id"] = node["id"]

    element = Element(
        node["tag"],
        attributes=properties,
        children=[] if len(children) > 0 else None,
    )

    __process_children(element, children)
    return element

