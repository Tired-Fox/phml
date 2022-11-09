from pathlib import Path
import re
from nodes import *

from html.parser import HTMLParser


class PEHLParser(HTMLParser):
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
        
        # TODO Custom element for python tags
        
        self.cur.children.append(Element(tag=tag, properties=properties, parent=self.cur))
        self.cur = self.cur.children[-1]

    def handle_startendtag(self, tag, attrs):
        properties: Properties = {}
        for attr in attrs:
            if attr[1] is not None:
                properties[attr[0]] = attr[1]
            else:
                properties[attr[0]] = "yes"
        
        self.cur.children.append(Element(tag=tag, properties=properties, parent=self.cur, openclose=True))

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


def parse(path: str | Path):
    """Parse a given pehl file to AST following hast and unist."""

    parser = PEHLParser()
    if Path(path).suffix == ".pehl":
        with open(Path(path), "r", encoding="utf-8") as source:
            src = source.read()
    
    parser.feed(src)
    
    # print(parser.cur.tree())
    # print(parser.cur)
    
    with open("output.pehl", "+w", encoding="utf-8") as out_file:
        out_file.write(parser.cur.pehl))
