from phml.nodes import AST, Element
from phml.builder import p

from phml.utils.locate import *

ast: AST = AST(
    p(
        p("doctype"),
        p(
            "html",
            {"lang": "en"},
            p("div", {"id": "test"}, p("h1", "Hello World!")),
            p("div", {"id": "test-1"}),
            p("div", {"id": "test-2"}),
        ),
    )
)
el: Element = p(
    "html",
    {"lang": "en"},
    p("div", {"id": "test"}, p("h1", "Hello World!")),
    p("div", {"id": "test-1"}),
    p("div", {"id": "test-2"}),
)

query_ast: Element = p(
    "html",
    {"lang": "en"},
    p(
        "div",
        {"id": "test", "class": "shadow red", "title": "Testing queries"},
        p("h1", "Hello World!"),
    ),
    p(
        "div",
        {"id": "test-1"},
        p("div", p("h1", p("span", "Hello World"), p("input", {"id": "in", "type": "checkbox"}))),
    ),
    p("div", {"id": "test-2"}),
)


def matching_lists(list1, list2):
    return len(list1) == len(list2) and all([i1 == i2 for i1, i2 in zip(list1, list2)])


class TestFind:
    """Test the phml.utils.locate.find module."""

    # "find",
    def test_find(self):
        assert find(ast, {"tag": "h1"}) is not None
        assert find(el, {"tag": "div", "id": "test"}) is not None

    def test_ancestor(self):
        # From an ast/root
        assert ancestor(find(ast, {"tag": "h1"})) == find(ast, {"tag": "div", "id": "test"})
        assert ancestor(
            find(ast, {"tag": "h1"}), find(ast, {"tag": "div", "id": "test-1"})
        ) == find(ast, {"tag": "html"})

        assert ancestor(
            find(ast, {"tag": "h1"}),
            find(ast, {"tag": "div", "id": "test-1"}),
            find(el, {"tag": "div", "id": "test"}),
        ) == find(ast, {"tag": "html"})

        # From an element
        assert ancestor(find(el, {"tag": "h1"})) == find(el, {"tag": "div", "id": "test"})
        assert ancestor(find(el, {"tag": "h1"}), find(el, {"tag": "div", "id": "test-1"})) == find(
            el, {"tag": "html"}
        )

        assert ancestor(
            find(el, {"tag": "h1"}),
            find(el, {"tag": "div", "id": "test-1"}),
            find(el, {"tag": "div", "id": "test"}),
        ) == find(el, {"tag": "html"})

    def test_find_all(self):
        assert len(find_all(ast, {"tag": "div"})) == 3
        assert matching_lists(
            find_all(ast, {"tag": "div"}),
            [find(ast, {"id": "test"}), find(ast, {"id": "test-1"}), find(ast, {"id": "test-2"})],
        )

        assert len(find_all(el, {"tag": "div"})) == 3
        assert matching_lists(
            find_all(el, {"tag": "div"}),
            [find(el, {"id": "test"}), find(el, {"id": "test-1"}), find(el, {"id": "test-2"})],
        )

    def test_find_after(self):
        assert find_after(find(ast, {"id": "test"}), {"id": "test-1"}) == find(
            ast, {"id": "test-1"}
        )
        assert find_after(find(ast, {"id": "test"})) == find(ast, {"id": "test-1"})

    def test_find_all_after(self):
        start = find(ast, {"id": "test"})

        assert matching_lists(
            find_all_after(start, {"tag": "div"}),
            [find(ast, {"id": "test-1"}), find(ast, {"id": "test-2"})],
        )

        assert matching_lists(
            find_all_after(start, {"id": "test-1"}),
            [find(ast, {"id": "test-1"})],
        )

        start = find(ast, {"id": "test"})
        assert matching_lists(
            find_all_after(start),
            [find(el, {"id": "test-1"}), find(el, {"id": "test-2"})],
        )

        assert matching_lists(find_all_after(start, {"id": "test-1"}), [find(el, {"id": "test-1"})])

    def test_find_before(self):
        start = find(ast, {"id": "test-2"})
        assert find_before(start, {"id": "test"}) == find(ast, {"id": "test"})

        start = find(ast, {"id": "test-2"})
        assert find_before(start) == find(ast, {"id": "test-1"})

    def test_find_all_before(self):
        start = find(ast, {"id": "test-2"})

        assert matching_lists(
            find_all_before(start),
            [find(el, {"id": "test"}), find(el, {"id": "test-1"})],
        )

    def test_find_all_between(self):
        parent = find(ast, {"tag": "html"})

        assert matching_lists(
            find_all_between(parent, start=0, end=len(parent.children), condition={"tag": "div"}),
            [find(ast, {"id": "test"}), find(ast, {"id": "test-1"}), find(ast, {"id": "test-2"})],
        )

        assert matching_lists(
            find_all_between(parent, start=0, end=len(parent.children), condition={"id": "fail"}),
            [],
        )

        parent = find(el, {"tag": "html"})

        assert matching_lists(
            find_all_between(parent, start=0, end=len(parent.children), condition={"tag": "div"}),
            [find(el, {"id": "test"}), find(el, {"id": "test-1"}), find(el, {"id": "test-2"})],
        )

        assert matching_lists(
            find_all_between(parent, start=0, end=len(parent.children), condition={"id": "fail"}),
            [],
        )


class TestSelect:
    """Test the phml.utils.locate.select module."""

    # matches
    def test_matches(self):
        assert matches(
            find(query_ast, {"id": "test"}), "div#test.shadow.red[title='Testing queries']"
        )
        assert matches(find(query_ast, {"id": "test"}), "div#test[title^=Testing]")
        assert matches(find(query_ast, {"id": "test"}), "#test.shadow[title$=queries]")
        assert matches(find(query_ast, {"id": "test"}), "div#test.red[title*='sting que']")
        assert matches(find(query_ast, {"id": "test-1"}), "#test-1[id|=test]")

    def test_query(self):
        assert query(query_ast, "div#test > h1") == find(query_ast, {"tag": "h1"})
        assert query(query_ast, "div#test h1") == find(query_ast, {"tag": "h1"})
        assert query(query_ast, "div#test *") == find(query_ast, {"tag": "h1"})
        assert query(query_ast, "div#test > *") == find(query_ast, {"tag": "h1"})
        assert query(query_ast, "div#test + div#test-1") == find(query_ast, {"id": "test-1"})
        assert query(query_ast, "div#test ~ div#test-2") == find(query_ast, {"id": "test-2"})
        assert query(query_ast, "div#test-1 > * h1 > span + input#in[type=checkbox]") == find(
            query_ast, {"tag": "input"}
        )

    def test_query_all(self):
        assert matching_lists(query_all(query_ast, "div"), find_all(query_ast, {"tag": "div"}))

        assert matching_lists(
            query_all(query_ast, "div[id|=test]"),
            find_all(
                query_ast,
                lambda n, i, _: n.type == "element"
                and "id" in n.properties
                and (n.properties["id"] == "test" or n.properties["id"].startswith("test-")),
            ),
        )

        assert matching_lists(
            query_all(query_ast, "div > h1"),
            find_all(
                query_ast,
                lambda n, i, pnt: n.type == "element"
                and n.tag == "h1"
                and pnt.type == "element"
                and pnt.tag == "div",
            ),
        )


class TestIndex:
    """Test the phml.utils.locate.index.Index class."""

    def test_index_constructor(self):
        iast = AST(
            p(
                p("doctype", "html"),
                p(
                    "html",
                    p("head"),
                    p(
                        "body",
                        p("div", {"id": "test-1"}, "test 1"),
                        p("div", {"id": "test-2"}, "test 2"),
                        p("div", {"id": "test-3"}, "test 3"),
                    ),
                ),
            )
        )

        # Basic indexing
        indexed_ast = Index("id", iast, {"tag": "div"})
        assert indexed_ast.indexed_tree == {
            "test-1": [p("div", {"id": "test-1"}, "test 1")],
            "test-2": [p("div", {"id": "test-2"}, "test 2")],
            "test-3": [p("div", {"id": "test-3"}, "test 3")],
        }

        # Validate extended dict functions
        assert list(indexed_ast.keys()) == ["test-1", "test-2", "test-3"]
        assert list(indexed_ast.values()) == [
            [p("div", {"id": "test-1"}, "test 1")],
            [p("div", {"id": "test-2"}, "test 2")],
            [p("div", {"id": "test-3"}, "test 3")],
        ]

        assert list(indexed_ast.items()) == [
            ("test-1", [p("div", {"id": "test-1"}, "test 1")]),
            ("test-2", [p("div", {"id": "test-2"}, "test 2")]),
            ("test-3", [p("div", {"id": "test-3"}, "test 3")]),
        ]

        assert "test-1" in indexed_ast

        # Validate with Callable key
        indexed_ast = Index(Index.key_by_tag, iast)
        assert indexed_ast.indexed_tree == {
            "html": [
                p(
                    "html",
                    p("head"),
                    p(
                        "body",
                        p("div", {"id": "test-1"}, "test 1"),
                        p("div", {"id": "test-2"}, "test 2"),
                        p("div", {"id": "test-3"}, "test 3"),
                    ),
                ),
            ],
            "head": [p("head")],
            "body": [
                p(
                    "body",
                    p("div", {"id": "test-1"}, "test 1"),
                    p("div", {"id": "test-2"}, "test 2"),
                    p("div", {"id": "test-3"}, "test 3"),
                ),
            ],
            "div": [
                p("div", {"id": "test-1"}, "test 1"),
                p("div", {"id": "test-2"}, "test 2"),
                p("div", {"id": "test-3"}, "test 3"),
            ],
        }

    def test_index_get(self):
        iast = AST(
            p(
                p("doctype", "html"),
                p(
                    "html",
                    p("head"),
                    p(
                        "body",
                        p("div", {"id": "test-1"}, "test 1"),
                        p("div", {"id": "test-2"}, "test 2"),
                        p("div", {"id": "test-3"}, "test 3"),
                    ),
                ),
            )
        )

        indexed_ast = Index(Index.key_by_tag, iast)

        assert indexed_ast.get("head") == [p("head")]
        assert indexed_ast.get("div") == [
            p("div", {"id": "test-1"}, "test 1"),
            p("div", {"id": "test-2"}, "test 2"),
            p("div", {"id": "test-3"}, "test 3"),
        ]

    def test_index_add(self):
        iast = AST(
            p(
                p("doctype", "html"),
                p(
                    "html",
                    p("head"),
                    p(
                        "body",
                        p("div", {"id": "test-1"}, "test 1"),
                        p("div", {"id": "test-2"}, "test 2"),
                        p("div", {"id": "test-3"}, "test 3"),
                    ),
                ),
            )
        )

        indexed_ast = Index(Index.key_by_tag, iast)
        indexed_ast.add(p("head", p("meta")))

        assert indexed_ast.get("head") == [p("head"), p("head", p("meta"))]

    def test_index_remove(self):
        iast = AST(
            p(
                p("doctype", "html"),
                p(
                    "html",
                    p("head", p("meta")),
                    p(
                        "body",
                        p("div", {"id": "test-1"}, "test 1"),
                        p("div", {"id": "test-2"}, "test 2"),
                        p("div", {"id": "test-3"}, "test 3"),
                    ),
                ),
            )
        )

        indexed_ast = Index(Index.key_by_tag, iast)
        indexed_ast.remove(p("div", {"id": "test-3"}, "test 3"))

        assert indexed_ast.get("div") == [
            p("div", {"id": "test-1"}, "test 1"),
            p("div", {"id": "test-2"}, "test 2"),
        ]

        assert "meta" in indexed_ast
        indexed_ast.remove(p("meta"))
        assert "meta" not in indexed_ast
