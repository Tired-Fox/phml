from typing import Optional

from phml.nodes import AST, Element, Root

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

    from phml.utils import is_element, remove_nodes, test

    if isinstance(tree, AST):
        src = tree.tree
    else:
        src = tree

    for strip in schema.strip:
        remove_nodes(src, ["element", {"tag": strip}])

    def recurse_check_tag(node: Root | Element):
        pop_els = []
        for idx, child in enumerate(node.children):
            if test(child, "element") and not is_element(child, schema.tagNames):
                pop_els.append(child)
            elif test(node.children[idx], "element"):
                recurse_check_tag(node.children[idx])

        for el in pop_els:
            node.children.remove(el)

    def recurse_check_ancestor(node: Root | Element):
        pop_els = []
        for idx, child in enumerate(node.children):
            if (
                test(child, "element")
                and child.tag in schema.ancestors.keys()
                and child.parent.tag not in schema.ancestors[child.tag]
            ):
                pop_els.append(child)
            elif test(node.children[idx], "element"):
                recurse_check_ancestor(node.children[idx])

        for el in pop_els:
            node.children.remove(el)

    def recurse_check_attributes(node: Root | Element):
        for idx, child in enumerate(node.children):
            if test(child, "element") and child.tag in schema.attributes.keys():
                valid_attrs = []
                for attr in schema.attributes[child.tag]:
                    if isinstance(attr, str):
                        valid_attrs.append(attr)
                    elif isinstance(attr, list):
                        valid_attrs.append(attr[0])

                pop_attrs = []
                for attr in node.children[idx].properties:
                    if attr not in valid_attrs:
                        pop_attrs.append(attr)
                    else:
                        for a in schema.attributes[child.tag]:
                            if isinstance(a, str) and a != attr:
                                pop_attrs.append(attr)
                            elif a[0] == attr and node.children[idx].properties[attr] not in a[1:]:
                                pop_attrs.append(attr)
                            elif attr in schema.protocols and not check_protocols(
                                child.properties[attr], schema.protocols[attr]
                            ):
                                pop_attrs.append(attr)

                for attr in pop_attrs:
                    node.children[idx].properties.pop(attr, None)

            elif test(node.children[idx], "element"):
                recurse_check_attributes(node.children[idx])

    def recurse_check_required(node: Root | Element):
        for idx, child in enumerate(node.children):
            if test(child, "element") and child.tag in schema.required.keys():
                for attr, value in schema.required[child.tag].items():
                    if attr not in child.properties:
                        node.children[idx].properties[attr] = value

            elif test(node.children[idx], "element"):
                recurse_check_required(node.children[idx])

    def check_protocols(value: str, protocols: list[str]):
        from re import match

        for protocol in protocols:
            if match(f"{protocol}:.*", value) is not None:
                return True
        return False

    recurse_check_tag(src)
    recurse_check_ancestor(src)
    recurse_check_attributes(src)
    recurse_check_required(src)


if __name__ == "__main__":
    from phml.builder import p
    from phml.utils import inspect

    el = p(
        "div",
        p("input", {"disabled": True, "width": "100px"}),
        p("custom"),
        p("script", "h1{color:blue;}"),
        p("li", "li without ol or ul"),
        p("blockquote", {"cite": "mailto:zboehm104@gmail.com"}),
    )

    sanatize(el)
