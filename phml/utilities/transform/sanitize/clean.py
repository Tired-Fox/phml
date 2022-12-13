from re import match
from typing import Optional

from phml.core.nodes import AST, Element, Root

from .schema import Schema


def sanatize(tree: AST | Root | Element, schema: Optional[Schema] = Schema()):
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
        tree (AST | Root | Element): The root of the tree that will be sanatized.
        schema (Optional[Schema], optional): User defined schema. Defaults to github schema.
    """

    from phml import check, is_element, remove_nodes  # pylint: disable=import-outside-toplevel

    if isinstance(tree, AST):
        src = tree.tree
    else:
        src = tree

    for strip in schema.strip:
        remove_nodes(src, ["element", {"tag": strip}])

    def recurse_check_tag(node: Root | Element):
        pop_els = []
        for idx, child in enumerate(node.children):
            if check(child, "element") and not is_element(child, schema.tag_names):
                pop_els.append(child)
            elif check(node.children[idx], "element"):
                recurse_check_tag(node.children[idx])

        for element in pop_els:
            node.children.remove(element)

    def recurse_check_ancestor(node: Root | Element):
        pop_els = []
        for idx, child in enumerate(node.children):
            if (
                check(child, "element")
                and child.tag in schema.ancestors.keys()
                and (
                    check(child.parent, "root")
                    or child.parent.tag not in schema.ancestors[child.tag]
                )
            ):
                pop_els.append(child)
            elif check(node.children[idx], "element"):
                recurse_check_ancestor(node.children[idx])

        for element in pop_els:
            node.children.remove(element)

    def build_valid_attributes(attributes: list) -> list[str]:
        """Extract attributes from schema."""
        valid_attrs = []
        for attribute in attributes:
            valid_attrs = (
                [*valid_attrs, attribute]
                if isinstance(attribute, str)
                else [*valid_attrs, attribute[0]]
            )
        return valid_attrs

    def build_remove_attr_list(properties: dict, attributes: dict, valid_attributes: list):
        """Build the list of attributes to remove from a dict of attributes."""
        result = []
        for attribute in properties:
            if attribute not in valid_attributes:
                result.append(attribute)
            else:
                for attr in attributes:
                    if isinstance(attr, list) and attr[0] == attribute and len(attr) > 1:
                        if not all(val == properties[attribute] for val in attr[1:]) or (
                            attribute in schema.protocols
                            and not check_protocols(
                                properties[attribute], schema.protocols[attribute]
                            )
                        ):
                            result.append(attribute)
                            break
                    elif (
                        attr == attribute
                        and attr in schema.protocols
                        and not check_protocols(properties[attribute], schema.protocols[attribute])
                    ):
                        result.append(attribute)
                        break

        return result

    def recurse_check_attributes(node: Root | Element):
        for idx, child in enumerate(node.children):
            if check(child, "element"):
                if child.tag in schema.attributes:
                    valid_attributes = build_valid_attributes(schema.attributes[child.tag])

                    pop_attrs = build_remove_attr_list(
                        node.children[idx].properties,
                        schema.attributes[child.tag],
                        valid_attributes,
                    )

                    for attribute in pop_attrs:
                        node.children[idx].properties.pop(attribute, None)

                recurse_check_attributes(node.children[idx])

    def recurse_check_required(node: Root | Element):
        for idx, child in enumerate(node.children):
            if check(child, "element") and child.tag in schema.required:
                for attr, value in schema.required[child.tag].items():
                    if attr not in child.properties:
                        node.children[idx][attr] = value

            elif check(node.children[idx], "element"):
                recurse_check_required(node.children[idx])

    def check_protocols(value: str, protocols: list[str]):
        for protocol in protocols:
            if match(f"{protocol}:.*", value) is not None:
                return True
        return False

    recurse_check_tag(src)
    recurse_check_ancestor(src)
    recurse_check_attributes(src)
    recurse_check_required(src)
