"""Pythonic Hypertext Markup Language (phml) parser."""
from re import match
from html.parser import HTMLParser

from phml.core.nodes import AST, Comment, DocType, Element, Point, Position, Properties, Root, Text

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


def parse_hypertest_markup(data: str, class_name: str) -> AST:
    """Parse a string as a hypertest markup document."""

    phml_parser = HypertextMarkupParser()

    if isinstance(data, str):
        try:
            phml_parser.feed(data)
            if len(phml_parser.cur_tags) > 0:
                last = phml_parser.cur_tags[-1].position
                raise Exception(
                    f"Unbalanced tags in source at [{last.start.line}:{last.start.column}]"
                )
            return AST(phml_parser.cur)
        except Exception as exception:
            raise Exception(
                f"{data[:6] + '...' if len(data) > 6 else data}\
: {exception}"
            ) from exception
    raise Exception(f"Data passed to {class_name}.parse must be a str")


def strip_blank_lines(data_lines: list[str]) -> list[str]:
    """Strip the blank lines at the start and end of a list."""
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
        for idx in range(len(data_lines) - 1, 0, -1):
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


def strip_and_count(data: str, cur_pos: tuple[int, int]) -> tuple[str, int, int]:
    """This function takes a possibly mutliline string and strips leading and trailing
    blank lines. Given the current position it will also calculate the line and column
    taht the data ends at.
    """
    lines, cols = 0, len(data) + cur_pos[1]
    if match(r"[ \n]+", data) is None:
        data_lines = data.split("\n")

        # If multiline data block
        if len(data_lines) > 1:
            data_lines = strip_blank_lines(data_lines)

            if len(data_lines) > 0:
                # Get the line and col of the final position
                lines, cols = len(data_lines) - 1, len(data_lines[-1])

            data_lines = "\n".join(data_lines)
        # Else it is a single line data block
        else:
            # Is not a blank line
            # if match(r" +\n", data_lines[0]) is None:
            data_lines = data_lines[0]

        return data_lines, cur_pos[0] + lines, cols
    return data, cur_pos[0] + len(data.split("\n")), len(data.split("\n")[-1])


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
        tokens = decl.split(" ")
        if tokens[0].lower() == "doctype":
            self.cur.children.append(
                DocType(
                    lang=tokens[1] if len(tokens) > 1 else "html",
                    parent=self.cur,
                    position=Position(self.getpos(), self.getpos()),
                )
            )

    def handle_starttag(self, tag, attrs):

        properties: Properties = {}

        # Build properties/attributes
        for attr in attrs:
            if attr[1] is not None:
                properties[attr[0]] = attr[1] if attr[1] != "no" else False
            else:
                properties[attr[0]] = True

        # Add new element to current elements children
        self.cur.children.append(Element(tag=tag, properties=properties, parent=self.cur))

        # Self closing tags are marked as such
        if tag in self_closing_tags:
            self.cur.children[-1].startend = True

            self.cur.children[-1].position = Position(
                self.getpos(), calc_end_of_tag(self.get_starttag_text(), self.getpos())
            )
        else:
            # New element is now the current node
            self.cur = self.cur.children[-1]
            # Elements tag is added to tag stack for balancing
            self.cur_tags.append(self.cur)
            # Elements start position is added
            self.cur.position = Position(self.getpos(), (0, 0))

    def handle_startendtag(self, tag, attrs):
        properties: Properties = {}

        # Build properties/attributes for element
        for attr in attrs:
            if attr[1] is not None:
                properties[attr[0]] = attr[1] if attr[1] != "no" else False
            else:
                properties[attr[0]] = True

        # Add new element to current elements children
        self.cur.children.append(
            Element(
                tag=tag,
                properties=properties,
                parent=self.cur,
                startend=True,
                position=Position(
                    self.getpos(), calc_end_of_tag(self.get_starttag_text(), self.getpos())
                ),
            )
        )

    def handle_endtag(self, tag):
        # Tag was closed validate the balancing and matches
        if tag == self.cur_tags[-1].tag:
            # Tags are balanced so add end point to position
            #  and make the parent the new current element
            self.cur.position.end = Point(*self.getpos())
            self.cur = self.cur.parent
            self.cur_tags.pop(-1)
        else:
            # Tags are not balanced, raise a new error
            raise Exception(
                f"Mismatched tags <{self.cur.tag}> and </{tag}> at \
[{self.getpos()[0]}:{self.getpos()[1]}]"
            )

    def handle_data(self, data):
        # Raw data, most likely text nodes
        # Strip extra blank lines and count the lines and columns
        data, eline, ecol = strip_and_count(data, self.getpos())

        # If the data is not empty after stripping blank lines add a new text
        #  node to current elements children
        if data not in [[], "", None]:
            self.cur.children.append(
                Text(data, self.cur, position=Position(self.getpos(), (eline, ecol)))
            )

    def handle_comment(self, data: str) -> None:
        # Strip extra blank lines and count the lines and columns
        data, eline, ecol = strip_and_count(data, self.getpos())

        # If end line is the same as current line then add 7 to
        # column num for `<!--` and `-->` syntax
        if eline == self.getpos()[0]:
            ecol += 7
        else:
            # Otherwise just add 3 for the `-->` syntax
            ecol += 3

        self.cur.children.append(
            Comment(
                value=data,
                parent=self.cur,
                position=Position(self.getpos(), (eline, ecol)),
            )
        )
