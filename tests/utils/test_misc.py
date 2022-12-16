from pytest import raises

from phml.utilities.misc import *
from phml.builder import p
from phml.core.nodes import AST


def test_depth():
    node = p(p("div", p("h1", "Hello World!")))
    assert depth(node.children[0].children[0]) == 1


class TestClasses:
    """Test the phml.utilities.misc.classes module."""

    # classnames
    def test_classnames(self):
        underline = False
        color = True

        result = classnames("red", {"underline": underline}, [{"green": color}, "bold"])

        assert result == "red green bold"

        div = p("div", {"class": "bold"})
        underline, color = True, False

        classnames(div, ["red", "bold", 3, {"underline": underline, "orange": color}])
        assert div["class"] == "bold red 3 underline"

        with raises(TypeError, match="Unkown conditional statement: .+"):
            classnames(3.4)

        with raises(TypeError, match="Node must be an element"):
            classnames(p(), "red")

        del div["class"]
        classnames(div, ["red"])
        assert "red" in div["class"]

    # classList
    def test_ClassList(self):
        node = p("div", {"class": "bold"})
        cl = ClassList(node)

        assert "red" not in node["class"] and not cl.contains("red")
        cl.add("red", "underline")
        assert (
            "red" in node["class"]
            and "underline" in node["class"]
            and cl.contains("red")
            and cl.contains("underline")
        )

        cl.toggle("red", "underline")
        assert (
            "red" not in node["class"]
            and "underline" not in node["class"]
            and not cl.contains("red")
            and not cl.contains("underline")
        )
        cl.toggle("red", "underline")
        assert (
            "red" in node["class"]
            and cl.contains("red")
            and "underline" in node["class"]
            and cl.contains("underline")
        )

        cl.replace("underline", "shadow")
        assert "shadow" in node["class"] and cl.contains("shadow")

        cl.remove("red", "shadow")
        assert (
            "red" not in node["class"]
            and "shadow" not in node["class"]
            and not cl.contains("red")
            and not cl.contains("shadow")
        )
        cl = ClassList(p("div", {"class": "bold"}))
        cl.remove("bold")
        assert "class" not in cl.node.properties


class TestComponent:
    """Test the phml.utilities.misc.component module."""

    def test_tag_from_file(self):
        from pathlib import Path

        file = Path("tests/utils/test_misc.py")
        assert tag_from_file(file) == "test-misc"
        assert tag_from_file("test-misc") == "test-misc"
        assert tag_from_file("TestMisCATime") == "test-mis-ca-time"

        with raises(TypeError, match="If filename is a path it must also be a valid file\\."):
            tag_from_file(Path("invalid/file.phml"))

    def test_filename_from_path(self):
        from pathlib import Path

        assert filename_from_path(Path("tests/utils/test_misc.py")) == "test_misc"

    def test_cmpt_name_from_path(self):
        from pathlib import Path
        
        assert cmpt_name_from_path(Path("dir")) == "dir"

    def test_parse_ast(self):
        bast = AST(
            p(
                p("head", p("meta")),
                p("body", p("h1", "Hello World")),
            )
        )

        with raises(Exception):
            parse_component(bast)

        with raises(Exception, match="Must have at least one element in a component."):
            parse_component(AST(p(p("python", "color = False"))))

        cast = AST(
            p(
                p("python", "underline = True"),
                p(
                    "div",
                    p("h1", "Hello World!"),
                ),
                p("script"),
                p("style"),
            )
        )
        assert parse_component(cast) == {
            "python": [p("python", "underline = True")],
            "script": [p("script")],
            "style": [p("style")],
            "component": p("div", p("h1", "Hello World!")),
        }


class TestHeading:
    """Test the phml.utilities.misc.heading module."""

    heading_1 = p("h1", "Hello World")
    heading_2 = p("h2", "Hello World")
    not_heading = p("div", "Hello World")
    non_element = p("Hello World!")

    assert heading_rank(heading_1) == 1
    assert heading_rank(heading_2) == 2

    with raises(TypeError, match=r"(Node must be a heading\. Was a [a-zA-Z_.]+)"):
        heading_rank(not_heading)
    with raises(TypeError, match=r"Node must be an element."):
        heading_rank(non_element)
