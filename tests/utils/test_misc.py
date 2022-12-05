from pytest import raises

from phml.utils.misc import *
from phml.builder import p
from phml.nodes import AST


class TestClasses:
    """Test the phml.utils.misc.classes module."""

    # classnames
    def test_classnames(self):
        underline = False
        color = True

        result = classnames("red", {"underline": underline}, [{"green": color}, "bold"])

        assert result == "red green bold"

        div = p("div", {"class": "bold"})
        underline, color = True, False

        classnames(div, ["red", "bold", {"underline": underline, "orange": color}])
        assert div.properties["class"] == "bold red underline"

    # classList
    def test_ClassList(self):
        node = p("div", {"class": "bold"})
        cl = ClassList(node)

        assert "red" not in node.properties["class"] and not cl.contains("red")
        cl.add("red", "underline")
        assert (
            "red" in node.properties["class"]
            and "underline" in node.properties["class"]
            and cl.contains("red")
            and cl.contains("underline")
        )

        cl.toggle("red", "underline")
        assert (
            "red" not in node.properties["class"]
            and "underline" not in node.properties["class"]
            and not cl.contains("red")
            and not cl.contains("underline")
        )
        cl.toggle("red", "underline")
        assert (
            "red" in node.properties["class"]
            and cl.contains("red")
            and "underline" in node.properties["class"]
            and cl.contains("underline")
        )

        cl.replace("underline", "shadow")
        assert "shadow" in node.properties["class"] and cl.contains("shadow")

        cl.remove("red", "shadow")
        assert (
            "red" not in node.properties["class"]
            and "shadow" not in node.properties["class"]
            and not cl.contains("red")
            and not cl.contains("shadow")
        )


class TestComponent:
    """Test the phml.utils.misc.component module."""

    def test_tag_from_file(self):
        from pathlib import Path

        file = Path("tests/utils/test_misc.py")
        assert tag_from_file(file) == "test-misc"
        assert tag_from_file("test-misc") == "test-misc"
        assert tag_from_file("TestMisCATime") == "test-mis-ca-time"

    def test_filename_from_path(self):
        from pathlib import Path

        assert filename_from_path(Path("tests/utils/test_misc.py")) == "test_misc"

    def test_parse_ast(self):
        bast = AST(
            p(
                p("head", p("meta")),
                p("body", p("h1", "Hello World")),
            )
        )

        cast = AST(p(p("python", "underline = True"), p("div", p("h1", "Hello World!"))))

        with raises(Exception):
            parse_component(bast)

        with raises(Exception, match="Must have at least one element in a component."):
            parse_component(AST(p(p("python", "color = False"))))

        assert parse_component(cast) == {
            "python": [p("python", "underline = True")],
            "script": [],
            "style": [],
            "component": p("div", p("h1", "Hello World!")),
        }


class TestHeading:
    """Test the phml.utils.misc.heading module."""

    heading_1 = p("h1", "Hello World")
    heading_2 = p("h2", "Hello World")
    not_heading = p("div", "Hello World")
    non_element = p("Hello World!")

    assert heading_rank(heading_1) == 1
    assert heading_rank(heading_2) == 2

    with raises(TypeError, match=r"(Node must be a heading\. Was a [a-zA-Z_.]+)"):
        heading_rank(not_heading)
    with raises(TypeError, match=r"(Node must be an element\. Was a [a-zA-Z_.]+)"):
        heading_rank(non_element)
