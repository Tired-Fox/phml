from phml.utilities.locate.find import *
from phml.utilities.locate.index import Index
from phml.utilities.locate.select import matches, query, query_all, parse_specifiers
from phml import p
from util_data import ast, container, dest, last

from pytest import raises

class TestFind:
    def test_ancestor(self):
        assert ancestor(dest, last) == container

    def test_find(self):
        assert find(ast, ["div", {"id": "sample-1"}]) is not None 
        assert find(ast, "span") is None

    def test_find_all(self):
        assert find_all(ast, ["div", {"class": "sample"}]) != []
        assert find_all(ast, "span") == []

    def test_find_after(self):
        assert find_after(dest, ["div", {"id": "sample-2"}]) is not None
        assert find_after(dest, "span") is None
        assert find_after(dest) is not None

    def test_find_all_after(self):
        assert find_all_after(dest, ["div", {"class": "sample"}]) != []
        assert find_all_after(dest, "span") == []
        assert find_all_after(p("div", {}), "div") == []
        assert find_all_after(dest) != []

    def test_find_before(self):
        assert find_before(last, ["div", {"id": "sample-2"}]) is not None
        assert find_before(last, "span") is None
        assert find_before(last) is not None

    def test_find_all_before(self):
        assert find_all_before(last, ["div", {"class": "sample"}]) != []
        assert find_all_before(last, "span") == []
        assert find_all_before(p("div", {}), "div") == []
        assert find_all_before(last) != []

    def test_find_all_between(self):
        assert len(find_all_between(container, (0, None), "div")) == 3
        assert len(find_all_between(container, (0, 2), "div")) == 1
        assert find_all_between(container, (0, None)) != []

class TestIndex:
    def test_index_attribute(self):
        indexed = Index(ast, "id")
        keys = ["sample-1", "sample-2", "sample-3", "container", ""]
        assert all(key in keys for key in list(indexed.keys()))
        assert all(len(indexed[key]) for key in keys[:-1]) and len(indexed[""]) == 6

    def test_index_with_condition(self):
        indexed = Index(ast, "id", "div")
        assert len(indexed.keys()) >= 2

    def text_index_get(self):
        indexed = Index(ast, "id")
        assert indexed.get("sample-2") is not None
        assert indexed.get("invalid") is None
        assert indexed.get("invalid", []) == []

    def test_index_callable(self):
        indexed = Index(ast, Index.key_by_tag)
        keys = ["div", "p", "html", "body", "h1", "title", "head"]
        assert all(key in keys for key in indexed)

    def test_index_add_remove(self):
        indexed = Index(ast, Index.key_by_tag)
        new_node = p("div", {})
        indexed.add(new_node)
        assert new_node in indexed["div"]
        indexed.remove(new_node)
        assert new_node not in indexed["div"]
        indexed.remove(indexed["p"][-1])
        assert "p" not in indexed

class TestSelect:
    def test_query(self):
        assert query(ast, "div") == container
        assert query(ast, "div#sample-1.sample") == dest
        assert query(ast, "div > p") == container[1]
        assert query(ast, "div > div + p") == container[1]
        assert query(ast, "div > div ~ #sample-3") == last
        assert query(ast, "div div") == dest
        assert query(ast, "div > div ~ *") is not None
        assert query(ast, "div > [class=sample]") == dest
        assert query(ast, "div > [id^=sample]") == dest
        assert query(ast, "div > [id$=ple-1]") == dest
        assert query(ast, "div > [id~=sample]") == dest
        assert query(ast, "div > [id*=sample]") == dest
        assert query(ast, "div > [id|=sample]") == dest
        assert query(ast, "span") is None
    
        assert query(p("div", p("div", {})), "div ~ div") is None
        assert query(p("div", p("div", {})), "div + div") is None
    
    def test_selector_exceptions(self):
        with raises(Exception, match="There may only be one id per element specifier\\. '.+'"):
            parse_specifiers("div#sample#element")

    def test_query_all(self):
        assert query_all(ast, "div") != []
        assert len(query_all(ast, "div.sample")) == 3
        assert query_all(ast, "div#container") == [container]
        assert query_all(ast, "div > div + p ~") != []
        assert query_all(ast, "div > *") != []
        assert query_all(ast, "div *") != []
    
        # Fail
        assert query_all(p("div", p("div", {})), "div ~ div") == []
        assert query_all(p("div", p("div", {})), "div + div") == []

    def test_matches(self):
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

    def test_matches_exceptions(self):
        div = p("div", {"data-test": "some-value"}) 

        with raises(Exception, match="Complex specifier detected and is not allowed.\n.+"):
            matches(div, "div > div")
        with raises(Exception, match="Specifier must only include tag name, classes, id, and or attribute specfiers.\nExample: `.+`"):
            matches(div, "*")

