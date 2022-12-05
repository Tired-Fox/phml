from phml.utils.transform import *
from phml.builder import p
from phml.utils import inspect


class TestExtract:
    """Test the phml.utils.transform.extract module"""

    def test_to_string(self):
        div = p("div", "hello person", p("h1", "how was your day"), p("br"), p(None, "newline?"))
        assert to_string(div) == "hello person how was your day newline?"


class TestTransform:
    """Test the phml.utils.transform.transform module"""

    # filter_nodes
    def test_filter_nodes(self):
        tree = p(
            "body", p("div", p("div", "Hello"), p("text", ",")), p("container", p("div", "World!"))
        )
        filter_nodes(tree, {"tag": "div"})

        assert tree == p("body", p("div", p("div")), p("div"))

    # remove_nodes
    def test_remove_nodes(self):
        tree = p(
            "body", p("div", p("div", "Hello"), p("text", ",")), p("container", p("div", "World!"))
        )
        remove_nodes(tree, {"tag": "div"})

        assert tree == p("body", p("container"))

    # map_nodes
    def test_map_nodes(self):
        tree = p(
            "body",
            p(
                "div",
                p("div", "Hello"),
                p("text", ","),
            ),
            p("container", p("div", "World!")),
        )

        def div_to_span(node):
            if node.type == "element" and node.tag == "div":
                return p("span", node.properties, *node.children)
            else:
                return node

        map_nodes(tree, div_to_span)

        assert tree == p(
            "body",
            p(
                "span",
                p("span", "Hello"),
                p("text", ","),
            ),
            p("container", p("span", "World!")),
        )

    # find_and_replace
    def test_find_and_replace(self):
        ast = p(
            "body",
            p(
                "span",
                p("span", "Hello"),
                p("text", ","),
            ),
            p("container", p("span", "World!")),
        )

        find_and_replace(ast, ("World!", "Everyone!"))
        assert ast == p(
            "body",
            p(
                "span",
                p("span", "Hello"),
                p("text", ","),
            ),
            p("container", p("span", "Everyone!")),
        )

    # shift_heading
    def test_shift_heading(self):
        heading = p("h1", "Hello World!")

        shift_heading(heading, 2)
        assert heading.tag == "h3"

        shift_heading(heading, 10)
        assert heading.tag == "h6"

        shift_heading(heading, -10)
        assert heading.tag == "h1"

    # replace_node
    def test_replace_node(self):
        root = p("body", 
            p("container", p("div", "hello world")),
            p("div")
        )
        replace_node(root, {"tag": "div"}, p("span", "Replacement"))

        assert root == p("body",
            p("container", p("span", "Replacement")),
            p("span", "Replacement")
        )
