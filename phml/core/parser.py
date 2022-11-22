"""Pythonic Hypertext Markup Language (phml) parser."""

from re import search
from pathlib import Path
from html.parser import HTMLParser
from typing import Callable, Optional

from phml.nodes import AST, Element, Root, DocType, Properties, Text, Comment, Position, Point

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

class PHMLParser(HTMLParser):
    """Custom html parser inherited from the python
    built-in html.parser.
    """

    cur: Root | Element
    """The current parent element in the recursion."""

    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)

        self.cur = Root()

    def handle_decl(self, decl: str) -> None:
        if self.cur.type == "root":
            cur_point = Point(*self.getpos())
            self.cur.children.append(DocType(self.cur, position=Position(cur_point, cur_point)))
        else:
            raise Exception("<!doctype> must be in the root!")

    def handle_pi(self, data: str) -> None:
        print("Encountered a processing instruction tag:", data)

    def handle_starttag(self, tag, attrs):
        properties: Properties = {}
        for attr in attrs:          
            if attr[1] is not None:
                properties[attr[0]] = attr[1]
            else:
                properties[attr[0]] = "yes"

        self.cur.children.append(Element(tag=tag, properties=properties, parent=self.cur))

        if tag in self_closing_tags:
            # from sys import stderr
            # from teddecor import TED

            # stderr.write(
            #     TED.parse(
            #         f"[@F yellow]*Warning[@F]:* <{tag}> should be self closing: [@F red] all children will be be pushed to parent element\n"
            #     )
            # )
            # stderr.flush()
            self.cur.children[-1].startend = True
            cur_pos = self.getpos()

            tag_text = self.get_starttag_text().split("\n")

            line = len(tag_text) - 1
            col = len(tag_text[-1]) + cur_pos[1] if len(tag_text) == 1 else len(tag_text[-1])

            self.cur.children[-1].position = Position(
                Point(cur_pos[0], cur_pos[1]), Point(cur_pos[0] + line, col)
            )
        else:
            self.cur = self.cur.children[-1]
            cur_pos = self.getpos()
            self.cur.position = Position(Point(cur_pos[0], cur_pos[1]), Point(0, 0))

        # input(f"{tag} | Start | {cur_pos}")

    def handle_startendtag(self, tag, attrs):
        properties: Properties = {}
        for attr in attrs:
            if attr[1] is not None:
                properties[attr[0]] = attr[1]
            else:
                properties[attr[0]] = "yes"

        cur_pos = self.getpos()
        start_pos = Point(cur_pos[0], cur_pos[1])

        tag_text = self.get_starttag_text().split("\n")

        line = len(tag_text) - 1
        col = len(tag_text[-1])

        end_pos = Point(cur_pos[0] + line, col)

        self.cur.children.append(
            Element(
                tag=tag,
                properties=properties,
                parent=self.cur,
                startend=True,
                position=Position(start_pos, end_pos),
            )
        )

    def handle_endtag(self, tag):
        if tag == self.cur.tag:
            line, col = self.getpos()
            end_pos = Point(line, col)

            if len(self.cur.children) == 0:
                self.cur.startend = True

            self.cur.position.end = end_pos
            if line - self.cur.position.start.line > 0:
                self.cur.position.indent = col // 4 if col != 0 else 0

            # input(f"{tag} | end | {end_pos} | {self.cur.position}")

            self.cur = self.cur.parent
        else:
            raise Exception(f"Mismatched tag: <{self.cur.tag}> and </{tag}>")

    def handle_data(self, data):
        lines, cols = 0, len(data) + self.getpos()[1]
        data = data.split("\n")
        if len(data) > 1:
            data = [
                d.replace("\t", "    ")
                for d in list(
                    filter(
                        lambda d: search(r"[^ \t\n]", d) is not None,
                        data,
                    )
                )
            ]
            if len(data) > 0:
                lines, cols = len(data) - 1, len(data[-1])
            data = "\n".join(data)
        else:
            data = data[0]

        if data not in [[], "", None]:
            cur_pos = self.getpos()
            end_point = Point(cur_pos[0] + lines, cols)

            self.cur.children.append(
                Text(
                    data,
                    self.cur,
                    position=Position(Point(*cur_pos), end_point),
                )
            )

    def handle_comment(self, data: str) -> None:
        lines, cols = 0, len(data) + self.getpos()[1]
        data = data.split("\n")
        if len(data) > 1:
            lines = len(data) - 1
            cols = len(data[-1]) + 3
        else:
            cols += 7

        data = "\n".join(data)
        cur_pos = self.getpos()

        self.cur.children.append(
            Comment(
                data,
                self.cur,
                Position(Point(*cur_pos), Point(cur_pos[0] + lines, cols)),
            )
        )


def json_to_ast(json_obj: dict):
    """Convert a json object to a string."""

    def get_node_type(t: str):
        if t == "root":
            return Root()
        elif t == "element":
            return Element()
        elif t == "doctype":
            return DocType()
        elif t == "text":
            return Text()
        elif t == "comment":
            return Comment()
        else:
            return None

    def recurse(obj: dict):
        """Recursivly construct ast from json."""
        if 'type' in obj:
            val = get_node_type(obj['type'])
            if val is not None:
                for key in obj:
                    if key not in ["children", "type", "position"] and hasattr(val, key):
                        setattr(val, key, obj[key])
                if 'children' in obj and hasattr(val, "children"):
                    for child in obj["children"]:
                        new_child = recurse(child)
                        new_child.parent = val
                        val.children.append(new_child)
                if 'position' in obj and hasattr(val, 'position'):
                    # start, end, indent
                    # line, column, offset
                    start = obj["position"]["start"]
                    end = obj["position"]["end"]
                    val.position = Position(
                        Point(start["line"], start["col"], start["offset"]),
                        Point(end["line"], end["col"], end["offset"]),
                        obj["position"]["indent"],
                    )
                return val
            else:
                raise Exception(f"Unkown node type <{obj['type']}>")
        else:
            raise Exception(
                'Invalid json for phml. Every node must have a type. Nodes may only have the types; root, element, doctype, text, or comment'
            )

    return recurse(json_obj)


class Parser:
    """Primary logic to handle everything with a phml file.

    This class can parse files as phml files and create an ast.
    The ast and the nodes themselfs can translate themselves to;
    html, phml, and json. The ast can recursively return itself as
    an html string. However, only this class can process the python
    blocks inside of the phml file.

    Call Parser.convert() and pass any kwargs you wish to be exposed to
    the process that processes the python. You may also use Parser.util to
    pass extensions to convert and manipulate the html along with the python
    processing.
    """

    parser: PHMLParser
    """The custom builtin `html.parser` class that builds phml ast."""

    ast: AST
    """The recursive node tree of the phml ast."""

    def __init__(self):
        self.phml_parser = PHMLParser()
        self.ast = None

    def load(self, path: str | Path, handler: Optional[Callable] = None):
        """Parse a given phml file to AST following hast and unist.

        When finished the PHML.ast variable will be populated with the
        resulting ast.

        Args:
            path (str | Path): The path to the file that should be parsed.
            handler (Callable | None): A function to call instead of the built in
            parser to parse to a phml.AST. Must take a string and return a phml.AST.
        """

        with open(path, "r", encoding="utf-8") as source:
            src = source.read()

        if handler is None:
            path = Path(path)

            if path.suffix == ".json":
                from json import loads

                self.ast = AST(json_to_ast(loads(src)))
            else:
                self.phml_parser.reset()
                self.phml_parser.cur = Root()

                self.phml_parser.feed(src)
                self.ast = AST(self.phml_parser.cur)
        else:
            self.ast = handler(src)

        return self

    def parse(self, data: str | dict, handler: Optional[Callable] = None):
        """Parse data from a phml/html string or from a dict to a phml ast.

        Args:
            data (str | dict): Data to parse in to a ast
            data_type (str): Can be `HTML`, `PHML`, `MARKDOWN`, or `JSON` which
            tells parser how to parse the data. Otherwise it will assume
            str data to be html/phml and dict as `json`.
            handler (Callable | None): A function to call instead of the built in
            parser to parse to a phml.AST. Must take a string and return a phml.AST.
        """
        if handler is None:
            if isinstance(data, dict):
                self.ast = AST(json_to_ast(data))
            elif isinstance(data, str):
                self.phml_parser.reset()
                self.phml_parser.cur = Root()

                self.phml_parser.feed(data)
                self.ast = AST(self.phml_parser.cur)
        else:
            self.ast = handler(data)

        return self
