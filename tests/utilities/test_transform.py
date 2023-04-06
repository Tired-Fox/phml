from phml.utilities.transform import *
from phml import p
from phml.nodes import Element, Node, AST, Literal

from util_data import *


def new_tree() -> Element:
    return p(
        "div",
        {"id": "container"},
        p("div", {"class": "sample", "id": "sample-1"}),
        p("p", {"hidden": True}, "test text"),
        p("div", {"class": "sample", "id": "sample-2"}),
        p("div", {"class": "sample", "id": "sample-3"}),
    )

def new_unsanatized() -> AST:
    return p(
        new_tree(),
        p("img", {"src": "@:/image/sample.png", "data-alt": "invalid", "data-src": "@:/invalid"}),
        p("script"),
        p("tr"),
        p("Component")
    )



class TestExtract:
    def test_to_string(self):
        assert to_string(ast) == "test hello world! test text"
        assert to_string(p("text", "test")) == "test"
        assert to_string(None) == ""



class TestTransform:
    def test_filter_nodes(self):
        tree = new_tree()
        filter_nodes(tree, "div")
        assert len(tree.children) == 3
        assert all(isinstance(node, Element) and node.tag == "div" for node in tree)

        tree = new_tree()
        filter_nodes(tree, lambda n, *_: Literal.is_text(n))
        assert all(Literal.is_text(node) for node in tree)



    def test_remove_nodes(self):
        tree = new_tree()
        remove_nodes(tree, "div")
        assert len(tree.children) == 1
        assert isinstance(tree.children[0], Element) and tree.children[0].tag == "p"

    def test_map_nodes(self):
        tree = new_tree()

        def div_to_span(node: Node) -> Node:
            if isinstance(node, Element) and node.tag == "div":
                node.tag = "span"
                return node
            return node

        map_nodes(tree, div_to_span)
        assert len(tree.children) == 4
        assert [child.tag for child in tree] == ["span", "p", "span", "span"]

    def test_find_and_replace(self):
        tree = new_tree()
        find_and_replace(tree, ("text", "TEXT"))
        assert tree.children[1].children[0].content == "test TEXT"

    def test_shift_heading(self):
        header = p("h1", "TITLE")
        shift_heading(header, 3)
        assert header.tag == "h4"
        shift_heading(header, -2)
        assert header.tag == "h2"

        shift_heading(header, -10)
        assert header.tag == "h1"
        shift_heading(header, 10)
        assert header.tag == "h6"

    def test_replace_node(self):
        tree = new_tree()
        replace_node(tree, "div", Element("span"))

        assert len(tree.children) == 4
        assert tree.children[0].tag == "span"
        replace_node(tree, "div", Element("span"), True)
        assert [child.tag for child in tree] == ["span", "p", "span", "span"]

        replace_node(tree, "span", None, True)
        assert len(tree.children) == 1
        replace_node(tree, "p", [Element("p"), Element("p")])
        assert len(tree.children) == 2 
        assert tree.children == [Element("p"), Element("p")]

    def test_modify_children(self):
        @modify_children
        def p_to_span(child: Node, *_):
            """Converts the `p` tags in the children to `span` tags."""
            if isinstance(child, Element) and child.tag == "p":
                child.tag = "span"
            return child

        tree = new_tree()
        p_to_span(tree)
        assert tree.children[1].tag == "span"


class TestSanatize:
    def test_strict(self):
        ast = new_unsanatized()
        ast.append(Element("input", {"type": "text"}))

        sanatize(ast)

        assert len(ast[0][0].attributes) == 1
        assert len(ast[0][2].attributes) == 1
        assert len(ast[0][3].attributes) == 1
        assert ast[-1]["type"] == "checkbox"
        assert len(ast[-2].attributes) == 0
        assert len(ast) == 3

    def test_custom(self):
        ast = new_unsanatized()
        ast.append(Element("Script"))

        allow_id_class = Schema().extend(
            attributes={
                "img": [("data-src", "@:/sample")],
                "*": [
                    "id",
                    "class",
                ],
            },
            protocols={"data-src": ["http"]},
            strip=["Script"],
            tag_names=["Script"]
        )

        sanatize(ast, allow_id_class)

        assert len(ast[0][0].attributes) == 2
        assert len(ast[0][2].attributes) == 2
        assert len(ast[0][3].attributes) == 2
