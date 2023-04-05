from re import match

from phml.nodes import Element, Parent

from .schema import Schema


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
        check,
        is_element,
        remove_nodes,
    )

    for strip in schema.strip:
        remove_nodes(tree, ["element", {"tag": strip}])

    def recurse_check_tag(node: Parent):
        pop_els = []
        for child in node:
            if check(child, "element") and not is_element(child, schema.tag_names):
                pop_els.append(child)
            elif isinstance(child, Parent):
                recurse_check_tag(child)

        for element in pop_els:
            node.remove(element)

    def recurse_check_ancestor(node: Parent):
        pop_els = []
        for child in node:
            if (
                isinstance(child, Element)
                and child.tag in schema.ancestors
                and (
                    isinstance(child.parent, Element)
                    and child.parent.tag not in schema.ancestors[child.tag]
                )
            ):
                pop_els.append(child)
            elif isinstance(child, Element):
                recurse_check_ancestor(child)

        for element in pop_els:
            node.remove(element)

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

    def build_remove_attr_list(
        properties: dict, attributes: list, valid_attributes: list
    ):
        """Build the list of attributes to remove from a dict of attributes."""
        result = []
        for attribute in properties:
            if attribute not in valid_attributes:
                result.append(attribute)
            else:
                for attr in attributes:
                    if (
                        isinstance(attr, list)
                        and attr[0] == attribute
                        and len(attr) > 1
                    ):
                        if not all(
                            val == properties[attribute] for val in attr[1:]
                        ) or (
                            attribute in schema.protocols
                            and not check_protocols(
                                properties[attribute],
                                schema.protocols[attribute],
                            )
                        ):
                            result.append(attribute)
                            break
                    elif (
                        attr == attribute
                        and attr in schema.protocols
                        and not check_protocols(
                            properties[attribute], schema.protocols[attribute]
                        )
                    ):
                        result.append(attribute)
                        break

        return result

    def recurse_check_attributes(node: Parent):
        for child in node:
            if isinstance(child, Element):
                if child.tag in schema.attributes:
                    valid_attributes = build_valid_attributes(
                        schema.attributes[child.tag]
                    )

                    # PERF: Not sure if the attributes are still being sanatized correctly
                    pop_attrs = build_remove_attr_list(
                        child.attributes,
                        schema.attributes[child.tag],
                        valid_attributes,
                    )

                    for attribute in pop_attrs:
                        child.pop(attribute, None)

                recurse_check_attributes(child)

    def recurse_check_required(node: Parent):
        for child in node:
            if isinstance(child, Element) and child.tag in schema.required:
                for attr, value in schema.required[child.tag].items():
                    if attr not in child.attributes:
                        child[attr] = value

            elif isinstance(child, Element):
                recurse_check_required(child)

    def check_protocols(value: str, protocols: list[str]):
        return any(match(f"{protocol}:.*", value) is not None for protocol in protocols)

    recurse_check_tag(tree)
    recurse_check_ancestor(tree)
    recurse_check_attributes(tree)
    recurse_check_required(tree)
