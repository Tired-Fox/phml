from phml.builder import p
from phml.nodes import *


def test_builder_types():
    # Root node
    assert p() == Root() and p(None) == Root()

    # Element node - self closing
    assert p("div") == Element("div", startend=True)

    # Element node with properties - self closing
    assert p("div", {"id": "test"}) == Element("div", {"id": "test"}, startend=True)

    # Text node
    assert p("text", "Text") == Text("Text")
    assert p("Some Text") == Text("Some Text")

    # Comment node
    assert p("<!--Comment-->") == Comment("Comment")

    # Doctype
    assert p("doctype", "xhtml") == DocType("xhtml")
    assert p("doctype") == DocType()


def test_builder_nesting():
    root_text = Root(children=[Text("Test")])
    root_text_builder = p(None, "Test")

    # Root node with text child
    assert root_text_builder == root_text

    # Children automatically get their children assigned
    assert root_text_builder.children[0].parent is not None

    root_element = Root(children=[Element("meta", startend=True)])
    # Root node with selector as both none and not none
    assert p(p("meta")) == root_element and p(None, p("meta")) == root_element

    element_child = Element("div", children=[Text("Test")])
    # Element node with children - not self closing
    assert p("div", "Test") == element_child
