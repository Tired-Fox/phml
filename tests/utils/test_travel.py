from phml.utils.travel import *
from phml.builder import p


def test_path():
    path_tree = p("div", p("div", p("span", p("strong", "Test"))))
    target = path_tree.children[0].children[0].children[0]
    target_path = path(target)

    assert target_path == [path_tree, path_tree.children[0], path_tree.children[0].children[0]]


def test_walk():
    tree = p("div", p("h1", "The", p("div")))
    tree = list(walk(tree))

    assert tree == [
        p("div", p("h1", "The", p("div"))),
        p("h1", "The", p("div")),
        p("text", "The"),
        p("div"),
    ]


def test_visit_children():
    tree = p("h1", "The", p("div"))
    tree = list(visit_children(tree))
    assert tree == [p("text", "The"), p("div")]


def test_visit_all_after():
    tree = p("h1", "The", p("div", "Book"))
    tree = list(visit_all_after(tree.children[0]))
    assert tree == [p("div", "Book"), p("text", "Book")]
