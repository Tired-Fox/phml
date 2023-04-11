from util_data import container, dest, last, middle, para, text

from phml.utilities.travel import *


def test_path():
    assert (first_path := path(dest)) != []
    assert [node.tag for node in first_path] == ["html", "body", "div"]

def test_path_names():
    assert path_names(dest) == ["html", "body", "div"]

def test_walk():
    walked = list(walk(container))
    assert len(walked) == 6
    assert walked == [container, dest, para, text, middle, last]

def test_visit_all_after():
    assert len(all_after := list(visit_all_after(dest))) == 4
    assert all_after == [para, text, middle, last]
