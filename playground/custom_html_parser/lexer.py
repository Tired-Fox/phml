# Capture the brackets and determine the element

# Captures open and closing tags retaining caps and empty named tags
from dataclasses import dataclass
import re
from teddecor import TED
from phml.core.nodes import *
from phml import inspect

REGEX = {
    "tag": re.compile(r"<(?!!--)(\!|\?|\/|)?([^>< ?\/\"'\s\-]*)\s*([^\/?<>]*)\s*(\/|\?|\-\-)?\s*(?<!\-\-)>|<!--(.*)-->"),
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

class TagMarkupParser:
    """Parse languages like XML, HTML, PHML, etc; into a PHML AST."""

    def parse(self, source: str) -> AST:
        """Main run function that takes a string of the source markup and returns the resulting
        PHML AST.
        """

        element = REGEX["tag"].search(source)
        previous = Position((0, 0), (0, 0))

        tag_stack = []

        root = Root()
        current = root

        while element is not None:
            # Create position in file
            position, text = self.__calculate(source, element, previous)
            if text.strip() != "":
                current.append(Text(text, position=Position(previous.end, position.start)))
            # Generate Element for tag found
            if element.group(5) is None:
                tag_type, name, attrs, closing = self.__parse_tag(*element.groups()[:4], pos=position)
            else:
                current.append(Comment(element.group(5) or "", position=position))

            if tag_type == Specifier.Close:
                if tag_stack[-1] != name:
                    raise Exception(f"Unbalanced tags {tag_stack!r} and {name!r}")
                _ = tag_stack.pop()
                current = current.parent
            elif tag_type in [Specifier.Open, Specifier.Decleration, Specifier.ProcProfile]:
                current.append(self.__create_node(tag_type, name, attrs, closing, position))
                if tag_type == Specifier.Open and closing != Specifier.Close:
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
        attrs = {}

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

        if tag_type == Specifier.ProcProfile and (closing != Specifier.ProcProfile or tag_name == ""):
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

if __name__ == "__main__":
    file = """\
    <!DOCTYPE html>
    <?proc ?>
    <html lang="en">
        <!-- Comment -->
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>

        <body>
            <>
                <Header />
                <PHML>
                    Some Data <
                </PHML>
                <div 
                    @if="True"
                    :id='id'
                >
                    Example
                </div>
                <input type=text />
            </>
        </body>

    </html>\
    """

    parser = TagMarkupParser()