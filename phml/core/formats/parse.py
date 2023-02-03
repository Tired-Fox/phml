"""Pythonic Hypertext Markup Language (phml) parser."""
from dataclasses import dataclass
import re
from teddecor import TED

from phml.core.nodes import (
    AST,
    Comment,
    DocType,
    Element,
    Point,
    Position,
    Properties,
    Root,
    Text,
    All_Nodes,
    PI,
    Parent,
)

REGEX = {
    "tag": re.compile(
        r"<!--(.*)-->|<(!|\?|\/)?([a-zA-Z0-9\.\-_:]*)((\s*[^ \"'><=\/\?]+(=\"[^\"]+\"|='[^']+'|=[^\s>]+)?)*)\s*(\/|\?)?\s*>"
    ),
    "attributes": re.compile(r"\s*([^<>\"'\= ]+)((=)\"([^\"]*)\"|(=)'([^']*)'|(=)([^<>\= ]+))?"),
    "whitespace": re.compile(r"\s+"),
}

self_closing_tags = [
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


def calc_end_of_tag(tag_text: str, cur_pos: tuple[int, int]) -> tuple[int, int]:
    """Given the current position and the open tag text, this function
    calculates where the start tag ends.
    """
    lines = tag_text.split("\n")
    line = len(lines) - 1
    col = len(lines[-1]) + cur_pos[1] if len(lines) == 1 else len(lines[-1])

    return cur_pos[0] + line, col


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


@dataclass
class Specifier:
    Open: str = "Open"
    Decleration: str = "DECLERATION"
    ProcProfile: str = "PROC_PROFILE"
    Close: str = "Close"

    @classmethod
    def of(cls, tag_type: str) -> str:
        if tag_type in ["", None]:
            return cls.Open
        elif tag_type == "!":
            return cls.Decleration
        elif tag_type == "?":
            return cls.ProcProfile
        elif tag_type == "/":
            return cls.Close

        raise TypeError(f"Unkown tag type <{tag_type}>: valid types are '', '!', '?', '/'")


class HypertextMarkupParser:
    """Parse languages like XML, HTML, PHML, etc; into a PHML AST."""

    def parse(self, source: str, auto_close: bool = True) -> AST:
        """Takes a string of the source markup and returns the resulting
        PHML AST.
        """
        element = REGEX["tag"].search(source)
        previous = Position((0, 0), (0, 0))

        tag_stack = []

        root = Root()
        current: Parent = root
        count = 0

        
        for element in REGEX["tag"].finditer(source):
            comment, tag_type, tag_name, tag_attributes, _, _, closing = element.groups()

            # Create position in file
            position, text = self.__calculate(
                source, element.group(0), (count, element.start()), previous
            )
            
            if "pre" in tag_stack:
                current.append(
                    Text(text, position=Position(previous.end, position.start))
                )
            elif text.strip() != "":
                current.append(
                    Text(strip(text, tag_stack), position=Position(previous.end, position.start))
                )
            # Generate Element for tag found
            if comment is None:
                (_type, name, attrs, closing) = self.__parse_tag(
                    tag_type, tag_name, tag_attributes, closing, pos=position, auto_close=auto_close
                )
            else:
                current.append(
                    Comment(
                        strip(comment, tag_stack) if comment is not None else "", position=position
                    )
                )
                count = element.start() + len(element.group(0))
                previous = position
                continue

            if _type == Specifier.Close:
                if tag_stack[-1] != name:
                    print(tag_stack, element.groups())
                    raise Exception(f"Unbalanced tags {tag_stack[-1]!r} and {name!r} at {position}")
                _ = tag_stack.pop()

                current = current.parent
            elif _type in [Specifier.Open, Specifier.Decleration, Specifier.ProcProfile]:
                current.append(self.__create_node(_type, name, attrs, closing, position))
                if _type == Specifier.Open and closing != Specifier.Close:
                    tag_stack.append(name)
                    current = current.children[-1]

            count = element.start() + len(element.group(0))
            previous = position

        if count < len(source):
            position, text = self.__calculate(source, source[count:], (count, count), previous)
            current.append(Text(strip(source, tag_stack), position=position))

        return AST(root)

    def __parse_tag(
        self,
        tag_type: str | None = None,
        name: str | None = None,
        tag_attrs: str | None = None,
        closing: str | None = None,
        pos: tuple[int, int] | None = None,
        auto_close: bool = True
    ):
        """Take the raw parts from the tag regex and parse it the appropriatly processed parts.

        Parts:
            - type (Specifier): Open tag, closing tag, decleration, or process profile.
                '', '?', '!', '/'.
            - name (str): Tag name. Required for process profiles and declerations.
            - attributes (dict[str, str]): Attributes for a given open tag.
            - closing (str): The tag can be closed with '/', or '?'. Must be closed with '?' if
                process profile.

        Note:
            Will automatically mark auto closing tags as self closing tags.
        """
        tag_type = Specifier.of(tag_type)
        tag_name = name or ""

        tag_attrs = REGEX["whitespace"].sub(" ", tag_attrs or "")
        attributes = REGEX["attributes"].findall(tag_attrs or "")

        attrs: Properties = {}

        for attribute in attributes:
            value = True
            attribute = [
                attribute[0],
                [item for item in [attribute[3], attribute[5], attribute[7]] if item != ""],
            ]
            attribute[1] = attribute[1][0] if len(attribute[1]) > 0 else ""
            if attribute[1] in ["true", "false", "yes", "no", ""]:
                value = attribute[1] in ["true", "yes", ""]
            else:
                value = attribute[1]
            attrs[attribute[0]] = value

        closing = Specifier.of(closing)

        if tag_type == Specifier.ProcProfile and (
            closing != Specifier.ProcProfile or tag_name == ""
        ):
            position = f" [$]{pos}[$]" if pos is not None else ""
            attrs = ' ' + tag_attrs if tag_attrs is not None else ''
            name = tag_name if tag_name != '' else "[@Fred]NAME[@F]"
            close = "?" if closing == Specifier.ProcProfile else "[@Fred]?[@F]"
            raise Exception(
                TED.parse(f"Invalid Processor Profile{position}: *<?{name}[@F]{attrs}{close}>")
            )

        if tag_type == Specifier.Decleration and tag_name == "":
            position = (
                f" \\[[@Fcyan]{pos[0]}[@F]:[@Fcyan]{pos[1]}[@F]\\]" if pos is not None else ""
            )
            attrs = ' ' + tag_attrs if tag_attrs is not None else ''
            name = tag_name if tag_name != '' else "[@Fred]NAME[@F]"
            raise Exception(TED.parse(f"Invalid Decleration {position}: *<!{tag_name}{attrs}>"))

        if closing == Specifier.Open and tag_name in self_closing_tags and auto_close:
            closing = Specifier.of("/")

        return tag_type, tag_name, attrs, closing

    def __create_node(
        self, tag_type: str, name: str, attrs: str, closing: str, position: Position | None
    ) -> All_Nodes:
        """Create a PHML node based on the data from the parsed tag."""

        if tag_type == Specifier.Open:
            return Element(name, attrs, startend=closing == Specifier.Close, position=position)
        elif tag_type == Specifier.Decleration:
            if name.lower() == "doctype":
                lang = "html"
                if len(attrs) > 0:
                    lang = list(attrs.keys())[0]
                return DocType(lang, position=position)
        elif tag_type == Specifier.ProcProfile:
            return PI(name, attrs, position=position)

    def __calculate(
        self, source: str, tag: str, locations: tuple[int, int], previous: Position
    ) -> tuple[Position, str]:
        """Calculate the position of the tag and return the text between this tag and the
        previous tag.
        """
        x_start = previous.end.column
        y_start = previous.end.line

        text = ""
        if locations[0] != locations[1]:
            text = source[locations[0] : locations[1]]

        for idx in range(locations[0], locations[1]):
            if source[idx] == "\n":
                x_start = 0
                y_start += 1
            else:
                x_start += 1

        start = Point(y_start, x_start)

        x_end, y_end = x_start, y_start
        for char in tag:
            if char == "\n":
                x_end = 0
                y_end += 1
            else:
                x_end += 1
        end = Point(y_end, x_end)

        return Position(start, end), text
