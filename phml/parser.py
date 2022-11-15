"""Pythonic Hypertext Markup Language (phml) parser."""

import re
from pathlib import Path
from html.parser import HTMLParser
from typing import Optional

from phml.AST import AST
from phml.nodes import Element, Root, DocType, Properties, Text, Comment, Position, Point
from phml.file_types import HTML, PHML, JSON

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
            
            self.cur.children[-1].openclose = True
            cur_pos = self.getpos()
            
            tag_text = self.get_starttag_text().split("\n")

            line = len(tag_text) - 1
            col = len(tag_text[-1]) + cur_pos[1] if len(tag_text) == 1 else len(tag_text[-1])
            
            self.cur.children[-1].position = Position(Point(cur_pos[0], cur_pos[1]), Point(cur_pos[0]+line, col))
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
                openclose=True,
                position=Position(start_pos, end_pos),
            )
        )

    def handle_endtag(self, tag):
        if tag == self.cur.tag:
            line, col = self.getpos()
            end_pos = Point(line, col)

            if len(self.cur.children) == 0:
                self.cur.openclose = True

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
                        lambda d: re.search(r"[^ \t\n]", d) is not None,
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

    def parse(self, path: str | Path):
        """Parse a given phml file to AST following hast and unist.

        When finished the PHML.ast variable will be populated with the
        resulting ast.

        Args:
            path (str | Path): The path to the file that should be parsed.
        """
        self.phml_parser.reset()
        self.phml_parser.cur = Root()
        

        with open(path, "r", encoding="utf-8") as source:
            src = source.read()

        self.phml_parser.feed(src)

        self.ast = AST(self.phml_parser.cur)

        return self

    def write(self, path: str, file_type: str = HTML, ast: Optional[Root] = None):
        """Write a phml ast to a file.

        Defaults to writing the parsed ast on this object to a file.
        Alternatively takes an ast param to write to a file.

        Can convert to json, phml, or html.
        """

        with open(path, "+w", encoding="utf-8") as out_file:
            out_file.write(self.stringify(file_type, ast))

        return self

    def stringify(self, file_type: str = HTML, ast: Optional[AST] = None) -> str:
        """Convert a phml ast to a string.

        Defaults to writing the parsed ast on this object to a file.
        Alternatively takes an ast param to write to a file.

        Can convert to json, phml, or html.
        """
        if ast is None:
            if self.ast is not None:
                ast = self.ast
            else:
                raise Exception(
                    "User must provide an ast. Either run PHML.parse() first or pass a phml ast."
                )

        if file_type == HTML:
            return ast.render()
        elif file_type == JSON:
            return ast.json()
        else:
            return ast.source()
