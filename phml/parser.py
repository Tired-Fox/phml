"""Pythonic Hypertext Markup Language (phml) parser."""
from copy import deepcopy
from operator import itemgetter
import re

from .nodes import (
    AST,
    Node,
    Element,
    Literal,
    Point,
    Position,
    Parent,
    LiteralType,
    Attribute,
)


def strip(data: str, cur_tags: list[str]) -> str:
    """This function takes a possibly multiline string and strips leading and trailing
    blank lines. Given the current tag stack it will not strip the text if it is nested
    in a `pre` tag.
    """
    if len(cur_tags) > 0 and (
        "python" == cur_tags[-1]
        or "script" == cur_tags[-1]
        or "style" == cur_tags[-1]
        or "pre" in cur_tags
    ):
        return data
    return data.strip()


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
    "Slot",
    "Markdown",
]


# Main form of tokenization
class RE:
    tag_start = re.compile(
        r"(?P<comment><!--)|<(?!!--)(?P<opening>!|\/)?(?P<name>([\w:\.]+\-?)+)|<(?P<opening2>/)?(?=\s+>|>)"
    )
    """Matches the start of a tag `<!name|</name|<name`"""

    tag_end = re.compile(r"(?P<closing>/?)>")
    """Matches the end of a tag `/>|>`."""

    comment = re.compile(r"<!--((?:.|\s)*)-->")
    """Matches all html style comments `<!--Comment-->`."""
    comment_close = re.compile(r"-->")

    attribute = re.compile(
        r"(?P<name>[\w:\-@]+)(?:=(?P<value>\{(?P<curly>[^\}]*)\/\}|\"(?P<double>[^\"]*)\"|'(?P<single>[^']*)'|(?P<open>[^>'\"\s]+)))?"
    )
    """Matches a tags attributes `attr|attr=value|attr='value'|attr="value"`."""

    bracket_attributte = re.compile(r"^\s*\{((?:\s|.)*)\/\}\s*$")


class HypertextMarkupParser:
    """Parse html/xml like source code strings."""

    tag_stack = []
    """Current stack of tags in order of when they are opened."""
    in_pre: int = 0
    """Whether the current element context is inside a pre element."""

    def __calc_line_col(self, source: str, start: int) -> tuple[int, int]:
        """Calculate the number of lines and columns that lead to the starting point int he source
        string.
        """
        source = source[:start]
        return (
            source.count("\n"),
            len(source.split("\n")[-1]) if len(source.split("\n")) > 0 else 0,
        )

    def __calc_col(self, num_lines: int, num_cols: int, init_cols: int) -> int:
        """Calculate whether the number of columns should be added to the current column or be
        treated as if it is starting from zero based on whether new lines exist.
        """
        return num_cols if num_lines != 0 else init_cols + num_cols

    def __parse_text(self, text: str, pos: Position) -> Literal|None:
        """Parse the comments and general text found in the provided source."""

        if len(text) > 0 and strip(text, self.tag_stack) != "":
            line, col = self.__calc_line_col(text, len(text))
            pos.start.line += line
            pos.start.column = col

            pos.end.line += line
            pos.end.column = self.__calc_col(line, col, pos.end.column)
            return Literal(
                LiteralType.Text,
                strip(text, self.tag_stack),
                position=Position.from_pos(pos),
                in_pre=self.in_pre > 0,
            )

        return None

    def __parse_attributes(self, attrs: str) -> dict[str, Attribute]:
        """Parse a tags attributes from the text found between the tag start and the tag end.

        Example:
            `<name (attributes)>`
        """
        attributes = {}
        for attr in RE.attribute.finditer(attrs):
            (name, value, _, double, single, no_bracket) = itemgetter(
                "name", "value", "curly", "double", "single", "open"
            )(attr.groupdict())

            value = double or single or no_bracket

            if value in ["yes", "true", None]:
                value = True
            elif value in ["no", "false"]:
                value = False

            attributes[name] = value
        return attributes

    def __parse_tag(self, source, position: Position):
        """Parse a tag from the given source. This includes the tag start, attributes and tag end.
        It will also parse any comments and text from the start of the source to the start of the
        tag.
        """
        begin = RE.tag_start.search(source)
        begin = (begin.start(), begin.group(0), begin.groupdict())

        elem = None
        if begin[0] > 0:
            elem = self.__parse_text(source[: begin[0]], position)

        position.end.column = position.start.column + len(begin[1])
        source = source[begin[0] + len(begin[1]) :]

        if begin[2]["comment"] is not None:
            end = RE.comment_close.search(source)
            if end is None:
                raise Exception("Comment was not closed")
            end = (end.start(), end.group(0), end.groupdict())
            attributes: dict[str, Attribute] = {"data": source[: end[0]]}
        else:
            begin[2]["opening"] = begin[2]["opening"] or begin[2]["opening2"]
            end = RE.tag_end.search(source)
            if end is None:
                raise Exception(
                    f"Expected tag {begin[1]} to be closed with symbol '>'. Was not closed."
                )
            end = (end.start(), end.group(0), end.groupdict())
            if begin[2]["opening"] == "/" and "<" in source[:end[0]]:
                line, col = self.__calc_line_col(source, end[0]+len(end[1]))
                position.end.line = position.start.line + line
                position.end.column = position.end.column + col
                raise Exception(f"Closing tag {begin[1]!r} was not closed, maybe it is missing a '>' symbol")
            attributes = self.__parse_attributes(source[: end[0]])

        line, col = self.__calc_line_col(source, end[0] + len(end[1]))
        position.end.line = position.start.line + line
        position.end.column = position.end.column + col

        return source[end[0] + len(end[1]) :], begin, attributes, end, elem

    def is_self_closing(self, name: str, auto_closing: bool) -> bool:
        """Check if the tag is self closing. Only check if auto_closing is toggled on."""

        if auto_closing:
            return name in self_closing
        return False # pragma: no cover

    def parse(self, source: str, auto_close: bool = True) -> AST | Node | None:
        """Parse a given html or phml string into it's corresponding phml ast.

        Args:
            source (str): The html or phml source to parse.

        Returns:
            AST: A phml AST representing the parsed code source.
        """

        self.tag_stack = []
        current = AST()
        position = Position((0, 0), (0, 0))

        while RE.tag_start.search(source) is not None and current is not None:
            source, begin, attr, end, elem = self.__parse_tag(source, position)

            if elem is not None:
                current.append(elem)

            if begin[2]["comment"] is not None:
                current.append(
                    Literal(
                        LiteralType.Comment,
                        str(attr["data"]),
                        position=Position.from_pos(position),
                        in_pre=self.in_pre > 0,
                    )
                )
            else:
                name = begin[2]["name"] or ""
                if begin[2]["opening"] == "/":
                    if name != self.tag_stack[-1]:
                        print("Tag Stack", self.tag_stack)
                        raise Exception(
                            f"Unbalanced tags: {name!r} | {self.tag_stack[-1]!r} at {position}"
                        )

                    ptag = self.tag_stack.pop()
                    if ptag == "pre":
                        self.in_pre -= 1

                    if current.position is not None:
                        current.position.end.line = position.end.line
                        current.position.end.column = position.end.column

                    current = current.parent
                elif begin[2]["opening"] == "!":
                    current.append(
                        Element(
                            "doctype",
                            {"lang": attr.get("lang", "html")},
                            position=Position.from_pos(position),
                        )
                    )
                elif (
                    end[2]["closing"] != "/"
                    and not self.is_self_closing(name, auto_close)
                    and begin[2]["opening"] is None
                ):
                    self.tag_stack.append(name)
                    if name == "pre":
                        self.in_pre += 1
                    current.append(
                        Element(
                            name,
                            attr,
                            [],
                            position=Position.from_pos(position),
                            in_pre=self.in_pre > 0,
                        )
                    )
                    if len(current) > 0:
                        current = current[-1]
                else:
                    current.append(
                        Element(
                            name,
                            attr,
                            position=deepcopy(position),
                            in_pre=self.in_pre > 0,
                        )
                    )

            position.start = Point(position.end.line, position.end.column)

        if len(source) > 0:
            elem = self.__parse_text(source, position)
            if (
                current is not None
                and isinstance(current, Parent)
                and current.children is not None
                and elem is not None
            ):
                current.append(elem)

        if len(self.tag_stack) > 0:
            raise Exception(
                f"The following tags where expected to be closed but where not: {', '.join(repr(tag) for tag in self.tag_stack)}"
            )
        return current
