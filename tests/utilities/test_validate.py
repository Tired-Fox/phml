from pytest import raises
from phml.utilities.validate import *
from phml import p
from phml.nodes import Element, Literal, LiteralType, Parent, Position
from util_data import *


class TestCheck:
    def test_tag(self):
        assert check(p("div"), "div")

    def test_attributes(self):
        node = p("div", {"id": "sample", "data-src": "invalid"})
        assert check(node, {"id": "sample"})
        assert check(node, {"data-src": True})

    def test_recursive(self):
        node = p("div", {"id": "sample", "data-src": "invalid"})
        assert check(node, ["div", [{"id": "sample"}, {"data-src": "invalid"}]])

    def test_callable(self):
        node = p("text", "Some test")
        assert check(node, Literal.is_text)

    def test_non_strict(self):
        assert check(
            p("div", {"id": "sample"}), ["div", {"id": "Invalid"}], strict=False
        )

    def test_invalid_condition(self):
        with raises(TypeError, match="Invalid test condition.*"):
            check(p("div"), None)


class ChildError:
    parent = None


class TestValidate:
    def test_validate(self):
        assert validate(p("div"))
        assert validate(p("text", "Test"))

        with raises(AssertionError, match="Children must be a node type"):
            validate(Element("div", children=[ChildError()]))
        with raises(
            AssertionError, match="Element 'attributes' must be of type 'bool' or 'str'"
        ):
            validate(p("div", {"id": None}))
        with raises(AssertionError, match="Literal 'content' must be of type 'str'"):
            validate(Literal(LiteralType.Text, None))

    def test_generated(self):
        assert generated(p("div"))
        assert not generated(Element("div", position=Position((0, 0), (0, 0))))

    def test_is_heading(self):
        assert is_heading(p("h1"))
        assert not is_heading(p("div"))

        with raises(TypeError, match="Node must be an element."):
            is_heading(p("text", ""))

    def test_is_css_link(self):
        assert is_css_link(p("link", {"rel": "stylesheet"}))
        assert is_css_link(p("link", {"rel": "stylesheet", "type": "text/css"}))
        assert is_css_link(p("link", {"rel": "stylesheet", "type": ""}))
        assert not is_css_link(
            p("link", {"rel": "stylesheet", "type": "text/javascript"})
        )
        assert not is_css_link(p("link", {"rel": "javascript"}))

    def test_is_css_style(self):
        assert is_css_style(p("style", {"type": ""}))
        assert is_css_style(p("style", {"type": "text/css"}))
        assert is_css_style(p("style"))
        assert not is_css_style(p("style", {"type": "scss"}))
        assert not is_css_style(p("div"))

    def test_is_javascript(self):
        assert is_javascript(p("script"))

        assert is_javascript(p("script", {"type": "text/ecmascript"}))
        assert is_javascript(p("script", {"type": "text/javascript"}))

        assert is_javascript(p("script", {"language": "ecmascript"}))
        assert is_javascript(p("script", {"language": "javascript"}))

        assert not is_javascript(
            p("script", {"language": "ecmascript", "type": "javascript"})
        )

    def test_is_element(self):
        assert is_element(p("div"))
        assert is_element(p("div"), "div")
        assert is_element(p("div"), "script", ["div", "meta"])

        assert not is_element(p("div"), "script", ["meta", "style"])
        assert not is_element(p("text", "data"), "script", ["meta", "style"])

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
        assert is_interactive(p("a", {"href": ""}))
        assert not is_interactive(p("a"))

        assert is_interactive(p("input", {"type": "text"}))
        assert not is_interactive(p("input", {"type": "hidden"}))
        assert not is_interactive(p("input"))

        assert is_interactive(p("img", {"usemap": True}))
        assert not is_interactive(p("img", {"usemap": False}))
        assert not is_interactive(p("img"))

        assert is_interactive(p("video", {"controls": True}))
        assert not is_interactive(p("img"))

        for ntype in [
            "button",
            "details",
            "embed",
            "iframe",
            "label",
            "select",
            "textarea",
        ]:
            assert is_interactive(p(ntype))

        assert not is_interactive(p("NotInteractive"))

    def test_is_phrasing(self):
        assert is_phrasing(p("text", "something"))
        assert is_phrasing(p("map", p("area"))[0])
        assert is_phrasing(p("meta", {"itemprop": True}))
        assert is_phrasing(p("link", {"itemprop": True}))
        assert is_phrasing(
            p(
                "link",
                {
                    "rel": "dns-prefetch modulepreload pingback preconnect prefetch preload prerender stylesheet"
                },
            )
        )
        assert not is_phrasing(p("link", {"rel": "invalid dns-prefetch"}))

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

        assert not is_phrasing(p("NotPhrasing"))

    def test_is_event_handler(self):
        assert is_event_handler("onclick")
        assert not is_event_handler("on")
        assert not is_event_handler("oncl")
        assert not is_event_handler("click")

    def test_blank(self):
        assert blank(None)
        assert blank(tuple())
        assert blank(dict())
        assert blank(set())
        assert blank(list())
        assert blank("")
        assert blank(" \n\t\r")
        
        assert not blank(" Data ")
        assert not blank(tuple(["data"]))
        assert not blank(set(["data"]))
        assert not blank(["data"])
        assert not blank({"not": "blank"})
        
