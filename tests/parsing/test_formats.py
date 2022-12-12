from pathlib import Path
from phml import Formats, Format, AST, parse_component
from phml.core.nodes import Text, Position, Element
from phml.builder import p
from pytest import raises

from data import *


def test_is_format():
    assert Formats.JSON.is_format("json")
    assert Formats.HTML.is_format("htm")

    with raises(Exception, match="Base class Format's parse method should never be called"):
        Format.parse("")

    with raises(Exception, match="Base class Format's compile method should never be called"):
        Format.compile(AST(p()))


def test_formats():
    assert len([0 for _ in Formats()]) > 0


def test_phml_format():
    assert Formats.PHML.parse(strings["phml"]) == asts["phml"]

    with raises(Exception, match=r"Data passed to PHMLFormat.parse must be a str"):
        Formats.PHML.parse(None)
    with raises(Exception, match=r"<!DOCT...: Unbalanced tags in source at .+"):
        Formats.PHML.parse("<!DOCTYPE html><html><body>")

    assert Formats.PHML.compile(AST(p(p("div")))) == "<!DOCTYPE html>\n<div />"


# html
def test_html_format():
    assert Formats.HTML.parse(strings["html"]) == asts["html"]

    with raises(Exception, match=r"Data passed to HTMLFormat.parse must be a str"):
        Formats.HTML.parse(None)
    with raises(Exception, match=r"<!DOCT...: Unbalanced tags in source at .+"):
        Formats.HTML.parse("<!DOCTYPE html><html><body>")

    component = parse_component(AST(p(p("div"), p("python", "message='hello world'"))))
    assert (
        Formats.HTML.compile(
            AST(p(p("message"), p("python", "message='hello world'"))), {"message": component}
        )
        == "<!DOCTYPE html>\n<div />"
    )

    assert Formats.HTML.compile(asts["phml"], title="sample title") == strings["html"]

    assert (
        Formats.HTML.compile(AST(p(p("div", {"@if": "False"}), p("div", {"@elif": "True"}))))
        == "<!DOCTYPE html>\n<div />"
    )

    assert (
        Formats.HTML.compile(AST(p(p("div", {"@if": "False"}), p("div", {"@else": True}))))
        == "<!DOCTYPE html>\n<div />"
    )

    with raises(Exception, match="There can only be one python condition statement at a time:\n.+"):
        Formats.HTML.compile(AST(p(p("div", {"@if": "True", "@else": True}))))

    with raises(
        Exception,
        match="Condition statements that are not py-if or py-for must have py-if or py-elif as a \
prevous sibling.+",
    ):
        Formats.HTML.compile(AST(p(p("div", {"@else": True}))))


test_dict = {
    "type": "element",
    "position": None,
    "properties": {},
    "tag": "title",
    "startend": False,
    "locals": {},
    "children": [{"type": "text", "position": None, "value": "{title or \"\"}", "num_lines": 1}],
}

# json
def test_json_format():
    from json import dumps

    assert Formats.JSON.parse(test_dict) == AST(p(p("title", "{title or \"\"}")))
    assert Formats.JSON.parse(dumps(test_dict)) == AST(p(p("title", "{title or \"\"}")))

    with raises(Exception, match="Data passed to JSONFormat.parse must be either a str or a dict"):
        Formats.JSON.parse(None)

    with raises(Exception, match="Unkown node type .+"):
        Formats.JSON.parse({"type": "invalid"})

    with raises(
        Exception,
        match="Invalid json for phml. Every node must have a type. Nodes may only have the types;\
 root, element, doctype, text, or comment",
    ):
        Formats.JSON.parse({})

    assert Formats.JSON.parse(
        {
            "type": "text",
            "position": {
                "start": {"line": 0, "column": 1, "offset": 2},
                "end": {"line": 0, "column": 1, "offset": 2},
                "indent": 3,
            },
            "value": "test",
        }
    ) == AST(p(Text("test")))

    assert Formats.JSON.parse(dicts) == asts["phml"]

    assert Formats.JSON.compile(asts["phml"]) == dumps(dicts, indent=2)

    with raises(Exception, match="Root nodes must only occur as the root of an ast/tree"):
        assert Formats.JSON.compile(AST(p(p("div", p()))))

    assert (
        (Formats.JSON.compile(AST(p(Element("div", position=Position((0, 1), (2, 3)))))))
        == '''\
{
  "type": "root",
  "position": null,
  "children": [
    {
      "type": "element",
      "position": {
        "start": {
          "line": 0,
          "column": 1,
          "offset": null
        },
        "end": {
          "line": 2,
          "column": 3,
          "offset": null
        },
        "indent": null
      },
      "properties": {},
      "tag": "div",
      "startend": false,
      "locals": {},
      "children": []
    }
  ]
}\
'''
    )


# xml
def test_xml_format():
    assert Formats.XML.parse(strings["xml"]) == asts["xml"]
    assert Formats.XML.parse(Path("tests/sample.xml")) == asts["xml"]

    with raises(
        Exception,
        match="Data passed into XMLFormat.parse must be either str or pathlib.Path",
    ):
        Formats.XML.parse(None)

    start = '''\
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{url}</loc>
    <lastmod>2022-06-04</lastmod>
  </url>
</urlset>
'''

    assert (
        Formats.XML.compile(Formats.XML.parse(start), url="https://www.example.com/foo.html")
        == strings["xml"]
    )
