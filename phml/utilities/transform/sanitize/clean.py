from __future__ import annotations
from re import match

from phml.nodes import Element, Parent, Node

from .schema import Schema

def recurse_check_tag(node: Parent, schema: Schema):
    from phml.utilities import is_element

    for child in list(node):
        if isinstance(child, Element) and not is_element(child, schema.tag_names):
            node.remove(child)
        elif isinstance(child, Parent):
            recurse_check_tag(child, schema)

def recurse_check_ancestor(node: Parent, schema: Schema):
    for child in list(node):
        if (
            isinstance(child, Element)
            and child.tag in schema.ancestors
            and (
                not isinstance(child.parent, Element)
                or child.parent.tag not in schema.ancestors[child.tag]
            )
        ):
            node.remove(child)
        elif isinstance(child, Element):
            recurse_check_ancestor(child, schema)

def build_remove_attr_list(
    properties: dict,
    attributes: dict[str, tuple[str | bool, ...]],
    valid_attributes: list,
    schema: Schema
):
    """Build the list of attributes to remove from a dict of attributes."""
    result = []
    for attribute in properties:
        if attribute not in valid_attributes:
            result.append(attribute)
        elif attribute in attributes:
            if (
                isinstance(properties[attribute], str)
                and attribute in schema.protocols
                and not check_protocols(
                    properties[attribute], schema.protocols[attribute],
                    schema
                )
            ):
                result.append(attribute)
            elif properties[attribute] != attributes[attribute]:
                result.append(attribute)
        elif (
            isinstance(properties[attribute], str)
            and attribute in schema.protocols
            and not check_protocols(
                properties[attribute], schema.protocols[attribute],
                schema
            )
        ):
            result.append(attribute)
    return result

def recurse_check_attributes(node: Node, schema: Schema):
    if isinstance(node, Element):
        if node.tag in schema.attributes:
            pop_attrs = build_remove_attr_list(
                node.attributes,
                {
                    str(attr[0]): attr[1:]
                    for attr in (
                        schema.attributes[node.tag]
                        + schema.attributes.get("*", [])
                    )
                    if isinstance(attr, tuple)
                },
                [
                    attr if isinstance(attr, str) else attr[0]
                    for attr in (
                        schema.attributes[node.tag]
                        + schema.attributes.get("*", [])
                    )
                ],
                schema,
            )

            for attribute in pop_attrs:
                node.pop(attribute, None)

        for child in node:
            recurse_check_attributes(child, schema)

def recurse_check_required(node: Parent, schema: Schema):
    for child in node:
        if isinstance(child, Element) and child.tag in schema.required:
            for attr, value in schema.required[child.tag].items():
                if attr not in child.attributes:
                    child[attr] = value
                elif isinstance(value, bool):
                    child[attr] = str(value).lower()
                elif isinstance(value, str) and child[attr] != value:
                    child[attr] = value
        elif isinstance(child, Element):
            recurse_check_required(child, schema)

def check_protocols(value: str, protocols: list[str], schema: Schema):
    return match(f"{'|'.join(protocols)}:.*", value) is not None

def recurse_strip(node, schema: Schema):
    from phml.utilities import is_element

    for child in list(node):
        if isinstance(child, Element) and is_element(child, schema.strip):
            node.remove(child)
        elif isinstance(child, Parent):
            recurse_strip(child, schema)

def sanatize(tree: Parent, schema: Schema = Schema()):
    """Sanatize elements and attributes in the phml tree. Should be used when using
    data from an unkown source. It should be used with an AST that has already been
    compiled to html to no unkown values are unchecked.

    By default the sanatization schema uses the github schema and follows the hast
    sanatize utility.

    * [github schema](https://github.com/syntax-tree/hast-util-sanitize/blob/main/lib/schema.js)
    * [hast sanatize](https://github.com/syntax-tree/hast-util-sanitize)

    Note:
        This utility will edit the tree in place.

    Args:
        tree (Parent): The root of the tree that will be sanatized.
        schema (Schema, optional): User defined schema. Defaults to github schema.
    """

    from phml.utilities import (  # pylint: disable=import-outside-toplevel
        remove_nodes,
    )

    for strip in schema.strip:
        remove_nodes(tree, ["element", {"tag": strip}])


    recurse_check_tag(tree, schema)
    recurse_strip(tree, schema)
    recurse_check_ancestor(tree, schema)
    recurse_check_attributes(tree, schema)
    recurse_check_required(tree, schema)
