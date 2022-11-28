"""Pythonic Hypertext Markup Language (phml) parser."""

from html.parser import HTMLParser
from typing import Optional

from phml.nodes import Element, Root, DocType, Properties, Text, Comment, Position, Point

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


def build_point(pos: tuple[int, int], offset: Optional[int] = None) -> Point:
    """Build a phml.node.Point from a tuple."""
    return Point(pos[0], pos[1], offset)


def build_position(
    start: tuple[int, int, Optional[int]],
    end: tuple[int, int, Optional[int]],
    indent: Optional[int] = None,
) -> Position:
    """Build a phml.node.Posiiton from two tuples."""
    return Position(build_point(*start), build_point(*end), indent)


def calc_end_of_tag(tag_text: str, cur_pos: tuple[int, int]) -> tuple[int, int]:
    """Given the current position and the open tag text, this function
    calculates where the start tag ends.
    """
    lines = tag_text.split("\n")
    line = len(lines) - 1
    col = len(lines[-1]) + cur_pos[1] if len(lines) == 1 else len(lines[-1])

    return cur_pos[0] + line, col


def strip_and_count(data: str, cur_pos: tuple[int, int]) -> tuple[str, int, int]:
    """This function takes a possibly mutliline string and strips leading and trailing
    blank lines. Given the current position it will also calculate the line and column
    taht the data ends at.
    """
    lines, cols = 0, len(data) + cur_pos[1]
    data_lines = data.split("\n")

    # If multiline data block
    if len(data_lines) > 1:

        # remove leading blank lines
        for idx in range(len(data_lines)):
            if data_lines[idx].strip() != "":
                data_lines = data_lines[idx:]
                break
            if idx == len(data_lines) - 1:
                data_lines = []
                break

        # Remove trailing blank lines
        if len(data_lines) > 0:
            for idx in range(len(data_lines) - 1, 0, -1):
                if data_lines[idx].replace("\n", " ").strip() != "":
                    data_lines = data_lines[: idx + 1]
                    break

        if len(data_lines) > 0:
            # Get the line and col of the final position
            lines, cols = len(data_lines) - 1, len(data_lines[-1])

        data_lines = "\n".join(data_lines)

    # Else it is a single line data block
    else:
        # Is not a blank line
        if data_lines[0].replace("\n", " ").strip() != "":
            data_lines = data_lines[0]
        else:
            data_lines = ""

    return data_lines, cur_pos[0] + lines, cols


class HypertextMarkupParser(HTMLParser):
    """Custom html parser inherited from the python
    built-in html.parser.
    """

    cur: Root | Element
    """The current parent element in the recursion."""
    
    cur_tags: list
    """Stack of all open tags. Used for balancing tags."""

    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)

        self.cur = Root()
        self.cur_tags = []

    def handle_decl(self, decl: str) -> None:
        if decl.split(" ")[0].lower() == "doctype":
            tokens = decl.split(" ")
            if self.cur.type == "root":
                if len(tokens) > 1:
                    self.cur.children.append(
                        DocType(
                            lang=tokens[1],
                            parent=self.cur,
                            position=build_point(self.getpos(), self.getpos()),
                        )
                    )
                else:
                    self.cur.children.append(
                        DocType(
                            lang=None,
                            parent=self.cur,
                            position=build_point(self.getpos(), self.getpos()),
                        )
                    )
            else:
                raise Exception("<!doctype> must be in the root!")

    def handle_pi(self, data: str) -> None:
        print("Encountered a processing instruction tag:", data)

    def handle_starttag(self, tag, attrs):

        properties: Properties = {}

        for attr in attrs:
            if attr[1] is not None:
                properties[attr[0]] = attr[1] if attr[1] != "no" else False
            else:
                properties[attr[0]] = True

        self.cur.children.append(Element(tag=tag, properties=properties, parent=self.cur))

        if tag in self_closing_tags:
            self.cur.children[-1].startend = True

            self.cur.children[-1].position = build_position(
                self.getpos(), calc_end_of_tag(self.get_starttag_text(), self.getpos())
            )
        else:
            self.cur = self.cur.children[-1]
            self.cur_tags.append(self.cur)
            self.cur.position = build_position(self.getpos(), (0, 0))

    def handle_startendtag(self, tag, attrs):
        properties: Properties = {}

        for attr in attrs:
            if attr[1] is not None:
                properties[attr[0]] = attr[1] if attr[1] != "no" else False
            else:
                properties[attr[0]] = True

        self.cur.children.append(
            Element(
                tag=tag,
                properties=properties,
                parent=self.cur,
                startend=True,
                position=build_position(
                    self.getpos(), calc_end_of_tag(self.get_starttag_text(), self.getpos())
                ),
            )
        )

    def handle_endtag(self, tag):
        if tag == self.cur_tags[-1].tag:
            if len(self.cur.children) == 0:
                self.cur.startend = True

            self.cur.position.end = build_point(self.getpos())
            self.cur = self.cur.parent
            self.cur_tags.pop(-1)
        else:
            raise Exception(
                f"Mismatched tags <{self.cur.tag}> and </{tag}> at [{self.getpos()[0]}:{self.getpos()[1]}]"
            )

    def handle_data(self, data):

        data, eline, ecol = strip_and_count(data, self.getpos())

        if data not in [[], "", None]:
            self.cur.children.append(
                Text(
                    data,
                    self.cur,
                    position=build_position(self.getpos(), (eline, ecol)),
                )
            )

    def handle_comment(self, data: str) -> None:
        data, eline, ecol = strip_and_count(data, self.getpos())

        if eline == self.getpos()[0]:
            ecol += 7
        else:
            ecol += 3

        self.cur.children.append(
            Comment(
                value=data,
                parent=self.cur,
                position=build_position(
                    self.getpos(),
                    (eline, ecol),
                ),
            )
        )
