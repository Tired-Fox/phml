from __future__ import annotations
from copy import deepcopy
import re
# https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
# https://www.jsonrpc.org/specification

from phml.core.nodes import Root, Element, Text, Comment, Node, Position, Point, DocType
from phml import inspect, query, PHML

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

# Main form of tokenization
class RE:
    tag_start = re.compile(r"<(?!!--)(?P<opening>!|\/)?(?P<name>([\w:\.]+\-?)*)|<(?=\s+|>)")
    """Matches the start of a tag `<!name|</name|<name`"""

    tag_end = re.compile(r"(?P<closing>/?)>")
    """Matches the end of a tag `/>|>`."""

    comment = re.compile(r"<!--((?:.|\s)*)-->")
    """Matches all html style comments `<!--Comment-->`."""

    attribute = re.compile(r"([\w:\-@]+)(?:=(\"([^\"]*)\"|'([^']*)'|([^>'\"]+)))?")
    """Matches a tags attributes `attr|attr=value|attr='value'|attr="value"`."""

class HTMLParser:
    def __calc_line_col(self, source: str, start: int) -> tuple[int, int]:
        """Calculate the number of lines and columns that lead to the starting point int he source
        string.
        """
        source = source[:start]
        return source.count("\n"), len(source.split("\n")[-1]) if len(source.split("\n")) > 0 else 0

    def __calc_col(self, num_lines: int, num_cols: int, init_cols: int) -> int:
        """Calculate whether the number of columns should be added to the current column or be
        treated as if it is starting from zero based on whether new lines exist.
        """
        return num_cols if num_lines != 0 else init_cols + num_cols

    def __parse_text_comment(self, text: str, pos: Position) -> list[Node]:
        """Parse the comments and general text found in the provided source."""

        elements = [] # List of text and comment elements.

        # For each comment add it to the list of elements
        while RE.comment.search(text) is not None:
            comment = RE.comment.search(text)
            line_s, col_s = self.__calc_line_col(text, comment.start())
            line_e, col_e = self.__calc_line_col(comment.group(0), len(comment.group(0)))

            pos.start = Point(
                pos.start.line + line_s,
                self.__calc_col(line_s, col_s, pos.start.column)
            )
            pos.end = Point(
                pos.start.line + line_e,
                self.__calc_col(line_e, col_e, pos.start.column)
            )

            # If there is text between two comments then add a text element
            if comment.start() > 0 and text[:comment.start()].strip() != "":
                elements.append(Text(
                    text[:comment.span()[0]],
                    position=deepcopy(pos)
                ))

            text = text[comment.span()[1]:]
            elements.append(Comment(comment.group(1), position=deepcopy(pos)))

        # remaining text is added as a text element
        if len(text) > 0:
            line, col = self.__calc_line_col(text, len(text))
            pos.start.line += line
            pos.start.column = col

            if text.strip() != "":
                elements.append(Text(
                    text,
                    position=Position(
                        deepcopy(pos.end),
                        (pos.end.line + line, self.__calc_col(line, col, pos.end.column))
                    )
                ))
        return elements

    def __parse_attributes(self, attrs: str) -> dict:
        """Parse a tags attributes from the text found between the tag start and the tag end.
        
        Example:
            `<name (attributes)>`
        """
        attributes = {}
        for attr in RE.attribute.finditer(attrs):
            name, value, i1, i2, i3 = attr.groups()
            value = i1 or i2 or i3

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

        elems = []
        if begin[0] > 0:
            elems = self.__parse_text_comment(source[:begin[0]], position)
        position.end.column = position.start.column + len(begin[1])
        source = source[begin[0] + len(begin[1]):]

        end = RE.tag_end.search(source)
        if end is None:
            raise Exception(f"Expected tag {begin} to be closed with symbol '>'. Was not closed.")
        end = (end.start(), end.group(0), end.groupdict())

        line, col = self.__calc_line_col(source, end[0] + len(end[1]))
        position.end.line = position.start.line + line
        position.end.column = position.end.column + col

        attributes = self.__parse_attributes(source[:end[0]])
        return source[end[0] + len(end[1]):], begin, attributes, end, elems

    def parse(self, source: str) -> Root:
        """Parse a given html or phml string into it's corresponding phml ast.

        Args:
            source (str): The html or phml source to parse.

        Returns:
            AST: A phml AST representing the parsed code source.
        """

        tag_stack = []
        current = Root()
        position = Position((0, 0), (0, 0))

        while RE.tag_start.search(source) is not None:
            source, begin, attr, end, elems = self.__parse_tag(source, position)

            if len(elems) > 0:
                current.extend(elems)

            print(begin[1], end[1])
            name = begin[2]["name"] or ''
            if begin[2]["opening"] == "/":
                if name != tag_stack[-1]:
                    input(tag_stack)
                    raise Exception(f"Unbalanced tags: {name!r} | {tag_stack[-1]!r} at {position}")

                tag_stack.pop()
                current.position.end.line = position.end.line
                current.position.end.column = position.end.column

                current = current.parent
            elif begin[2]["opening"] == "!":
                current.append(DocType(attr.get("lang", "html"), position=deepcopy(position)))
            elif (
                end[2]["closing"] != "/"
                and name not in self_closing
                and begin[2]["opening"] is None
            ):
                tag_stack.append(name)
                current.append(Element(name, attr, position=deepcopy(position)))
                current = current.children[-1]
            else:
                current.append(Element(name, attr, position=deepcopy(position)))

            position.start = deepcopy(position.end)

        return current

# with open("page.phml", "r", encoding="utf-8") as file:
#     ast = HTMLParser().parse(file.read())

# print(inspect(ast))

# python_block = query(ast, "python")
# if python_block is not None:
#     print(python_block.children[0].normalized)
phml = PHML()
phml.add("Name.phml")
print(phml.load("page.phml").render())
print(phml.load("page2.phml").render())