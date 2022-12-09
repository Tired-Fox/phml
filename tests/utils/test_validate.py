from pytest import raises

from phml.validate import *
from phml.nodes import Element, Position, Point
from phml.builder import p

# test


class Child_No_Type:
    children: list

    def __init__(self, children: list) -> None:
        self.children = children


class Child_Wrong_Type:
    children: list
    type: str = "test"

    def __init__(self, children: list) -> None:
        self.children = children


def test_check():
    assert not check(p(), "root", None, p())
    assert not check(p("div"), "div", 2, p(p("div")))
    assert not check(p("div"), "root")
    assert not check(p("div"), {"id": "test"})
    assert not check(p("div", {"id": "good"}), {"id": "test"})
    assert not check(p("div", {"id": "good"}), {"tag": "math"})

    assert not check(p("div", {"id": "good"}), [{"tag": "div"}, "math"])
    assert check(p("div", {"id": "good"}), [{"tag": "div"}, "math"], strict=False)

    assert not check(p(), lambda x, i, p: False)
    with raises(Exception, match="Invalid test condition"):
        check(p(), 3)


class TestValidate:
    """Test the phml.utils.validate.validate module."""

    # validate
    def test_validate(self):
        # children
        sample = Child_No_Type([])
        with raises(AssertionError, match="Node should have a type"):
            validate(sample)

        sample = Child_Wrong_Type([])
        with raises(
            AssertionError,
            match="Node should have a type of 'root' or 'element' to contain the 'children' attribute",
        ):
            validate(sample)

        sample = Element("div", children=["The", 3])
        with raises(AssertionError, match="Children must be a node type"):
            validate(sample)

        assert validate(Element("div", children=[p("h1", "Hello World!")]))
        # properties
        prop = p("text", "The end")
        prop.properties = {"id": "test"}

        with raises(AssertionError, match="Node must be of type 'element' to contain 'properties'"):
            validate(prop)

        prop = Element("div", {"id": ["Some", "List"]})
        with raises(AssertionError, match="Node 'properties' must be of type 'int' or 'str'"):
            validate(prop)

        prop = Element("div", {"id": "3"})
        assert validate(prop)

        # Value
        prop = p("text", "3")
        prop.value = 3
        with raises(AssertionError, match="Node 'value' must be of type 'str'"):
            validate(prop)

        assert validate(p("text", "valide value"))

    # parent
    def test_parent(self):
        # Needs to be subclass of parent node
        with raises(
            AssertionError,
            match="Node must inherit from 'Parent'. 'Root' and 'Element' are most common.",
        ):
            parent(p("text", "Invalid"))

        # Needs to have children
        with raises(AssertionError, match="Parent nodes should have the 'children' attribute"):
            el = p("div")
            el.children = None
            parent(el)

        # If element parent then needs to have properties
        with raises(
            AssertionError, match="Parent element node shoudl have the 'properties' element."
        ):
            el = p("div")
            el.properties = None
            parent(el)

    # literal
    def test_literal(self):
        # Needs to be subclass of parent node
        with raises(
            AssertionError,
            match="Node must inherit from 'Literal'. 'Text' and 'Comment' are most common.",
        ):
            literal(p("div"))

        # Needs to have children
        with raises(AssertionError, match="Literal nodes 'value' type should be 'str'"):
            el = p("text", "3")
            el.value = 3
            literal(el)

    # generated
    def test_generated(self):
        assert generated(p("div"))
        assert not generated(Element("div", position=Position(Point(0, 1), Point(2, 3))))

    # has_property
    def test_has_property(self):
        element = p("div", {"id": "test", "class": "underline bold"})
        non_element = p("text", "Invalid")

        assert has_property(element, "id")
        assert not has_property(element, "checked")

        with raises(TypeError, match="Node must be an element."):
            has_property(non_element, "class")

    # is_heading
    def test_is_heading(self):
        heading = p("h1", "Heading 1")
        element = p("div")
        text = p("text", "Invalid")

        assert is_heading(heading)
        assert not is_heading(element)

        with raises(TypeError, match="Node must be an element."):
            has_property(text, "class")

    # is_css_link
    def test_is_css_link(self):
        # Invalid
        assert not is_css_link(p("text", "test"))
        assert not is_css_link(p("div"))
        assert not is_css_link(p("link"))
        assert not is_css_link(p("link", {"rel": "test"}))
        assert not is_css_link(p("link", {"rel": "stylesheet", "type": "test"}))

        # Valid
        assert is_css_link(p("link", {"rel": "stylesheet", "type": "text/css"}))
        assert is_css_link(p("link", {"rel": "stylesheet", "type": ""}))
        assert is_css_link(p("link", {"rel": "stylesheet"}))

    # is_css_style
    def test_is_css_style(self):
        # Invalid
        assert not is_css_style(p("text", "test"))
        assert not is_css_style(p("div"))
        assert not is_css_style(p("style", {"type": "test"}))

        # Valid
        assert is_css_style(p("style"))
        assert is_css_style(p("style", {"type": ""}))
        assert is_css_style(p("style", {"type": "text/css"}))

    # is_javascript
    def test_is_javascript(self):
        # Invalid
        assert not is_javascript(p("text", "test"))
        assert not is_javascript(p("div"))
        assert not is_javascript(p("script", {"type": "text/css"}))
        assert not is_javascript(p("script", {"type": "text/javascript", "language": "javascript"}))
        assert not is_javascript(p("script", {"language": "css"}))

        # Valid
        assert is_javascript(p("script", {"language": "javascript"}))
        assert is_javascript(p("script", {"language": "ecmascript"}))
        assert is_javascript(p("script", {"type": "text/javascript"}))
        assert is_javascript(p("script", {"type": "text/ecmascript"}))
        assert is_javascript(p("script"))

    # is_element
    def test_is_element(self):
        assert not is_element(p("text", "test"), "div")
        assert not is_element(p("div"), "h1")
        assert not is_element(p("div"), "span", "h1")
        assert not is_element(p("div", "span", ["body", "main"]))

        assert is_element(p("div"), "div")
        assert is_element(p("div"), "span", ["div", "h1"])

    def test_is_embedded(self):
        for ntype in [
            "audio",
            "canvas",
            "embed",
            "iframe",
            "img",
            "math",
            "object",
            "picture",
            "svg",
            "video",
        ]:
            assert is_embedded(p(ntype))

    def test_is_interactive(self):
        assert is_interactive(p("a", {"href": "https://example.com"}))
        assert not is_interactive(p("a"))

        assert is_interactive(p("input", {"type": "checkbox"}))
        assert not is_interactive(p("input", {"type": "hidden"}))
        assert not is_interactive(p("input"))

        assert is_interactive(p("img", {"usemap": True}))
        assert not is_interactive(p("img"))

        assert is_interactive(p("video", {"controls": True}))
        assert not is_interactive(p("video"))

        assert not is_interactive(p("div"))

        for ntype in ["button", "details", "embed", "iframe", "label", "select", "textarea"]:
            assert is_interactive(p(ntype))

    def test_is_phrasing(self):
        assert is_phrasing(p("text", "test"))

        nmap = p("map", p("area"))
        assert is_phrasing(nmap.children[0])
        assert not is_phrasing(p("area"))
        assert not is_phrasing(p("div", p("area")).children[0])

        assert is_phrasing(p("meta", {"itemprop": True}))
        assert not is_phrasing(p("meta"))

        assert not is_phrasing(p("div"))
        assert is_phrasing(
            p(
                "link",
                {
                    "rel": "dns-prefetch modulepreload pingback preconnect prefetch preload prerender stylesheet",
                },
            )
        )
        assert is_phrasing(
            p(
                "link",
                {
                    "itemprop": True,
                },
            )
        )
        assert is_phrasing(
            p(
                "link",
                {"itemprop": True, "rel": "invalid"},
            )
        )
        assert not is_phrasing(
            p(
                "link",
                {"rel": "dns-prefetch modulepreload invalid"},
            )
        )

        for ntype in [
            "node",
            "map",
            "mark",
            "math",
            "audio",
            "b",
            "bdi",
            "bdo",
            "br",
            "button",
            "canvas",
            "cite",
            "code",
            "data",
            "datalist",
            "del",
            "dfn",
            "em",
            "embed",
            "i",
            "iframe",
            "img",
            "input",
            "ins",
            "kbd",
            "label",
            "a",
            "abbr",
            "meter",
            "noscript",
            "object",
            "output",
            "picture",
            "progress",
            "q",
            "ruby",
            "s",
            "samp",
            "script",
            "select",
            "slot",
            "small",
            "span",
            "strong",
            "sub",
            "sup",
            "svg",
            "template",
            "textarea",
            "time",
            "u",
            "var",
            "video",
            "wbr",
        ]:
            assert is_phrasing(p(ntype))

    # is_event_handler
    def test_is_event_handler(self):
        assert not is_event_handler("one")
        assert not is_event_handler("once")
        assert not is_event_handler("Something")

        assert is_event_handler("onclick")
        assert is_event_handler("onafterprint")
