"""Pythonic Hypertext Markup Language (phml) parser."""
from copy import deepcopy
from operator import itemgetter
import re

from phml.core.nodes import (
    AST,
    Comment,
    DocType,
    Element,
    Point,
    Position,
    Root,
    Text,
    Parent,
)
from phml.utilities.travel.travel import path_names

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


def parse_hypertest_markup(data: str, class_name: str, auto_close: bool = True) -> AST:
    """Parse a string as a hypertest markup document."""

    if isinstance(data, str):
        return AST(parse(data))
    raise Exception(f"Data passed to {class_name}.parse must be a str")


def strip_blank_lines(data_lines: list[str]) -> list[str]:
    """Strip the blank lines at the start and end of a list."""
    data_lines = [line.replace("\r\n", "\n") for line in data_lines]
    # remove leading blank lines
    for idx in range(0, len(data_lines)):  # pylint: disable=consider-using-enumerate
        if data_lines[idx].strip() != "":
            data_lines = data_lines[idx:]
            break
        if idx == len(data_lines) - 1:
            data_lines = []
            break

    # Remove trailing blank lines
    if len(data_lines) > 0:
        for idx in range(len(data_lines) - 1, -1, -1):
            if data_lines[idx].replace("\n", " ").strip() != "":
                data_lines = data_lines[: idx + 1]
                break

    return data_lines


def strip(data: str, cur_tags: list[str]) -> tuple[str, int, int]:
    """This function takes a possibly mutliline string and strips leading and trailing
    blank lines. Given the current position it will also calculate the line and column
    that the data ends at.
    """
    if "pre" not in cur_tags:
        data_lines = data.split("\n")

        # If multiline data block
        if len(data_lines) > 1:
            data_lines = strip_blank_lines(data_lines)

            data = "\n".join(data_lines)
        # Else it is a single line data block
        else:
            data = data_lines[0]

    return data


REGEX = {
    "element": re.compile(
        r"<!--(?P<comment>[\w\W]*)-->|<(?P<decl>!)?(?P<name>[\w]+(?:[\w.:\-]+)*)(?P<attrs>(?:\s*([\w:.\-]+=\"[^\"]*\"|[\w:.\-]+='[^']*'|[\w:.\-]+=[^ />]+|[\w:.\-]+))*)\s*(?P<closing>\/)?>|<(?!!--)(?=\s*/?>)"
    ),
    "end_tag": "</\\s*{}\\s*>",
    "attr": re.compile(
        r"((?P<n1>[\w:.\-]+)='(?P<v1>[^']*)'|(?P<n2>[\w:.\-]+)=\"(?P<v2>[^\"]*)\"|(?P<n3>[\w:.\-]+)=(?P<v3>[^>\s]+)|(?P<n4>[\w:.\-]+))"
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


def calc_end(text: str, start: Point):
    """Calculate the end position of a given text block."""
    line = start.line + text.count("\n")
    col = (
        max(1, len(text.rsplit("\n", 1)[-1]))
        if text.count("\n") > 0
        else start.column + len(text)
    )
    return Point(line, col)


def parse(
    data: str,
    context: Parent = Root(),
    position: Position = Position((1, 1, None), (1, 1, None)),
):
    """Parse an element and it's tags."""

    while REGEX["element"].search(data) is not None:
        tag = REGEX["element"].search(data)
        tag_info = tag.groupdict()
        whole = tag.group(0)

        start = tag.start()
        if start > 0:
            text_pos = deepcopy(position)
            text_pos.end = calc_end(data[:start], text_pos.start)
            if (
                isinstance(context, Element)
                and "pre" not in path_names(context)
                and "pre" != context.tag
            ) or isinstance(context, Root):
                if data[:start].strip() != "":
                    context.append(Text(data[:start].strip(), position=text_pos))
            else:
                context.append(Text(data[:start], position=text_pos))

            position.start.line = text_pos.end.line
            position.start.column = text_pos.end.column + 1

        data = data[start + len(whole) :]
        if tag_info["decl"] is not None:
            start = position.start
            end = calc_end(whole, start)
            attrs: list[str] = list(parse_attrs(tag_info["attrs"]).keys())
            context.append(
                DocType(
                    attrs[0] if len(attrs) > 0 else "html",
                    position=Position(
                        (start.line, start.column, None), (end.line, end.column, None)
                    ),
                )
            )
            position = Position(end, end)
        if tag_info["comment"] is None:
            end = re.compile(REGEX["end_tag"].format(tag_info["name"]))
            end_tag = end.search(data)

            if end_tag is None or tag_info["closing"] is not None:
                if tag_info["name"] not in self_closing and tag_info["closing"] is None:
                    raise ValueError(f"<{tag_info['name']}> tag was not closed")
                else:
                    attrs: dict = parse_attrs(tag_info["attrs"])
                    start = position.start
                    end = calc_end(whole, position.start)
                    context.append(
                        Element(
                            tag_info["name"],
                            {
                                key: value
                                for key, value in attrs.items()
                                if key.strip() != ""
                            },
                            position=Position(
                                (start.line, start.column, None),
                                (end.line, end.column, None),
                            ),
                            startend=True,
                        )
                    )
                    position = Position(end, end)
            else:
                attrs = parse_attrs(tag_info["attrs"])
                start = position.start
                end = calc_end(
                    data[: end_tag.start() + len(end_tag.group(0))],
                    calc_end(whole[1:], start),
                )
                new_node = Element(
                    tag=tag_info["name"] or "",
                    properties={
                        key: value for key, value in attrs.items() if key.strip() != ""
                    },
                    children=[],
                    position=Position(
                        (start.line, start.column, None), (end.line, end.column, None)
                    ),
                )
                context.append(new_node)
                start = calc_end(whole, position.start)
                parse(
                    data[: end_tag.start()],
                    new_node,
                    Position(
                        (start.line, start.column, None),
                        (position.end.line, position.end.column, None),
                    ),
                )
                data = data[end_tag.start() + len(end_tag.group(0)) :]
                position = Position(end, end)
        elif tag_info["comment"] is not None:
            start = position.start
            end = calc_end(tag_info["comment"], start)
            end.column += 6
            if tag_info["comment"].count("\n") > 0:
                end.column -= 4
            context.append(
                Comment(
                    tag_info["comment"],
                    position=Position(
                        (start.line, start.column, None),
                        (end.line, end.column, None),
                    ),
                )
            )
            position = Position(end, end)

    if len(data) > 0:
        start = position.start
        end = calc_end(data, start)
        pos = Position(
            (start.line, start.column, None),
            (end.line, max(0, end.column - 1), None),
        )
        if (
            isinstance(context, Element)
            and "pre" not in path_names(context)
            and "pre" != context.tag
        ) or isinstance(context, Root):
            if data.strip() != "":
                context.append(Text(data.strip(), position=pos))
        else:
            context.append(Text(data, position=pos))

        position = Position(end, end)

    return context

