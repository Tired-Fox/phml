"""."""
import re
from pathlib import Path

from typing import Any, Literal
from nodes import Literal, Node, Root, Element, position, Parent
from v2.nodes import NodeType

self_closing = [
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
    "command",
    "keygen",
    "menuitem",
]

REGEX = {
    "element": re.compile(
        r"<!--(?P<comment>[\w\W]*)-->|<(?P<decl>!)?(?P<name>[\w]+(?:[\w.:]+)*)(?P<attrs>(?:\s*([\w:.]+=\"[^\"]*\"|[\w:.]+='[^']*'|[\w:.]+=[^ />]+|[\w:.]+))*)\s*(?P<closing>\/)?>|<(?!!--)(?=\s*/?>)"
    ),
    "end_tag": "</\\s*{}\\s*>",
    "attr": re.compile(
        r"((?P<n1>[\w:.]+)='(?P<v1>[^']*)'|(?P<n2>[\w:.]+)=\"(?P<v2>[^\"]*)\"|(?P<n3>[\w:.]+)=(?P<v3>[^>\s]+)|(?P<n4>[\w:.]+))"
    ),
}


def parse_attr_value(attrs: str, stop_chars: str | None = None):
    stop_pattern = (
        re.compile(f"^[{stop_chars}]$")
        if stop_chars is not None
        else re.compile(r"^[>\s]$")
    )
    i = 0
    while i < len(attrs) and stop_pattern.match(attrs[i]) is None:
        i += 1

    if stop_chars is not None and attrs[i] not in stop_chars:
        raise ValueError(
            "Attribute not closed. Expected <{', '.join(repr(c) for c in stop_chars)}>"
        )

    return attrs[:i], i


def parse_attrs(attrs: str) -> dict:
    """Parse the valid attributes that are found in the attributes string from
    an elements open tag.
    """
    attrs = attrs.strip()

    results = {}
    for attr in REGEX["attr"].finditer(attrs):
        attr = attr.groupdict()
        name = attr["n1"] or attr["n2"] or attr["n3"] or attr["n4"]
        value = attr["v1"] or attr["v2"] or attr["v3"] or True
        results[name] = value
    return results


def parse_tags(data: str, context: Parent):
    """Parse an element and it's tags."""

    while REGEX["element"].search(data) is not None:
        tag = REGEX["element"].search(data)
        tag_info = tag.groupdict()

        start = tag.start()
        if start > 0:
            if isinstance(context, Element) and "pre" not in context.tag_path:
                if data[:start].strip() != "":
                    context.append(Literal("text", data[:start].strip()))
            else:
                context.append(Literal("text", data[:start]))
        data = data[start + len(tag.group(0)) :]
        if tag_info["comment"] is None:
            end = re.compile(REGEX["end_tag"].format(tag_info["name"]))
            end_tag = end.search(data)

            if end_tag is None or tag_info["closing"] is not None:
                if tag_info["name"] not in self_closing and tag_info["closing"] is None:
                    raise ValueError(f"<{tag_info['name']}> tag was not closed")
                else:
                    attrs = parse_attrs(tag_info["attrs"])
                    context.append(
                        Element(
                            tag_info["name"],
                            {
                                key: value
                                for key, value in attrs.items()
                                if key.strip() != ""
                            },
                            position=None,
                        )
                    )
            else:
                attrs = parse_attrs(tag_info["attrs"])
                new_node = Element(
                    tag=tag_info["name"] or "",
                    attributes={key: value for key, value in attrs.items() if key.strip() != ""},
                    children=[],
                    position=None,
                )
                context.append(new_node)
                parse_tags(data[: end_tag.start()], new_node)
                data = data[end_tag.start() + len(end_tag.group(0)) :]
        elif tag_info["comment"] is not None:
            context.append(Literal("comment", tag_info["comment"]))

    if len(data) > 0:
        if isinstance(context, Element) and "pre" not in context.tag_path:
            if data.strip() != "":
                context.append(Literal("text", data.strip()))
        else:
            context.append(Literal("text", data))


if __name__ == "__main__":
    with Path("sandbox/sample.phml").open("r", encoding="utf-8") as file:
        data = file.read()

    root: Root = Root([])
    parse_tags(data, root)
    # print(root)
    print(root[0])
    if isinstance(root[0], Parent):
        for child in root[0]:
            if isinstance(child, Element) and child.tag == "body":
                for c in child:
                    print(c)
