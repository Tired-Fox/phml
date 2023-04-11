from pytest import raises

from phml import p
from phml.nodes import *


def test_ast():
    assert isinstance(p(), AST)


def test_element():
    assert isinstance(p("div"), Element)
    assert p("div", {"id": "test"}) == Element("div", {"id": "test"})
    assert p("div", {"id": "test"}, "text") == Element(
        "div", {"id": "test"}, [Literal(LiteralType.Text, "text")]
    )
    assert p("doctype") == Element("doctype", {"html": True})
    assert p("div#sample.red.underline") == Element("div", {"id": "sample", "class": "red underline"})

def test_element_fail():
    with raises(TypeError, match="Selector must be of the format `.+`"):
        p(">")

def test_element_list_children():
    assert isinstance(p("div", ["Some text", "<!--Comment-->", p("div")]), Element)
    with raises(TypeError, match="Unkown type <.+> in .+: .+"):
        p("div", ["some text", []])


def test_literal():
    assert isinstance(text := p("text", "Some text here"), Literal) and Literal.is_text(
        text
    )
    assert isinstance(
        comment := p("comment", "Some comment"), Literal
    ) and Literal.is_comment(comment)
    assert isinstance(p("div", "<!--Comment String-->"), Element)

