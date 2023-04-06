from phml.utilities.travel import *
from util_data import container, first, para, text, middle, last

def test_path():
    assert (first_path := path(first)) != []
    assert [node.tag for node in first_path] == ["html", "body", "div"]

def test_path_names():
    assert path_names(first) == ["html", "body", "div"]

def test_walk():
    walked = list(walk(container))
    assert len(walked) == 6
    assert walked == [container, first, para, text, middle, last]

def test_visit_all_after():
    assert len(all_after := list(visit_all_after(first))) == 4
    assert all_after == [para, text, middle, last]
