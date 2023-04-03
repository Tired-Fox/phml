from phml.utilities.locate.find import *
from phml.utilities.locate.index import Index
from phml.utilities.locate.select import matches, query, query_all
from phml.builder import p
from phml.nodes import AST

from pytest import raises

first = p("div", {"class": "sample", "id": "sample-1"})
last = p("div", {"class": "sample", "id": "sample-3"})
container = p("div",
    {"id": "container"},
    first,
    p("p", {"hidden": True}, "test text"),
    p("div", {"class": "sample", "id": "sample-2"}),
    last 
)

ast: AST = p(
    p("html",
        p("head",
            p("title", "test")
        ),
        p("body",
            p("h1", "hello world!"),
            container
        )
    )
)

def test_ancestor():
    assert ancestor(first, last) == container

def test_find():
    assert find(ast, ["div", {"id": "sample-1"}]) is not None 
    assert find(ast, "span") is None

def test_find_all():
    assert find_all(ast, ["div", {"class": "sample"}]) != []
    assert find_all(ast, "span") == []

def test_find_after():
    assert find_after(first, ["div", {"id": "sample-2"}]) is not None
    assert find_after(first, "span") is None
    assert find_after(first) is not None

def test_find_all_after():
    assert find_all_after(first, ["div", {"class": "sample"}]) != []
    assert find_all_after(first, "span") == []
    assert find_all_after(p("div", {}), "div") == []
    assert find_all_after(first) != []

def test_find_before():
    assert find_before(last, ["div", {"id": "sample-2"}]) is not None
    assert find_before(last, "span") is None
    assert find_before(last) is not None

def test_find_all_before():
    assert find_all_before(last, ["div", {"class": "sample"}]) != []
    assert find_all_before(last, "span") == []
    assert find_all_before(p("div", {}), "div") == []
    assert find_all_before(last) != []

def test_find_all_between():
    assert len(find_all_between(container, (0, None), "div")) == 3
    assert len(find_all_between(container, (0, 2), "div")) == 1
    assert find_all_between(container, (0, None)) != []

def test_index_attribute():
    indexed = Index(ast, "id")
    keys = ["sample-1", "sample-2", "sample-3", "container", ""]
    assert all(key in keys for key in list(indexed.keys()))
    assert all(len(indexed[key]) for key in keys[:-1]) and len(indexed[""]) == 6

def test_index_with_condition():
    indexed = Index(ast, "id", "div")
    assert len(indexed.keys()) >= 2

def text_index_get():
    indexed = Index(ast, "id")
    assert indexed.get("sample-2") is not None
    assert indexed.get("invalid") is None
    assert indexed.get("invalid", []) == []

def test_index_callable():
    indexed = Index(ast, Index.key_by_tag)
    keys = ["div", "p", "html", "body", "h1", "title", "head"]
    assert all(key in keys for key in indexed)

def test_index_add_remove():
    indexed = Index(ast, Index.key_by_tag)
    new_node = p("div", {})
    indexed.add(new_node)
    assert new_node in indexed["div"]
    indexed.remove(new_node)
    assert new_node not in indexed["div"]
    indexed.remove(indexed["p"][-1])
    assert "p" not in indexed

def test_select_query():
    assert query(ast, "div") == container
    assert query(ast, "div#sample-1.sample") == first
    assert query(ast, "div > p") == container[1]
    assert query(ast, "div > div + p") == container[1]
    assert query(ast, "div > div ~ #sample-3") == last
    assert query(ast, "div div") == first
    assert query(ast, "div > div ~ *") is not None
    assert query(ast, "div > [class=sample]") == first
    assert query(ast, "div > [id^=sample]") == first
    assert query(ast, "div > [id$=ple-1]") == first
    assert query(ast, "div > [id~=sample]") == first
    assert query(ast, "div > [id*=sample]") == first
    assert query(ast, "div > [id|=sample]") == first
    assert query(ast, "span") is None

    # Fail
    with raises(Exception, match="There may only be one id per element specifier."):
        query(ast, "div#sample#element")

    assert query(p("div", p("div", {})), "div ~ div") is None
    assert query(p("div", p("div", {})), "div + div") is None

def test_select_query_all():
    assert query_all(ast, "div") != []
    assert len(query_all(ast, "div.sample")) == 3
    assert query_all(ast, "div#container") == [container]
    assert query_all(ast, "div > div + p ~") != []
    assert query_all(ast, "div > *") != []
    assert query_all(ast, "div *") != []

    # Fail
    assert query_all(p("div", p("div", {})), "div ~ div") == []
    
    assert query_all(p("div", p("div", {})), "div + div") == []

def test_select_matches():
    assert matches(p("div", {}), "div")
    assert matches(p("div", {"id": "sample"}), "div#sample")
    assert matches(p("div", {"class": "sample red"}), "div.sample.red")
    assert matches(p("div", {"hidden": True}), "div[hidden]")
    div = p("div", {"data-test": "some-value"}) 
    assert matches(div, "div[data-test=some-value]")
    assert matches(div, "div[data-test^=some]")
    assert matches(div, "[data-test|=some]")
    assert matches(div, "[data-test~=me-va]")
    assert matches(div, "[data-test$=value]")
    with raises(Exception, match="Complex specifier detected and is not allowed.\n.+"):
        matches(div, "div > div")
    with raises(Exception, match="Specifier must only include tag name, classes, id, and or attribute specfiers.\nExample: `.+`"):
        matches(div, "*")

