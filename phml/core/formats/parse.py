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
    PI
)

REGEX = {
    "tag": re.compile(
        r"<!--(.*)-->|<(!|\?|\/)?([a-zA-Z0-9\.\-_]*)((\s*[^ \"'><=\/]+(=\"[^\"]+\"|='[^']+'|=[^\s>]+)?)*)\s*(\/|\?)?\s*>"
    ),
    "attributes": re.compile(r"\s*([^<>\"'\= ]+)((=)\"([^\"]*)\"|(=)'([^']*)'|(=)([^<>\= ]+))?"),
    "whitespace": re.compile(r"\s+")
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


def parse_hypertest_markup(data: str, class_name: str) -> AST:
    """Parse a string as a hypertest markup document."""

    phml_parser = HypertextMarkupParser()

    if isinstance(data, str):
        return phml_parser.parse(data)
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


# class HypertextMarkupParser(HTMLParser):
#     """Custom html parser inherited from the python
#     built-in html.parser.
#     """

#     cur: Root | Element
#     """The current parent element in the recursion."""

#     cur_tags: list
#     """Stack of all open tags. Used for balancing tags."""

#     def __init__(self, *, convert_charrefs=True):
#         super().__init__(convert_charrefs=convert_charrefs)

#         self.cur = Root()
#         self.cur_tags = []

#     def handle_decl(self, decl: str) -> None:
#         tokens = decl.split(" ")
#         if tokens[0].lower() == "doctype":
#             self.cur.children.append(
#                 DocType(
#                     lang=tokens[1] if len(tokens) > 1 else "html",
#                     parent=self.cur,
#                     position=Position(self.getpos(), self.getpos()),
#                 )
#             )

#     def handle_starttag(self, tag, attrs):
#         properties: Properties = {}

#         # Build properties/attributes
#         for attr in attrs:
#             if attr[1] is not None:
#                 properties[attr[0]] = attr[1] if attr[1] != "no" else False
#             else:
#                 properties[attr[0]] = True

#         # Add new element to current elements children
#         self.cur.children.append(Element(tag=tag, properties=properties, parent=self.cur))

#         # Self closing tags are marked as such
#         if tag in self_closing_tags:
#             self.cur.children[-1].startend = True

#             self.cur.children[-1].position = Position(
#                 self.getpos(), calc_end_of_tag(self.get_starttag_text(), self.getpos())
#             )
#         else:
#             # New element is now the current node
#             self.cur = self.cur.children[-1]
#             # Elements tag is added to tag stack for balancing
#             self.cur_tags.append(self.cur)
#             # Elements start position is added
#             self.cur.position = Position(self.getpos(), (0, 0))

#     def handle_startendtag(self, tag, attrs):
#         properties: Properties = {}

#         # Build properties/attributes for element
#         for attr in attrs:
#             if attr[1] is not None:
#                 properties[attr[0]] = attr[1] if attr[1] != "no" else False
#             else:
#                 properties[attr[0]] = True

#         # Add new element to current elements children
#         self.cur.children.append(
#             Element(
#                 tag=tag,
#                 properties=properties,
#                 parent=self.cur,
#                 startend=True,
#                 position=Position(
#                     self.getpos(), calc_end_of_tag(self.get_starttag_text(), self.getpos())
#                 ),
#             )
#         )

#     def handle_endtag(self, tag):
#         # Tag was closed validate the balancing and matches
#         if tag == self.cur_tags[-1].tag:
#             # Tags are balanced so add end point to position
#             #  and make the parent the new current element
#             self.cur.position.end = Point(*self.getpos())
#             self.cur = self.cur.parent
#             self.cur_tags.pop(-1)
#         else:
#             # Tags are not balanced, raise a new error
#             raise Exception(
#                 f"Mismatched tags <{self.cur.tag}> and </{tag}> at \
# [{self.getpos()[0]}:{self.getpos()[1]}]"
#             )

#     def handle_data(self, data):
#         # Raw data, most likely text nodes
#         # Strip extra blank lines and count the lines and columns
#         data, eline, ecol = strip(data, self.getpos(), self.cur_tags)

#         # If the data is not empty after stripping blank lines add a new text
#         #  node to current elements children
#         if data not in [[], "", None]:
#             self.cur.children.append(
#                 Text(data, self.cur, position=Position(self.getpos(), (eline, ecol)))
#             )

#     def handle_comment(self, data: str) -> None:
#         # Strip extra blank lines and count the lines and columns
#         data, eline, ecol = strip(data, self.getpos(), self.cur_tags)

#         # If end line is the same as current line then add 7 to
#         # column num for `<!--` and `-->` syntax
#         if eline == self.getpos()[0]:
#             ecol += 7
#         else:
#             # Otherwise just add 3 for the `-->` syntax
#             ecol += 3

#         self.cur.children.append(
#             Comment(
#                 value=data,
#                 parent=self.cur,
#                 position=Position(self.getpos(), (eline, ecol)),
#             )
#         )

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

    def parse(self, source: str) -> AST:
        """Takes a string of the source markup and returns the resulting
        PHML AST.
        """

        element = REGEX["tag"].search(source)
        previous = Position((0, 0), (0, 0))

        tag_stack = []

        root = Root()
        current = root

        while element is not None:
            comment, tag_type, tag_name, tag_attributes, _, _, closing = element.groups()
            # Create position in file
            position, text = self.__calculate(source, element, previous)
            if text.strip() != "":
                current.append(Text(strip(text, tag_stack), position=Position(previous.end, position.start)))
            # Generate Element for tag found
            if comment is None:
                (
                    _type,
                    name,
                    attrs,
                    closing
                ) = self.__parse_tag(
                    tag_type,
                    tag_name,
                    tag_attributes,
                    closing,
                    pos=position)
            else:
                current.append(
                    Comment(
                        strip(comment, tag_stack) if comment is not None else "",
                        position=position
                    )
                )
                # Progress file
                source = source[element.start() + len(element.group(0)):]
                # Find next node
                element = REGEX["tag"].search(source)
                previous = position
                continue

            if _type == Specifier.Close:
                if tag_stack[-1] != name:
                    raise Exception(f"Unbalanced tags {tag_stack[-1]!r} and {name!r} at {position}")
                _ = tag_stack.pop()
                current = current.parent
            elif _type in [Specifier.Open, Specifier.Decleration, Specifier.ProcProfile]:
                current.append(self.__create_node(_type, name, attrs, closing, position))
                if _type == Specifier.Open and closing != Specifier.Close:
                    tag_stack.append(name)
                    current = current.children[-1]

            # Progress file
            source = source[element.start() + len(element.group(0)):]
            # Find next node
            element = REGEX["tag"].search(source)
            previous = position

        return AST(root)

    def __parse_tag(
        self,
        tag_type: str | None = None,
        name: str | None = None,
        tag_attrs: str | None = None,
        closing: str | None = None,
        pos: tuple[int, int] | None = None
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
                [
                    item for item in [attribute[3],attribute[5], attribute[7]]
                    if item != ""
                ]
            ]
            attribute[1] = attribute[1][0] if len(attribute[1]) > 0 else ""
            if attribute[1] in ["true", "false", "yes", "no", ""]:
                value = attribute[1] in ["true", "yes", ""]
            else:
                value = attribute[1]
            attrs[attribute[0]] = value

        closing = Specifier.of(closing)

        if (
            tag_type == Specifier.ProcProfile
            and (
                closing != Specifier.ProcProfile
                or tag_name == ""
            )
        ):
            position = f" [$]{pos}[$]" if pos is not None else ""
            attrs = ' ' + tag_attrs if tag_attrs is not None else ''
            name = tag_name if tag_name != '' else "[@Fred]NAME[@F]"
            close = "?" if closing == Specifier.ProcProfile else "[@Fred]?[@F]"
            raise Exception(TED.parse(
                f"Invalid Processor Profile{position}: *<?{name}[@F]{attrs}{close}>"
            ))

        if tag_type == Specifier.Decleration and tag_name == "":
            position = (
                f" \\[[@Fcyan]{pos[0]}[@F]:[@Fcyan]{pos[1]}[@F]\\]"
                if pos is not None else ""
            )
            attrs = ' ' + tag_attrs if tag_attrs is not None else ''
            name = tag_name if tag_name != '' else "[@Fred]NAME[@F]"
            raise Exception(TED.parse(
                f"Invalid Decleration {position}: *<!{tag_name}{attrs}>"
            ))

        if closing == Specifier.Open and tag_name in self_closing_tags:
            closing = Specifier.of("/")

        return tag_type, tag_name, attrs, closing

    def __create_node(
        self,
        tag_type: str,
        name: str,
        attrs: str,
        closing: str,
        position: Position | None
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
        self,
        file: str, 
        tag: re.Match, 
        previous: Position
    ) -> tuple[Position, str]:
        """Calculate the position of the tag and return the text between this tag and the
        previous tag.
        """
        x_start = previous.end.column
        y_start = previous.end.line

        text = file[:tag.start()]

        for idx in range(0, tag.start()):
            if file[idx] == "\n":
                x_start = 0
                y_start += 1
            else:
                x_start += 1

        start = Point(y_start, x_start)

        x_end, y_end = x_start, y_start
        for char in tag.group(0):
            if char == "\n":
                x_end = 0
                y_end += 1
            else:
                x_end += 1
        end = Point(y_end, x_end)
        return Position(start, end), text
