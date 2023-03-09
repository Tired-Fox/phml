from phml.utilities.transform import *
from phml.core import AST
from phml.builder import p


class TestExtract:
    """Test the phml.utils.transform.extract module"""

    def test_to_string(self):
        div = p("div", "hello person", p("h1", "how was your day"), p("br"), p(None, "newline?"))
        assert to_string(div) == "hello person how was your day newline?"
        assert (
            to_string(
                AST(
                    p(
                        p(
                            "div",
                            "hello person",
                            p("h1", "how was your day"),
                            p("br"),
                            p(None, "newline?"),
                        )
                    )
                )
            )
            == "hello person how was your day newline?"
        )
        assert to_string(p("text", "The Day")) == "The Day"
        assert to_string(p("<!--The Day-->")) == "The Day"
        assert to_string(p("doctype")) is None

class TestTransform:
    """Test the phml.utils.transform.transform module"""

    # filter_nodes
    def test_filter_nodes(self):
        tree = p(
            "body", p("div", p("div", "Hello"), p("text", ",")), p("container", p("div", "World!"))
        )
        filter_nodes(tree, {"tag": "div"})

        assert tree == p("body", p("div", p("div")), p("div"))

        tree = AST(
            p(
                p(
                    "body",
                    p("div", p("div", "Hello"), p("text", ",")),
                    p("container", p("div", "World!")),
                )
            )
        )
        filter_nodes(tree, {"tag": "div"})

        assert tree == AST(p(p("div", p("div")), p("div")))

        tree = AST(
            p(
                p(
                    "body",
                    p("div", p("div", "Hello"), p("text", ",")),
                    p("container", p("div", "World!")),
                )
            )
        )
        filter_nodes(tree, "text")

        assert tree == AST(p(p("text", "Hello"), p("text", ","), p("text", "World!")))

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

        tree = AST(
            p(
                p(
                    "body",
                    p(
                        "div",
                        p("div", "Hello"),
                        p("text", ","),
                    ),
                    p("container", p("div", "World!")),
                )
            )
        )

        map_nodes(tree, div_to_span)

        assert tree == AST(
            p(
                p(
                    "body",
                    p(
                        "span",
                        p("span", "Hello"),
                        p("text", ","),
                    ),
                    p("container", p("span", "World!")),
                )
            )
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
        root = p("body", p("container", p("div", "hello world")), p("div"))
        replace_node(root, {"tag": "div"}, p("span", "Replacement"))

        assert root == p("body", p("container", p("span", "Replacement")), p("div"))

        root = p("body", p("container", p("div", "hello world")), p("div"))
        replace_node(root, {"tag": "div"}, None, all_nodes=True)

        assert root == p("body", p("container"))

    def test_modify_children(self):
        @modify_children
        def div_to_span(node=None, idx=None, parent=None):
            if node.type == "element" and node.tag == "div":
                return p("span", node.properties, *node.children)
            return node

        ast = AST(p(p("div", "Hello World")))
        root = p(p("div", "Hello World"))
        element = p("div", p("div", "Hello World"))

        div_to_span(ast)
        div_to_span(root)
        div_to_span(element)

        assert ast == AST(p(p("span", "Hello World")))
        assert root == p(p("span", "Hello World"))
        assert element == p("div", p("span", "Hello World"))


class TestClean:
    def test_sanatize(self):

        root = AST(p(p("div")))
        sanatize(AST(p(p("div"))))
        assert root == AST(p(p("div")))

        root = p(p("div"), p("container"))
        sanatize(root)
        assert root == p(p("div"))

        root = p(p("div"), p("tr"))
        sanatize(root)
        assert root == p(p("div"))

        root = p(p("div", {"invalid": True}))
        sanatize(root)
        assert root == p(p("div"))

        root = p(p("div", {"itemType": "Dog"}, p("div", {"id": "tag"})))
        sanatize(root)
        assert root == p(p("div", {"itemType": "Dog"}, p("div")))

        root = p(p("input", {"type": "number"}))
        sanatize(root)
        assert root == p(p("input", {"type": "checkbox", "disabled": True}))

        root = p(
            p("a", {"href": "co.mel.exorg"}),
            p("blockquote", {"cite": "www.example.com"}),
            p("img", {"src": "build.apps.code", "longDesc": "build.apps.code"}),
            p("a", {"href": "https://www.example.com"})
        )
        sanatize(root)
        assert root == p(
            p("a"),
            p("blockquote"),
            p("img"),
            p("a", {"href": "https://www.example.com"})
        )
