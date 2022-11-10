"""Pythonic Hypertext Markup Language (phml) parser."""

import re
from pathlib import Path
from html.parser import HTMLParser
from typing import Optional

from .nodes import Element, Root, DocType, Properties, Text, Comment
from .file_types import HTML, PHML, JSON


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
            self.cur.children.append(DocType())
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
        self.cur = self.cur.children[-1]

    def handle_startendtag(self, tag, attrs):
        properties: Properties = {}
        for attr in attrs:
            if attr[1] is not None:
                properties[attr[0]] = attr[1]
            else:
                properties[attr[0]] = "yes"

        self.cur.children.append(
            Element(
                tag=tag, 
                properties=properties, 
                parent=self.cur,
                openclose=True,
            )
        )

    def handle_endtag(self, tag):
        if tag == self.cur.tag:
            self.cur = self.cur.parent
        else:
            raise Exception(f"Mismatched tag: <{self.cur.tag}> and </{tag}>")

    def handle_data(self, data):
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
            data = "\n".join(data)
        else:
            data = data[0].strip()

        if data not in [[], "", None]:
            self.cur.children.append(Text(data))

    def handle_comment(self, data: str) -> None:
        self.cur.children.append(Comment(data))

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

    ast: Root
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
        with open(Path(path), "r", encoding="utf-8") as source:
            src = source.read()

        self.phml_parser.feed(src)

        self.ast = self.phml_parser.cur

        return self

    def write(self, path: str, file_type: str = PHML, ast: Optional[Root] = None):
        """Write a phml ast to a file.

        Defaults to writing the parsed ast on this object to a file.
        Alternatively takes an ast param to write to a file.

        Can convert to json, phml, or html.
        """

        with open(path, "+w", encoding="utf-8") as out_file:
            out_file.write(self.stringify(file_type, ast))

        return self

    def stringify(self, file_type: str = PHML, ast: Optional[Root] = None) -> str:
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
            return ast.html()
        elif file_type == JSON:
            return ast.json()
        else:
            return ast.phml()