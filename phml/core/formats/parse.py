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
    Node
)

def parse_hypertest_markup(data: str, class_name: str, auto_close: bool = True) -> AST:
    """Parse a string as a hypertest markup document."""

    phml_parser = HypertextMarkupParser()

    if isinstance(data, str):
        return phml_parser.parse(data, auto_close=auto_close)
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
    taht the data ends at.
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
    tag_start = re.compile(r"<(?!!--)(?P<opening>!|\/)?(?P<name>([\w:\.]+\-?)+)|<(?P<opening2>/)?(?=\s+>|>)")
    """Matches the start of a tag `<!name|</name|<name`"""

    tag_end = re.compile(r"(?P<closing>/?)>")
    """Matches the end of a tag `/>|>`."""

    comment = re.compile(r"<!--((?:.|\s)*)-->")
    """Matches all html style comments `<!--Comment-->`."""

    attribute = re.compile(r"(?P<name>[\w:\-@]+)(?:=(?P<value>\{(?P<curly>[^\}]*)\/\}|\"(?P<double>[^\"]*)\"|'(?P<single>[^']*)'|(?P<open>[^>'\"]+)))?")
    """Matches a tags attributes `attr|attr=value|attr='value'|attr="value"`."""
    
    bracket_attributte = re.compile(r"^\s*\{((?:\s|.)*)\/\}\s*$")

class HypertextMarkupParser:
    """Parse html/xml like source code strings."""

    tag_stack = []
    """Current stack of tags in order of when they are opened."""
    
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
                    strip(text[:comment.span()[0]], self.tag_stack),
                    position=deepcopy(pos)
                ))

            text = text[comment.span()[1]:]
            elements.append(
                Comment(strip(comment.group(1), self.tag_stack), position=deepcopy(pos))
            )

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
            (
                name,
                value,
                _,
                double,
                single,
                no_bracket
            ) = itemgetter('name', 'value', 'curly', 'double', 'single', 'open')(attr.groupdict())

            if value is not None and RE.bracket_attributte.match(value) is not None:
                if not name.startswith(":"):
                    name = ":" + name
                value = RE.bracket_attributte.match(value).group(1)
            else:
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
        begin[2]["opening"] = begin[2]["opening"] or begin[2]["opening2"]

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

    def is_self_closing(self, name: str, auto_closing: bool) -> bool:
        """Check if the tag is self closing. Only check if auto_closing is toggled on."""

        if auto_closing:
            return name in self_closing
        return False

    def parse(self, source: str, auto_close: bool = True) -> Root:
        """Parse a given html or phml string into it's corresponding phml ast.

        Args:
            source (str): The html or phml source to parse.

        Returns:
            AST: A phml AST representing the parsed code source.
        """

        self.tag_stack = []
        current = Root()
        position = Position((0, 0), (0, 0))

        while RE.tag_start.search(source) is not None:
            source, begin, attr, end, elems = self.__parse_tag(source, position)

            if len(elems) > 0:
                current.extend(elems)

            name = begin[2]["name"] or ''
            if begin[2]["opening"] == "/":
                if name != self.tag_stack[-1]:
                    input(self.tag_stack)
                    raise Exception(
                        f"Unbalanced tags: {name!r} | {self.tag_stack[-1]!r} at {position}"
                    )

                self.tag_stack.pop()
                current.position.end.line = position.end.line
                current.position.end.column = position.end.column

                current = current.parent
            elif begin[2]["opening"] == "!":
                current.append(DocType(attr.get("lang", "html"), position=deepcopy(position)))
            elif (
                end[2]["closing"] != "/"
                and not self.is_self_closing(name, auto_close)
                and begin[2]["opening"] is None
            ):
                self.tag_stack.append(name)
                current.append(Element(name, attr, position=deepcopy(position)))
                current = current.children[-1]
            else:
                current.append(Element(name, attr, position=deepcopy(position), startend=True))

            position.start = deepcopy(position.end)

        return AST(current)
